# AWVS 批量扫描工具

本工具用于通过 Acunetix Web Vulnerability Scanner (AWVS) API 对一批目标 URL 执行自动化扫描，包括添加目标、配置扫描参数及启动不同模板的扫描。

---

## 功能

* 从文件批量读取待扫描的 URL 列表
* 支持自定义爬虫速度、大小写敏感、代理设置
* 可选择不同扫描类型（Full Scan、Critical/High Risk、XSS、SQL 注入、Weak Passwords、Crawl Only）
* 自动添加扫描目标、配置目标属性并启动扫描任务
* 对常见 API 请求失败进行错误提示与回退处理

---

## 环境依赖

* Python 3.6+
* requests

```bash
pip install requests
```

---

## 文件结构

```text
awvs_batch_scanner.py    # 主脚本文件
urls.txt                 # 示例待扫描 URL 列表，每行一个 URL
README.md                # 本说明文档
```

---

## 使用方法

```bash
python awvs_batch_scanner.py --file <URL 列表文件> [OPTIONS]
```

### 参数说明

| 参数                 | 说明                                           | 默认值    |
| ------------------ | -------------------------------------------- | ------ |
| `--file`           | 必需，待扫描 URL 列表文件路径，每行一个 URL                   | —      |
| `--speed`          | 扫描速度，可选 slow/moderate/fast/sequential/slower | `fast` |
| `--case-sensitive` | 爬虫是否大小写敏感，可选 yes/no/auto                     | `auto` |
| `--proxy`          | 可选，代理地址，例如 `http://user:pass@host:port`      | —      |
| `--scan-type`      | 扫描类型，可选: full/critical/xss/sql/weak/crawl    | `full` |

### 扫描类型对照

| 模板键        | 描述                           | Profile ID                             |
| ---------- | ---------------------------- | -------------------------------------- |
| `full`     | 全扫描 (Full Scan)              | `11111111-1111-1111-1111-111111111111` |
| `critical` | 关键/高危漏洞 (Critical/High Risk) | `11111111-1111-1111-1111-111111111112` |
| `xss`      | 跨站脚本 (XSS)                   | `11111111-1111-1111-1111-111111111116` |
| `sql`      | SQL 注入 (SQL Injection)       | `11111111-1111-1111-1111-111111111113` |
| `weak`     | 弱口令 (Weak Passwords)         | `11111111-1111-1111-1111-111111111115` |
| `crawl`    | 仅爬虫 (Crawl Only)             | `11111111-1111-1111-1111-111111111117` |

---

## 示例

将 `urls.txt` 中的 URL 以 fast 速度、auto 大小写、无代理、启动 SQL 注入模板扫描：

```bash
python awvs_batch_scanner.py \
  --file urls.txt \
  --speed fast \
  --case-sensitive auto \
  --scan-type sql
```

启用代理并进行全量扫描：

```bash
python awvs_batch_scanner.py \
  --file urls.txt \
  --proxy http://127.0.0.1:8080 \
  --scan-type full
```

---

## 常见问题

1. **添加目标失败**：请检查 AWVS API 地址及 KEY 是否正确，确保服务可用。
2. **配置失败或启动失败**：查看打印的 HTTP 响应码及内容，排查网络、权限或参数问题。
3. **自定义扫描模板**：如需使用自定义 Profile ID，可修改脚本中的 `PROFILE_MAP` 或直接在命令行传递。

---

## 许可证

MIT License
