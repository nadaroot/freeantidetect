"""
Browser locator, portable downloader, and process launcher for Root Detect.
Supports both Chromium-based engines and Gecko/Firefox engines.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from rootdetect.downloader import find_downloaded_browsers, download_chromium

# Extension source directory inside package
EXTENSION_SRC_DIR = Path(__file__).parent / "extension"

def find_installed_browsers() -> List[Dict[str, str]]:
    """
    Scans system and local storage for available Chromium and Gecko browsers.
    Returns list of dicts: [{"name": "...", "path": "...", "type": "...", "engine": "chromium|gecko"}]
    """
    found = []

    # 1. Check portable downloaded browsers first
    portable = find_downloaded_browsers()
    found.extend(portable)

    # 2. Check system installed browsers
    system = platform.system().lower()

    if "darwin" in system:
        candidates = [
            ("Google Chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "chromium"),
            ("Google Chrome (User)", Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "chromium"),
            ("Brave Browser", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser", "chromium"),
            ("Microsoft Edge", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "chromium"),
            ("Mozilla Firefox", "/Applications/Firefox.app/Contents/MacOS/firefox", "gecko"),
            ("Firefox Developer Edition", "/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox", "gecko"),
            ("LibreWolf", "/Applications/LibreWolf.app/Contents/MacOS/librewolf", "gecko"),
            ("Floorp", "/Applications/Floorp.app/Contents/MacOS/floorp", "gecko"),
            ("Zen Browser", "/Applications/Zen Browser.app/Contents/MacOS/zen", "gecko"),
            ("Chromium", "/Applications/Chromium.app/Contents/MacOS/Chromium", "chromium"),
            ("Arc", "/Applications/Arc.app/Contents/MacOS/Arc", "chromium")
        ]
        for name, p, engine in candidates:
            path_obj = Path(p)
            if path_obj.exists() and os.access(path_obj, os.X_OK):
                found.append({"name": name, "path": str(path_obj.resolve()), "type": name.lower(), "engine": engine})

    elif "windows" in system:
        env_prog = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        env_prog86 = os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")
        env_local = os.environ.get("LOCALAPPDATA", "C:\\Users\\User\\AppData\\Local")

        candidates = [
            ("Google Chrome", os.path.join(env_prog, "Google\\Chrome\\Application\\chrome.exe"), "chromium"),
            ("Google Chrome", os.path.join(env_prog86, "Google\\Chrome\\Application\\chrome.exe"), "chromium"),
            ("Brave Browser", os.path.join(env_prog, "BraveSoftware\\Brave-Browser\\Application\\brave.exe"), "chromium"),
            ("Microsoft Edge", os.path.join(env_prog86, "Microsoft\\Edge\\Application\\msedge.exe"), "chromium"),
            ("Mozilla Firefox", os.path.join(env_prog, "Mozilla Firefox\\firefox.exe"), "gecko"),
            ("Mozilla Firefox", os.path.join(env_prog86, "Mozilla Firefox\\firefox.exe"), "gecko"),
            ("LibreWolf", os.path.join(env_prog, "LibreWolf\\librewolf.exe"), "gecko"),
        ]
        for name, p, engine in candidates:
            if p and os.path.exists(p):
                found.append({"name": name, "path": p, "type": name.lower(), "engine": engine})

    else: # Linux
        candidates = [
            ("Google Chrome", "/usr/bin/google-chrome", "chromium"),
            ("Google Chrome", "/usr/bin/google-chrome-stable", "chromium"),
            ("Brave Browser", "/usr/bin/brave-browser", "chromium"),
            ("Mozilla Firefox", "/usr/bin/firefox", "gecko"),
            ("LibreWolf", "/usr/bin/librewolf", "gecko"),
            ("Chromium", "/usr/bin/chromium", "chromium"),
            ("Microsoft Edge", "/usr/bin/microsoft-edge", "chromium"),
        ]
        for name, p, engine in candidates:
            if os.path.exists(p) and os.access(p, os.X_OK):
                found.append({"name": name, "path": p, "type": name.lower(), "engine": engine})

    return found

def get_default_browser_path(auto_download: bool = False) -> Optional[str]:
    browsers = find_installed_browsers()
    if browsers:
        return browsers[0]["path"]
    
    if auto_download:
        return download_chromium()
    return None

def is_gecko_browser(browser_path: str) -> bool:
    low = browser_path.lower()
    return any(name in low for name in ["firefox", "librewolf", "floorp", "zen", "gecko"])

def prepare_firefox_profile(profile: Dict[str, Any], user_data_path: Path):
    """
    Configures user.js for Firefox-based profiles with stealth and proxy settings.
    """
    user_data_path.mkdir(parents=True, exist_ok=True)
    fp = profile.get("fingerprint", {})
    proxy = profile.get("proxy")

    prefs = [
        'user_pref("privacy.resistFingerprinting", true);',
        'user_pref("media.peerconnection.enabled", false);', # WebRTC leak shield
        'user_pref("dom.webdriver.enabled", false);',
        'user_pref("marionette.enabled", false);',
        'user_pref("toolkit.telemetry.enabled", false);',
        'user_pref("datareporting.healthreport.uploadEnabled", false);'
    ]

    if fp.get("user_agent"):
        prefs.append(f'user_pref("general.useragent.override", "{fp["user_agent"]}");')

    if proxy:
        proto = proxy.get("protocol", "http")
        host = proxy.get("host")
        port = proxy.get("port")
        if host and port:
            prefs.append('user_pref("network.proxy.type", 1);') # Manual proxy
            if proto == "socks5":
                prefs.append(f'user_pref("network.proxy.socks", "{host}");')
                prefs.append(f'user_pref("network.proxy.socks_port", {port});')
                prefs.append('user_pref("network.proxy.socks_version", 5);')
                prefs.append('user_pref("network.proxy.socks_remote_dns", true);')
            else:
                prefs.append(f'user_pref("network.proxy.http", "{host}");')
                prefs.append(f'user_pref("network.proxy.http_port", {port});')
                prefs.append(f'user_pref("network.proxy.ssl", "{host}");')
                prefs.append(f'user_pref("network.proxy.ssl_port", {port});')

    user_js_file = user_data_path / "user.js"
    with open(user_js_file, "w", encoding="utf-8") as f:
        f.write("\n".join(prefs) + "\n")

def prepare_profile_extension(profile: Dict[str, Any], target_dir: Path) -> Path:
    """
    Creates a customized unpacked Chrome extension in target_dir for this specific profile.
    """
    ext_dir = target_dir / "extension"
    ext_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy manifest.json & background.js
    shutil.copy(EXTENSION_SRC_DIR / "manifest.json", ext_dir / "manifest.json")
    shutil.copy(EXTENSION_SRC_DIR / "background.js", ext_dir / "background.js")

    fp = profile.get("fingerprint", {})
    proxy_info = profile.get("proxy")

    # 2. Prepare config for background & inject
    config_data = {
        "seed": fp.get("seed", 42),
        "webgl_vendor": fp.get("webgl_vendor"),
        "webgl_renderer": fp.get("webgl_renderer"),
        "platform": fp.get("platform"),
        "hardware_concurrency": fp.get("hardware_concurrency", 8),
        "device_memory": fp.get("device_memory", 16),
        "max_touch_points": fp.get("max_touch_points", 0),
        "is_mobile": fp.get("is_mobile", False),
        "canvas_noise": fp.get("canvas_noise", True),
        "audio_noise": fp.get("audio_noise", True),
        "proxy_auth": {
            "username": proxy_info.get("username"),
            "password": proxy_info.get("password")
        } if proxy_info and proxy_info.get("username") else None
    }

    with open(ext_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    # 3. Create customized inject.js with config baked in
    with open(EXTENSION_SRC_DIR / "inject.js", "r", encoding="utf-8") as f:
        inject_base = f.read()

    config_js_snippet = f"window.__ROOT_DETECT_CONFIG__ = {json.dumps(config_data)};\n"
    with open(ext_dir / "inject.js", "w", encoding="utf-8") as f:
        f.write(config_js_snippet + inject_base)

    return ext_dir

def launch_browser(
    profile: Dict[str, Any],
    browser_path: Optional[str] = None,
    custom_url: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Launches Chrome/Chromium or Firefox with isolated profile, custom flags, and stealth settings.
    """
    if not browser_path:
        browser_path = get_default_browser_path(auto_download=True)
        if not browser_path:
            return False, "Не найден браузер и не удалось выполнить авто-загрузку"

    user_data_path = Path(profile["user_data_path"])
    user_data_path.mkdir(parents=True, exist_ok=True)
    target_url = custom_url or "https://browserleaks.com/canvas"

    fp = profile.get("fingerprint", {})
    proxy = profile.get("proxy")

    if is_gecko_browser(browser_path):
        # --- GECKO / FIREFOX ENGINE LAUNCH ---
        prepare_firefox_profile(profile, user_data_path)
        flags = [
            browser_path,
            "-no-remote",
            "-profile",
            str(user_data_path.resolve()),
            target_url
        ]
    else:
        # --- CHROMIUM ENGINE LAUNCH ---
        profile_base_dir = user_data_path.parent
        ext_dir = prepare_profile_extension(profile, profile_base_dir)

        flags = [
            browser_path,
            f"--user-data-dir={str(user_data_path.resolve())}",
            f"--load-extension={str(ext_dir.resolve())}",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "--password-store=basic",
            "--disable-features=IsolateOrigins,site-per-process",
            f"--window-size={fp.get('screen_width', 1920)},{fp.get('screen_height', 1080)}"
        ]

        if fp.get("is_mobile"):
            flags.extend([
                "--touch-events=enabled",
                "--enable-touch-drag-drop",
                f"--force-device-scale-factor={fp.get('scale_factor', 3.0)}"
            ])

        if fp.get("user_agent"):
            flags.append(f"--user-agent={fp['user_agent']}")

        if fp.get("languages"):
            primary_lang = fp["languages"].split(",")[0].split(";")[0]
            flags.append(f"--lang={primary_lang}")

        if proxy and proxy.get("chrome_arg"):
            flags.append(f"--proxy-server={proxy['chrome_arg']}")

        flags.append(target_url)

    try:
        if platform.system().lower() == "windows":
            subprocess.Popen(
                flags,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                close_fds=True
            )
        else:
            subprocess.Popen(
                flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        return True, "Браузер успешно запущен"
    except Exception as e:
        return False, f"Ошибка при запуске браузера: {str(e)}"
