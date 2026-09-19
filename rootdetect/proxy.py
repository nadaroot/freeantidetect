"""
Proxy parser, formatter, and checker for Root Detect.
Supports both standard library urllib and requests.
"""

import time
import json
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any

try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False

def parse_proxy_string(proxy_str: str) -> Optional[Dict[str, Any]]:
    """
    Parses proxy in formats:
    - protocol://user:pass@ip:port
    - protocol://ip:port
    - ip:port:user:pass
    - ip:port
    Returns dict with protocol, host, port, username, password, formatted_url, chrome_proxy_arg.
    """
    if not proxy_str or not proxy_str.strip():
        return None

    raw = proxy_str.strip()
    protocol = "http"
    username = None
    password = None
    host = None
    port = None

    if "://" in raw:
        parsed = urllib.parse.urlparse(raw)
        protocol = parsed.scheme.lower()
        if protocol not in ["http", "https", "socks4", "socks5"]:
            protocol = "http"
        host = parsed.hostname
        port = parsed.port
        username = parsed.username
        password = parsed.password
    else:
        parts = raw.split(":")
        if len(parts) == 2:
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                return None
        elif len(parts) == 4:
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                return None
            username = parts[2]
            password = parts[3]
        else:
            return None

    if not host or not port:
        return None

    chrome_arg = f"{protocol}://{host}:{port}"
    
    if username and password:
        requests_url = f"{protocol}://{urllib.parse.quote(username)}:{urllib.parse.quote(password)}@{host}:{port}"
    else:
        requests_url = f"{protocol}://{host}:{port}"

    return {
        "raw": raw,
        "protocol": protocol,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "requests_url": requests_url,
        "chrome_arg": chrome_arg
    }

def check_proxy(proxy_str: str, timeout: int = 7) -> Dict[str, Any]:
    """
    Checks if proxy is alive, measures latency, detects external IP and location.
    Works with urllib (built-in) or requests.
    """
    parsed = parse_proxy_string(proxy_str)
    if not parsed:
        return {"status": "error", "message": "Неверный формат прокси"}

    start = time.time()
    try:
        if HAVE_REQUESTS:
            proxies = {
                "http": parsed["requests_url"],
                "https": parsed["requests_url"]
            }
            resp = requests.get(
                "http://ip-api.com/json/?fields=status,message,country,countryCode,city,query,isp",
                proxies=proxies,
                timeout=timeout
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return {
                        "status": "online",
                        "ip": data.get("query"),
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "city": data.get("city"),
                        "isp": data.get("isp"),
                        "latency_ms": latency,
                        "parsed": parsed
                    }
        else:
            proxy_handler = urllib.request.ProxyHandler({
                'http': parsed["requests_url"],
                'https': parsed["requests_url"]
            })
            opener = urllib.request.build_opener(proxy_handler)
            req = urllib.request.Request(
                "http://ip-api.com/json/?fields=status,message,country,countryCode,city,query,isp",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with opener.open(req, timeout=timeout) as response:
                latency = int((time.time() - start) * 1000)
                data = json.loads(response.read().decode('utf-8'))
                if data.get("status") == "success":
                    return {
                        "status": "online",
                        "ip": data.get("query"),
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "city": data.get("city"),
                        "isp": data.get("isp"),
                        "latency_ms": latency,
                        "parsed": parsed
                    }

        return {"status": "error", "message": "Не удалось получить гео-данные"}
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        err_msg = str(e)
        if "timeout" in err_msg.lower():
            err_msg = "Таймаут соединения"
        elif "connection" in err_msg.lower() or "proxy" in err_msg.lower():
            err_msg = "Не удалось подключиться к прокси"
        return {
            "status": "offline",
            "message": err_msg,
            "latency_ms": latency
        }
