import requests
import argparse
import time
import json
import urllib.parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 内置扫描模板映射
PROFILE_MAP = {
    'full': '11111111-1111-1111-1111-111111111111',
    'critical': '11111111-1111-1111-1111-111111111112',
    'xss': '11111111-1111-1111-1111-111111111116',
    'sql': '11111111-1111-1111-1111-111111111113',
    'weak': '11111111-1111-1111-1111-111111111115',
    'crawl': '11111111-1111-1111-1111-111111111117'
}

class AWVSScanner:
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-Auth': api_key,
            'Content-Type': 'application/json'
        }

    def add_target(self, target_url, description="Added by AWVS Batch Tool"):  # 添加扫描目标
        data = {"address": target_url, "description": description}
        try:
            resp = requests.post(
                f"{self.api_url}/api/v1/targets", json=data,
                headers=self.headers, verify=False, timeout=30
            )
            if resp.status_code == 201:
                return resp.json().get('target_id')
            print(f"[!] 添加目标失败: HTTP {resp.status_code}, 响应: {resp.text}")
        except Exception as e:
            print(f"[!] 添加目标请求异常: {e}")
        return None

    def configure_target(self, target_id, config: dict):  # 配置目标扫描参数
        default_cfg = {
            "limit_crawler_scope": True,
            "sensor": False,
            "scan_speed": "fast",
            "case_sensitive": "auto",
            "technologies": [],
            "custom_headers": [],
            "custom_cookies": [],
            "excluded_paths": [],
            "user_agent": "",
            "debug": False,
            "ad_blocker": True
        }
        default_cfg.update(config)
        try:
            resp = requests.patch(
                f"{self.api_url}/api/v1/targets/{target_id}/configuration",
                json=default_cfg, headers=self.headers,
                verify=False, timeout=30
            )
            if resp.status_code == 204:
                return True
            print(f"[!] 配置失败: HTTP {resp.status_code}, 数据: {json.dumps(default_cfg)}")
            print(f"[!] 响应内容: {resp.text}")
        except Exception as e:
            print(f"[!] 配置请求异常: {e}")
        return False

    def start_scan(self, target_id, profile_key='full'):  # 启动扫描任务，支持多种扫描模板
        profile_id = PROFILE_MAP.get(profile_key)
        if not profile_id:
            print(f"[!] 未知的扫描类型 '{profile_key}'，使用默认 'full' 模板")
            profile_id = PROFILE_MAP['full']

        scan_config = {
            "target_id": target_id,
            "profile_id": profile_id,
            "schedule": {"disable": False}
        }
        try:
            resp = requests.post(
                f"{self.api_url}/api/v1/scans", json=scan_config,
                headers=self.headers, verify=False, timeout=30
            )
            if resp.status_code == 201:
                return resp.json().get('scan_id')
            print(f"[!] 启动扫描失败: HTTP {resp.status_code}, 响应: {resp.text}")
        except Exception as e:
            print(f"[!] 启动扫描请求异常: {e}")
        return None


def parse_proxy(proxy_url: str) -> dict:  # 解析代理 URL 到 AWVS ProxySettings 格式
    result = {}
    parsed = urllib.parse.urlparse(proxy_url)
    if not parsed.scheme or not parsed.hostname or not parsed.port:
        raise ValueError(f"Invalid proxy URL: {proxy_url}")
    result["enabled"] = True
    result["address"] = parsed.hostname
    result["port"] = parsed.port
    result["protocol"] = parsed.scheme
    if parsed.username:
        result["username"] = urllib.parse.unquote(parsed.username)
    if parsed.password:
        result["password"] = urllib.parse.unquote(parsed.password)
    return result


def main():
    parser = argparse.ArgumentParser(description="AWVS 批量扫描工具")
    parser.add_argument("--file", required=True, help="URL 列表文件路径")
    parser.add_argument("--speed", default="fast",
                        choices=["slow", "moderate", "fast", "sequential", "slower"],
                        help="扫描速度 (slow/moderate/fast/sequential/slower)")
    parser.add_argument("--proxy", help="代理地址，如 http://user:pass@host:port")
    parser.add_argument("--case-sensitive", dest="case_sensitive",
                        choices=["yes", "no", "auto"], default="auto",
                        help="爬虫大小写敏感 (yes/no/auto)")
    parser.add_argument("--scan-type", dest="scan_type",
                        choices=list(PROFILE_MAP.keys()), default="full",
                        help="扫描类型: full/critical/xss/sql/weak/crawl")
    args = parser.parse_args()

    API_URL = "https://localhost:3443"
    API_KEY = "1986ad8c0a5b3df4d7028d5f3c06e936ca29fbd14f4044246b1b1df8ffe2e73ff"
    scanner = AWVSScanner(API_URL, API_KEY)

    proxy_cfg = None
    if args.proxy:
        try:
            proxy_cfg = parse_proxy(args.proxy)
        except Exception as e:
            print(f"[!] 解析代理失败: {e}，跳过代理配置。")

    with open(args.file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        print(f"\n[+] 处理目标: {url}")
        target_id = scanner.add_target(url)
        if not target_id:
            print("  |-- ❌ 添加目标失败，跳过")
            continue

        cfg = {"scan_speed": args.speed, "case_sensitive": args.case_sensitive}
        if proxy_cfg:
            cfg["proxy"] = proxy_cfg

        print(f"  |-- 正在配置目标 (速度:{args.speed} 大小写:{args.case_sensitive} 代理:{'已配置' if proxy_cfg else '无'})...")
        if not scanner.configure_target(target_id, cfg):
            print("  |-- ⚠ 配置失败，使用默认配置")

        print(f"  |-- 正在启动'{args.scan_type}'扫描...")
        scan_id = scanner.start_scan(target_id, args.scan_type)
        if scan_id:
            print(f"  |-- ✅ 扫描已启动 (ID:{scan_id})")
        else:
            print("  |-- ❌ 启动扫描失败")

        time.sleep(1)

if __name__ == "__main__":
    main()
