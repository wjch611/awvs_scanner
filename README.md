**AWVS 批量扫描工具**

本工具基于 Python 实现，利用 Acunetix WVS (AWVS) API 批量添加扫描目标、配置扫描参数并启动扫描任务，支持自定义扫描速度、大小写敏感选项及代理设置。

------

## 功能概览

- 从文件中读取待扫描 URL 列表
- 调用 AWVS API 批量添加扫描目标
- 按需配置扫描参数：
  - 扫描速度 (`fast`, `moderate`, `slow`, `sequential`, `slower`)
  - 爬虫大小写敏感 (`yes`, `no`, `auto`)
  - 可选 HTTP 代理（支持 `http://host:port` 与 `http://user:pass@host:port`）
- 启动扫描任务并输出 Scan ID

------

## 环境与依赖

- Python 3.6+

- 依赖包:

  ```bash
  pip install requests
  ```

------

## 使用说明

将脚本保存为 `scan.py`，配置好 AWVS API 地址与 Key 后，即可执行。

```bash
python scan.py --file targets.txt [options]
```

### 参数说明

| 参数               | 说明                                                         | 示例                            |
| ------------------ | ------------------------------------------------------------ | ------------------------------- |
| `--file`           | **必选**，URL 列表文件路径，每行一个完整 URL                 | `targets.txt`                   |
| `--speed`          | 扫描速度，可选: `slow`, `moderate`, `fast`, `sequential`, `slower` | `--speed slow`                  |
| `--case-sensitive` | 是否区分大小写，可选: `yes`, `no`, `auto`                    | `--case-sensitive yes`          |
| `--proxy`          | 可选 HTTP 代理，支持带鉴权                                   | `--proxy http://127.0.0.1:8080` |

### 示例

- **基础运行**（默认速度 `fast`，无代理）：

  ```bash
  python awvs_scanner.py --file targets.txt --speed moderate --proxy http://127.0.0.1:7777
  ```

- **指定速度和大小写敏感**：

  ```bash
  python scan.py --file targets.txt --speed moderate --case-sensitive yes
  ```

- **使用代理**：

  ```bash
  python scan.py --file targets.txt --proxy http://user:pass@proxy.example.com:8080
  ```

------

## 日志与错误处理

- 添加目标失败或 API 请求异常时，会打印对应错误并跳过
- 代理解析失败时，会提示解析错误并忽略代理配置

------

## AWVS API 配置

脚本中默认配置：

```python
API_URL = "https://localhost:3443"
API_KEY = "<你的_API_KEY>"
```

请根据实际环境修改。

------

## 许可

MIT License