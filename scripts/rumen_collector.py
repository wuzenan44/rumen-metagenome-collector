#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rumen Metagenome Collector - 自动检索瘤胃宏基因组组装数据集并生成 HTML 报告
用法:
    python rumen_collector.py --host "cattle" --output C:/path/to/output --max-results 200
"""

import argparse
import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import List, Dict, Set


# ─────────────────────────────────────────────
# 配置参数
# ─────────────────────────────────────────────
HOST_SPECIES = {
    "cattle": ["Bos taurus", "cow", "cattle", "bovine"],
    "sheep": ["Ovis aries", "sheep", "ovine"],
    "goat": ["Capra hircus", "goat", "caprine"],
    "yak": ["Bos mutus", "yak"],
    "buffalo": ["Bubalus bubalis", "buffalo"],
    "all": ["rumen", "ruminant"]
}

SEARCH_KEYWORDS = [
    "rumen metagenome",
    "rumen microbiome",
    "rumen metagenomic",
    "rumen microbial community",
    "rumen MAGs",
    "rumen fermentation",
    "rumen microbiota"
]

# ENA API 端点
ENA_SEARCH = "https://www.ebi.ac.uk/ena/portal/api/search"
ENA_BROWSER = "https://www.ebi.ac.uk/ena/browser/api"

# NCBI API 端点
NCBI_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def build_ena_query(host_species: List[str], keywords: List[str]) -> str:
    """构建 ENA 搜索查询"""
    # 构建基础查询词
    host_terms = ' OR '.join([f'"{h}"' for h in host_species])
    keyword_terms = ' OR '.join([f'"{k}"' for k in keywords])

    # 构建完整查询
    query = f'({host_terms}[Title] OR {host_terms}[Description] OR {host_terms}[Scientific Name])'
    query += f' AND ({keyword_terms}[Title] OR {keyword_terms}[Description])'
    query += ' AND "metagenomic"[Library Strategy]'
    query += ' AND ("assembly"[Assembly Level] OR "scaffold"[Assembly Level] OR "contig"[Assembly Level])'

    return query


def ena_search(query: str, max_results: int = 200) -> List[Dict]:
    """在 ENA 中搜索宏基因组数据集"""
    params = {
        "result": "assembly",
        "query": query,
        "fields": "accession,scientific_name,study_title,description,assembly_type,"
                  "assembly_level,coverage,n_contigs,contig_n50,total_length,"
                  "country,collection_date,first_created,study_accession",
        "format": "json",
        "size": max_results
    }

    url = f"{ENA_SEARCH}?{urllib.parse.urlencode(params)}"
    datasets = []

    try:
        print(f"  ENA 查询: {query[:100]}...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())

            if isinstance(data, list):
                for item in data:
                    datasets.append({
                        "accession": item.get("accession", ""),
                        "scientific_name": item.get("scientific_name", ""),
                        "title": item.get("study_title", ""),
                        "description": item.get("description", "")[:300],
                        "assembly_type": item.get("assembly_type", ""),
                        "assembly_level": item.get("assembly_level", ""),
                        "coverage": item.get("coverage", ""),
                        "n_contigs": item.get("n_contigs", ""),
                        "contig_n50": item.get("contig_n50", ""),
                        "total_length": item.get("total_length", ""),
                        "country": item.get("country", ""),
                        "collection_date": item.get("collection_date", ""),
                        "first_created": item.get("first_created", ""),
                        "study_accession": item.get("study_accession", ""),
                        "database": "ENA"
                    })
            print(f"  ENA: 发现 {len(datasets)} 个数据集")

    except Exception as e:
        print(f"  [warn] ENA 搜索失败: {e}")

    return datasets


def ncbi_search_sra(host_species: List[str], keywords: List[str], max_results: int = 200) -> List[Dict]:
    """在 NCBI SRA 中搜索宏基因组数据"""
    datasets = []

    # 构建查询
    host_terms = ' OR '.join(host_species)
    keyword_terms = ' OR '.join(keywords)
    query = f'({host_terms}) AND ({keyword_terms}) AND metagenome'

    params = urllib.parse.urlencode({
        "db": "sra",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    })

    url = f"{NCBI_ESEARCH}?{params}"

    try:
        print(f"  NCBI SRA 查询...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            ids = data.get("esearchresult", {}).get("idlist", [])
            print(f"  NCBI SRA: 发现 {len(ids)} 个项目")

            # 获取详细信息
            for i in range(0, min(len(ids), 50), 10):  # 批量获取
                batch_ids = ids[i:i+10]
                batch_data = ncbi_fetch_sra_details(batch_ids)
                datasets.extend(batch_data)
                time.sleep(0.5)

    except Exception as e:
        print(f"  [warn] NCBI SRA 搜索失败: {e}")

    return datasets


def ncbi_fetch_sra_details(ids: List[str]) -> List[Dict]:
    """获取 SRA 项目详细信息"""
    if not ids:
        return []

    datasets = []
    params = urllib.parse.urlencode({
        "db": "sra",
        "id": ",".join(ids),
        "rettype": "xml",
        "retmode": "xml",
    })

    url = f"{NCBI_EFETCH}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            xml_text = resp.read().decode()
            root = ET.fromstring(xml_text)

            for exp in root.findall(".//EXPERIMENT"):
                acc = exp.get("accession", "")
                title_elem = exp.find("TITLE")
                title = title_elem.text if title_elem is not None else ""

                # 提取文库信息
                library = exp.find("LIBRARY_DESCRIPTOR")
                if library is not None:
                    library_strategy = library.find("LIBRARY_STRATEGY")
                    library_source = library.find("LIBRARY_SOURCE")

                    if (library_strategy is not None and
                        library_strategy.text and
                        "METAGENOMIC" in library_strategy.text.upper()):

                        datasets.append({
                            "accession": acc,
                            "title": title[:200],
                            "description": "",
                            "library_strategy": library_strategy.text,
                            "database": "NCBI SRA"
                        })

    except Exception as e:
        print(f"  [warn] 获取 SRA 详情失败: {e}")

    return datasets


def ncbi_search_genome(host_species: List[str], max_results: int = 100) -> List[Dict]:
    """在 NCBI Genome 中搜索组装基因组"""
    datasets = []

    # 搜索瘤胃相关 MAGs
    query = "rumen[All Fields] AND metagenome[All Fields] AND (assembly[Filter] OR MAGs[All Fields])"

    params = urllib.parse.urlencode({
        "db": "genome",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    })

    url = f"{NCBI_ESEARCH}?{params}"

    try:
        print(f"  NCBI Genome 查询...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            ids = data.get("esearchresult", {}).get("idlist", [])
            print(f"  NCBI Genome: 发现 {len(ids)} 个项目")

            # 获取摘要信息
            if ids:
                datasets.extend(ncbi_fetch_genome_summary(ids[:30]))

    except Exception as e:
        print(f"  [warn] NCBI Genome 搜索失败: {e}")

    return datasets


def ncbi_fetch_genome_summary(ids: List[str]) -> List[Dict]:
    """获取 Genome 项目摘要"""
    if not ids:
        return []

    datasets = []
    params = urllib.parse.urlencode({
        "db": "genome",
        "id": ",".join(ids),
        "retmode": "json",
    })

    url = f"{NCBI_ESUMMARY}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            result = data.get("result", {})

            for uid in result.get("uids", []):
                info = result[uid]
                datasets.append({
                    "accession": info.get("assembly_accession", ""),
                    "title": info.get("organism_name", "")[:100],
                    "description": info.get("submission_date", ""),
                    "database": "NCBI Genome"
                })

    except Exception as e:
        print(f"  [warn] 获取 Genome 摘要失败: {e}")

    return datasets


def generate_html_report(host: str, datasets: List[Dict], output_path: str, search_date: str) -> str:
    """生成 HTML 格式的完整报告"""
    ds_rows = ""
    for d in datasets:
        ds_rows += f"""
        <tr>
          <td><a href="{get_download_link(d)}" target="_blank">{d.get('accession','')}</a></td>
          <td>{d.get('database','')}</td>
          <td>{d.get('scientific_name', d.get('title','')[:50])}</td>
          <td>{d.get('assembly_level', 'N/A')}</td>
          <td>{d.get('n_contigs', 'N/A')}</td>
          <td>{d.get('contig_n50', 'N/A')}</td>
          <td>{d.get('total_length', 'N/A')}</td>
          <td>{d.get('country', 'N/A')}</td>
          <td style="max-width:300px;font-size:10px">{d.get('description', d.get('title','')[:100])}</td>
        </tr>"""

    detail_sections = ""
    for i, d in enumerate(datasets[:50], 1):  # 限制详情数量
        detail_sections += f"""
      <h3>{i}. {d.get('accession', '')} - {d.get('title', d.get('scientific_name', ''))[:60]}</h3>
      <ul>
        <li><strong>编号:</strong> {d.get('accession', '')}</li>
        <li><strong>数据库:</strong> {d.get('database', '')}</li>
        <li><strong>物种:</strong> {d.get('scientific_name', d.get('title', ''))}</li>
        <li><strong>组装水平:</strong> {d.get('assembly_level', 'N/A')}</li>
        <li><strong>连接数:</strong> {d.get('n_contigs', 'N/A')}</li>
        <li><strong>Contig N50:</strong> {d.get('contig_n50', 'N/A')}</li>
        <li><strong>总长度:</strong> {d.get('total_length', 'N/A')}</li>
        <li><strong>国家:</strong> {d.get('country', 'N/A')}</li>
        <li><strong>描述:</strong> {d.get('description', d.get('title', ''))[:300]}</li>
        <li><strong>下载链接:</strong> <a href="{get_download_link(d)}">{get_download_link(d)}</a></li>
      </ul>
      <hr>"""

    # 统计信息
    db_stats = {}
    for d in datasets:
        db = d.get('database', 'Unknown')
        db_stats[db] = db_stats.get(db, 0) + 1

    stats_rows = ""
    for db, count in db_stats.items():
        stats_rows += f"<tr><td>{db}</td><td>{count}</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>瘤胃宏基因组数据集检索报告 ({host})</title>
<style>
  body{{font-family:"Microsoft YaHei",sans-serif;max-width:1200px;margin:0 auto;padding:30px;color:#333;font-size:12pt;line-height:1.7}}
  h1{{font-size:22pt;text-align:center;color:#1a365d;border-bottom:3px solid #2b6cb0;padding-bottom:12px}}
  h2{{font-size:15pt;color:#2c5282;border-left:4px solid #3182ce;padding-left:10px;margin-top:30px}}
  h3{{font-size:13pt;color:#2d3748;margin-top:22px}}
  table{{width:100%;border-collapse:collapse;margin:15px 0;font-size:10pt}}
  th,td{{border:1px solid #cbd5e0;padding:7px 9px;text-align:left;vertical-align:top}}
  th{{background:#2c5282;color:#fff}}
  tr:nth-child(even){{background:#f7fafc}}
  .meta{{text-align:center;color:#718096;font-size:10pt;margin-bottom:25px}}
  a{{color:#3182ce}}
  ul{{margin-left:22px}}
  li{{margin-bottom:4px}}
  hr{{border-top:1px solid #e2e8f0;margin:20px 0}}
</style>
</head>
<body>
<h1>瘤胃宏基因组数据集自动检索报告</h1>
<div class="meta">
  <p><strong>目标宿主:</strong> {host}</p>
  <p><strong>检索日期:</strong> {search_date}</p>
  <p><strong>发现数据集:</strong> {len(datasets)} 个</p>
  <p><strong>检索数据库:</strong> ENA + NCBI SRA + NCBI Genome</p>
</div>
<hr>

<h2>📊 数据库统计</h2>
<table>
  <tr><th>数据库</th><th>数据集数量</th></tr>
  {stats_rows}
</table>

<h2>📋 检索策略</h2>
<ul>
  <li><strong>目标数据:</strong> 已组装的瘤胃宏基因组数据（MAGs、scaffolds、contigs）</li>
  <li><strong>检索范围:</strong> ENA、NCBI SRA、NCBI Genome 数据库</li>
  <li><strong>过滤条件:</strong> metagenomic library strategy + assembly/scaffold/contig level</li>
  <li><strong>宿主物种:</strong> {', '.join(HOST_SPECIES.get(host, ['rumen']))}</li>
  <li><strong>关键词:</strong> {', '.join(SEARCH_KEYWORDS[:5])}...</li>
</ul>

<h2>📄 数据集汇总</h2>
<table>
  <tr>
    <th>编号</th><th>数据库</th><th>物种/标题</th><th>组装水平</th><th>连接数</th><th>N50</th><th>总长度</th><th>国家</th><th>描述</th>
  </tr>
  {ds_rows}
</table>

<h2>📄 数据集详细信息 (前50个)</h2>
{detail_sections}

<hr>
<div class="meta">
  <p>报告生成时间: {search_date} | 自动生成，建议人工核实每个数据集的详细信息</p>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  报告已保存: {output_path}")
    return output_path


def get_download_link(dataset: Dict) -> str:
    """获取数据集下载链接"""
    acc = dataset.get("accession", "")
    db = dataset.get("database", "")

    if db == "ENA":
        return f"https://www.ebi.ac.uk/ena/browser/view/{acc}"
    elif db == "NCBI SRA":
        return f"https://www.ncbi.nlm.nih.gov/sra/{acc}"
    elif db == "NCBI Genome":
        return f"https://www.ncbi.nlm.nih.gov/assembly/{acc}"
    else:
        return f"https://www.google.com/search?q={acc}"


def run(host: str, output_dir: str, max_results: int = 200):
    """主运行函数"""
    search_date = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
    os.makedirs(output_dir, exist_ok=True)

    all_datasets = []

    # 获取搜索关键词
    host_list = HOST_SPECIES.get(host, HOST_SPECIES["all"])

    print(f"\n开始检索 {host} 瘤胃宏基因组数据集...")
    print(f"目标宿主: {', '.join(host_list)}")

    # === 搜索 ENA ===
    print("\n[数据库 1/3] ENA 检索...")
    ena_query = build_ena_query(host_list, SEARCH_KEYWORDS)
    ena_datasets = ena_search(ena_query, max_results)
    all_datasets.extend(ena_datasets)
    time.sleep(1)

    # === 搜索 NCBI SRA ===
    print("\n[数据库 2/3] NCBI SRA 检索...")
    sra_datasets = ncbi_search_sra(host_list, SEARCH_KEYWORDS, max_results)
    all_datasets.extend(sra_datasets)
    time.sleep(1)

    # === 搜索 NCBI Genome ===
    print("\n[数据库 3/3] NCBI Genome 检索...")
    genome_datasets = ncbi_search_genome(host_list, max_results // 2)
    all_datasets.extend(genome_datasets)

    # 去重
    seen = set()
    unique_datasets = []
    for d in all_datasets:
        acc = d.get("accession", "")
        if acc and acc not in seen:
            seen.add(acc)
            unique_datasets.append(d)

    print(f"\n共找到 {len(unique_datasets)} 个唯一数据集")

    # === 生成报告 ===
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    html_path = os.path.join(output_dir, f"{host}_rumen_metagenome_report_{ts}.html")
    generate_html_report(host, unique_datasets, html_path, search_date)

    return html_path, unique_datasets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rumen Metagenome Collector")
    parser.add_argument("--host", default="cattle",
                       choices=["cattle", "sheep", "goat", "yak", "buffalo", "all"],
                       help="宿主物种类型")
    parser.add_argument("--output",
                       default=os.path.expanduser("~/Desktop/瘤胃宏基因组报告"),
                       help="输出目录")
    parser.add_argument("--max-results", type=int, default=200,
                       help="每个数据库最大结果数")

    args = parser.parse_args()

    html_path, datasets = run(args.host, args.output, args.max_results)
    print(f"\n完成！共发现 {len(datasets)} 个数据集")
    print(f"报告路径: {html_path}")
