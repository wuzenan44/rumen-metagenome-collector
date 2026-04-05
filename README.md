# 瘤胃宏基因组数据集收集器 (Rumen Metagenome Collector)

自动从 ENA 和 NCBI 数据库检索、收集全球瘤胃宏基因组组装数据，生成结构化报告并支持邮件自动发送。

## 主要功能

- ✅ **多数据库检索**: 同时搜索 ENA、NCBI SRA、NCBI Genome
- ✅ **智能过滤**: 只获取已组装数据 (MAGs、scaffolds、contigs)
- ✅ **多宿主支持**: 牛、羊、山羊、牦牛、水牛等反刍动物
- ✅ **HTML 报告**: 自动生成美观的数据集报告
- ✅ **邮件发送**: 支持自动将报告发送到指定邮箱
- ✅ **定时任务**: 可配置定时自动运行

## 快速开始

### 1. 基本使用

```bash
# 检索牛瘤胃宏基因组数据
python scripts/rumen_collector.py --host cattle --output ./reports

# 检索所有反刍动物
python scripts/rumen_collector.py --host all --output ./reports --max-results 500
```

### 2. 配置邮件发送

```bash
# 设置环境变量
export RUMEN_SMTP_USER="your_email@example.com"
export RUMEN_SMTP_PASS="your_auth_code"

# 运行并自动发送邮件
python scripts/daily_run.py
```

## 输出示例

生成的 HTML 报告包含:

- 📊 数据库统计 (各数据库数据集数量)
- 🔍 检索策略说明
- 📋 数据集汇总表 (编号、物种、组装水平、连接数、N50、总长度、国家、描述)
- 📄 前50个数据集详细信息
- 🔗 直接下载链接

## 宿主物种选项

| 值 | 说明 |
|---|---|
| `cattle` | 牛 (Bos taurus) |
| `sheep` | 羊 (Ovis aries) |
| `goat` | 山羊 (Capra hircus) |
| `yak` | 牦牛 (Bos mutus) |
| `buffalo` | 水牛 (Bubalus bubalis) |
| `all` | 所有反刍动物 |

## 邮箱配置指南

### QQ邮箱

1. 登录 QQ邮箱 → 设置 → 账户
2. 开启 SMTP 服务
3. 生成授权码 (不是登录密码)
4. 设置环境变量:
   ```bash
   export RUMEN_SMTP_USER="your_qq@qq.com"
   export RUMEN_SMTP_PASS="your_auth_code"
   ```

### Gmail

1. 启用两步验证
2. 生成应用专用密码
3. 设置环境变量:
   ```bash
   export RUMEN_SMTP_USER="your_gmail@gmail.com"
   export RUMEN_SMTP_PASS="your_app_password"
   ```

### 163邮箱

1. 设置 → POP3/SMTP/IMAP
2. 开启 SMTP 服务
3. 获取授权码
4. 设置环境变量:
   ```bash
   export RUMEN_SMTP_USER="your_163@163.com"
   export RUMEN_SMTP_PASS="your_auth_code"
   ```

## 定时任务设置

### Linux/macOS (crontab)

```bash
# 编辑 crontab
crontab -e

# 每天早上8点运行
0 8 * * * cd /path/to/rumen-metagenome-collector && python scripts/daily_run.py
```

### Windows (任务计划程序)

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器 (如每天8点)
4. 操作: 启动程序 `python.exe`
5. 参数: `C:\path\to\scripts\daily_run.py`

## 文件结构

```
rumen-metagenome-collector/
├── SKILL.md              # Skill 说明文件
├── README.md             # 本文件
├── LICENSE               # MIT 许可证
└── scripts/
    ├── rumen_collector.py    # 主搜索脚本
    ├── send_report.py        # 邮件发送
    └── daily_run.py          # 定时任务入口
```

## 系统要求

- Python 3.8+
- 网络连接 (访问 ENA/NCBI API)
- (可选) 邮箱账户 (用于发送报告)

## 注意事项

1. **API 限制**: 内置延迟避免超过 ENA/NCBI API 限制
2. **网络稳定性**: 搜索需要 5-10 分钟，请保持网络稳定
3. **数据验证**: 建议人工核对报告中的数据集信息
4. **邮件安全**: 不要在代码中硬编码邮箱密码

## 使用场景

- 📚 **文献综述**: 收集特定物种的瘤胃宏基因组数据
- 🔬 **元分析**: 跨研究比较瘤胃微生物组
- 📊 **数据库构建**: 构建自定义瘤胃微生物基因组数据库
- 📧 **监控提醒**: 定期接收新数据集通知
- 💰 **基金申请**: 展示数据可用性

## 性能

- 搜索时间: 5-10 分钟 (3个数据库)
- 结果数量: 50-500+ (取决于物种和关键词)
- 报告大小: 100KB - 2MB

## 故障排除

### 问题: 搜索结果为空

- 检查网络连接
- 尝试增加 `--max-results` 参数
- 检查关键词是否合适

### 问题: 邮件发送失败

- 确认 SMTP_USER 和 SMTP_PASS 已正确设置
- 确认使用的是授权码而非登录密码
- 检查邮箱是否开启了 SMTP 服务

### 问题: 报告无法打开

- 确认输出目录存在且有写入权限
- 检查 HTML 文件是否完整生成

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交问题和改进建议!

## 致谢

- ENA (European Nucleotide Archive)
- NCBI (National Center for Biotechnology Information)
- 原始灵感来自 geo-dataset-researcher skill
