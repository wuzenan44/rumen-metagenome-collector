---
name: rumen-metagenome-collector
description: Automatically discover and collect assembled rumen metagenome datasets from ENA and NCBI databases. Searches for metagenome-assembled genomes (MAGs), assembled contigs, and complete metagenome assemblies from global rumen microbiome studies. Generates structured HTML reports with dataset metadata and supports email delivery. Use when users need to systematically collect public rumen metagenomic datasets, monitor new releases, or compile dataset inventories for microbiome research. Keywords: rumen, metagenome, MAGs, microbiome, ENA, NCBI, SRA, assembly, cow, cattle, sheep, goat, livestock, gut microbiome.
license: MIT
compatibility: Requires Python 3.8+ for dataset search and metadata retrieval. Internet connection needed for ENA/NCBI API access. No API keys required - uses free public APIs.
metadata:
  version: "1.0.0"
  category: Data & Analytics
  tags:
    - bioinformatics
    - metagenomics
    - microbiome
    - rumen
    - ENA
    - NCBI
    - MAGs
    - data-collection
    - automation
    - email
    - livestock
---

# Rumen Metagenome Collector

## Overview

This skill systematically collects assembled rumen metagenome datasets from ENA (European Nucleotide Archive) and NCBI (National Center for Biotechnology Information) databases through targeted searches, generates structured HTML reports, and supports email delivery of findings.

## How It Works

### Data Sources

**Primary Databases:**
- **ENA (European Nucleotide Archive)**: European primary archive for nucleotide sequencing data
- **NCBI SRA**: Sequence Read Archive for raw sequencing data
- **NCBI GenBank**: Assembled genome and metagenome data

**Target Data Types:**
- Metagenome-Assembled Genomes (MAGs)
- Assembled contigs/scaffolds
- Complete metagenome assemblies
- Binned genome collections

### Search Strategy

The skill uses a multi-faceted search approach:

1. **Keyword-based queries**: Search for rumen-related terms
2. **Assembly filters**: Target only assembled data (not raw reads)
3. **Host species**: cattle, cow, sheep, goat, yak, buffalo
4. **Geographic scope**: Global datasets
5. **Study type**: Metagenomic studies only

### Key Search Terms

- Rumen microbiome metagenome
- Rumen metagenome assembly
- Cow/cattle/sheep rumen microbiome
- Rumen MAGs
- Rumen microbial community
- Rumen fermentation metagenome

## Quick Start

### Prerequisites
- Python 3.8+
- Internet connection
- Email account (for delivery feature, optional)

### Basic Usage

```bash
# Search for rumen metagenome datasets
python scripts/rumen_collector.py \
  --host "cattle" \
  --output "./reports" \
  --max-results 200
```

### With Email Delivery

```bash
# Set SMTP credentials
export RUMEN_SMTP_USER="your_email@example.com"
export RUMEN_SMTP_PASS="your_auth_code"

# Run with email
python scripts/daily_run.py
```

### Search Multiple Host Species

```bash
# Search all ruminant species
python scripts/rumen_collector.py \
  --host "all" \
  --output "./reports" \
  --max-results 500
```

## Output

Generates an HTML report containing:
- Search methodology and database sources
- Summary statistics (total datasets, by species, by country)
- Detailed metadata table:
  - Accession ID (ENA/NCBI)
  - Host species
  - Geographic origin
  - Assembly statistics
  - Study title and description
  - Download links
  - Publication information (if available)

## Customization

### Target Different Species

Edit `HOST_SPECIES` in `scripts/rumen_collector.py`:

```python
HOST_SPECIES = {
    "cattle": ["Bos taurus", "cow", "cattle", "bovine"],
    "sheep": ["Ovis aries", "sheep", "ovine"],
    "goat": ["Capra hircus", "goat", "caprine"],
    "yak": ["Bos mutus", "yak"],
    "buffalo": ["Bubalus bubalis", "buffalo"],
}
```

### Add Custom Keywords

Edit `SEARCH_KEYWORDS` in `scripts/rumen_collector.py`:

```python
SEARCH_KEYWORDS = [
    "rumen metagenome",
    "rumen microbiome",
    "rumen MAGs",
    # Add your custom keywords
]
```

### Configure Email

Edit `scripts/daily_run.py`:

```python
CONFIG = {
    "hosts": ["cattle", "sheep", "goat"],
    "email_to": "your@email.com",
    "output_dir": "./reports",
}
```

## Use Cases

- **Meta-analysis**: Collect datasets for cross-study microbiome analysis
- **Database curation**: Build custom rumen metagenome databases
- **Monitoring alerts**: Track new rumen metagenome releases
- **Grant preparation**: Demonstrate data availability for proposals
- **Training datasets**: Compile data for machine learning pipelines

## Understanding ENA Search API

The skill uses ENA's powerful search API with filters:

- **Assembly level**: Target only assembled data
- **Library source**: METAGENOMIC
- **Material**: Environmental samples (rumen fluid/content)
- **Assembly type**: Complete genome, scaffold, contig

Example ENA query:
```
("rumen"[Title] OR "rumen"[Description])
AND "metagenomic"[Library Strategy]
AND "assembly"[Assembly Level]
```

## Understanding NCBI Search

NCBI searches target:
- **SRA**: For raw reads with assembly information
- **GenBank**: For assembled MAGs and genomes
- **BioProject**: For complete study metadata

## Error Handling

- Network timeouts: 15-30 second timeouts with retry
- API failures: Graceful degradation with warnings
- Missing metadata: Reports all available data
- Email failures: Clear troubleshooting guidance
- Large datasets: Paginated retrieval to avoid timeouts

## File Structure

```
rumen-metagenome-collector/
├── SKILL.md              # This file
├── README.md             # Documentation
├── LICENSE               # MIT License
└── scripts/
    ├── rumen_collector.py    # Main search script (Python 3)
    ├── ena_api.py           # ENA database interface
    ├── ncbi_api.py          # NCBI database interface
    ├── report_generator.py  # HTML report generation
    ├── send_report.py       # Email sending (Python 2/3)
    └── daily_run.py         # Scheduled task entry
```

## Performance

- Search time: 5-10 minutes for comprehensive queries
- Rate limiting: Built-in delays between API calls
- Max results: Configurable (default: 200 per database)
- API limits: Respects ENA/NCBI rate limits

## Advanced Features

### Assembly Quality Filtering

```bash
# Filter for high-quality assemblies only
python scripts/rumen_collector.py \
  --min-contig-n50 10000 \
  --min-completeness 90 \
  --max-contamination 5
```

### Geographic Filtering

```bash
# Target specific regions
python scripts/rumen_collector.py \
  --country "China,USA,Germany" \
  --output "./reports"
```

### Date Range Queries

```bash
# Search recent datasets only
python scripts/rumen_collector.py \
  --after-date "2023-01-01" \
  --output "./reports"
```

## Integration with Downstream Analysis

Collected datasets can be used for:
- Taxonomic profiling (Kraken2, MetaPhlAn)
- Functional annotation (HUMAnN, eggNOG)
- Comparative genomics
- Pangenome analysis
- Machine learning feature extraction

## Contributing

When contributing to this skill:
1. Maintain compatibility with Python 3.8+
2. Respect database rate limits
3. Add proper error handling
4. Document new search keywords
5. Test email delivery before deploying

## License

MIT License - See LICENSE file for details
