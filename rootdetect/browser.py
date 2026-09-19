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
if getattr(sys, '_MEIPASS', None):
    EXTENSION_SRC_DIR = Path(sys._MEIPASS) / "rootdetect" / "extension"
else:
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
        env_local = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        env_appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))

        candidates = [
            # Google Chrome
            ("Google Chrome", os.path.join(env_prog, "Google\\Chrome\\Application\\chrome.exe"), "chromium"),
            ("Google Chrome", os.path.join(env_prog86, "Google\\Chrome\\Application\\chrome.exe"), "chromium"),
            ("Google Chrome (User)", os.path.join(env_local, "Google\\Chrome\\Application\\chrome.exe"), "chromium"),
            # Brave
            ("Brave Browser", os.path.join(env_prog, "BraveSoftware\\Brave-Browser\\Application\\brave.exe"), "chromium"),
            ("Brave Browser (User)", os.path.join(env_local, "BraveSoftware\\Brave-Browser\\Application\\brave.exe"), "chromium"),
            # Microsoft Edge
            ("Microsoft Edge", os.path.join(env_prog86, "Microsoft\\Edge\\Application\\msedge.exe"), "chromium"),
            ("Microsoft Edge", os.path.join(env_prog, "Microsoft\\Edge\\Application\\msedge.exe"), "chromium"),
            # Thorium
            ("Thorium", os.path.join(env_local, "Thorium\\Application\\thorium.exe"), "chromium"),
            ("Thorium", os.path.join(env_prog, "Thorium\\Application\\thorium.exe"), "chromium"),
            # Opera & Opera GX
            ("Opera", os.path.join(env_local, "Programs\\Opera\\launcher.exe"), "chromium"),
            ("Opera GX", os.path.join(env_local, "Programs\\Opera GX\\launcher.exe"), "chromium"),
            # Yandex Browser
            ("Yandex Browser", os.path.join(env_local, "Yandex\\YandexBrowser\\Application\\browser.exe"), "chromium"),
            # Vivaldi
            ("Vivaldi", os.path.join(env_local, "Vivaldi\\Application\\vivaldi.exe"), "chromium"),
            ("Vivaldi", os.path.join(env_prog, "Vivaldi\\Application\\vivaldi.exe"), "chromium"),
            # Mozilla Firefox
            ("Mozilla Firefox", os.path.join(env_prog, "Mozilla Firefox\\firefox.exe"), "gecko"),
            ("Mozilla Firefox", os.path.join(env_prog86, "Mozilla Firefox\\firefox.exe"), "gecko"),
            ("Mozilla Firefox (User)", os.path.join(env_local, "Mozilla Firefox\\firefox.exe"), "gecko"),
            # LibreWolf
            ("LibreWolf", os.path.join(env_prog, "LibreWolf\\librewolf.exe"), "gecko"),
            ("LibreWolf", os.path.join(env_local, "LibreWolf\\librewolf.exe"), "gecko"),
            # Floorp & Zen
            ("Floorp", os.path.join(env_appdata, "Floorp\\floorp.exe"), "gecko"),
            ("Zen Browser", os.path.join(env_prog, "Zen Browser\\zen.exe"), "gecko"),
        ]
        for name, p, engine in candidates:
            if p and os.path.exists(p):
                found.append({"name": name, "path": p, "type": name.lower(), "engine": engine})

    else: # Linux
        candidates = [
            ("Google Chrome", "/usr/bin/google-chrome", "chromium"),
            ("Google Chrome", "/usr/bin/google-chrome-stable", "chromium"),
            ("Chromium", "/usr/bin/chromium", "chromium"),
            ("Chromium", "/usr/bin/chromium-browser", "chromium"),
            ("Brave Browser", "/usr/bin/brave-browser", "chromium"),
            ("Microsoft Edge", "/usr/bin/microsoft-edge", "chromium"),
            ("Microsoft Edge", "/usr/bin/microsoft-edge-stable", "chromium"),
            ("Thorium", "/usr/bin/thorium-browser", "chromium"),
            ("Opera", "/usr/bin/opera", "chromium"),
            ("Yandex Browser", "/usr/bin/yandex-browser", "chromium"),
            ("Vivaldi", "/usr/bin/vivaldi", "chromium"),
            ("Mozilla Firefox", "/usr/bin/firefox", "gecko"),
            ("LibreWolf", "/usr/bin/librewolf", "gecko"),
            ("Floorp", "/usr/bin/floorp", "gecko"),
            ("Zen Browser", "/usr/bin/zen-browser", "gecko"),
            # Snap packages
            ("Chromium (Snap)", "/snap/bin/chromium", "chromium"),
            ("Firefox (Snap)", "/snap/bin/firefox", "gecko"),
            ("Brave (Snap)", "/snap/bin/brave", "chromium"),
            # Flatpak packages
            ("Chromium (Flatpak)", "/var/lib/flatpak/exports/bin/org.chromium.Chromium", "chromium"),
            ("Firefox (Flatpak)", "/var/lib/flatpak/exports/bin/org.mozilla.firefox", "gecko"),
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
    Generates tailored config.json, rules.json (declarativeNetRequest), content.js, and inject.js.
    Uses /tmp on macOS to avoid macOS TCC Documents folder sandbox read restrictions.
    """
    p_id = profile.get("id", "default")
    if sys.platform == "darwin":
        runtime_ext_dir = Path("/tmp") / f"rootdetect_ext_{p_id}"
    else:
        runtime_ext_dir = target_dir / "extension"
    runtime_ext_dir.mkdir(parents=True, exist_ok=True)

    local_ext_dir = target_dir / "extension"
    local_ext_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy manifest.json & background.js
    shutil.copy(EXTENSION_SRC_DIR / "manifest.json", runtime_ext_dir / "manifest.json")
    shutil.copy(EXTENSION_SRC_DIR / "background.js", runtime_ext_dir / "background.js")

    from rootdetect.fingerprints import sanitize_fingerprint
    fp = sanitize_fingerprint(profile.get("fingerprint", {}))
    profile["fingerprint"] = fp
    proxy_info = profile.get("proxy")

    plat = fp.get("platform", "Win32")
    is_mobile = bool(fp.get("is_mobile", False))
    ua = fp.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36")
    languages = fp.get("languages", "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")
    screen_w = fp.get("screen_width", 412 if is_mobile else 1920)
    screen_h = fp.get("screen_height", 892 if is_mobile else 1080)
    scale_factor = fp.get("scale_factor", 2.625 if is_mobile else 1.0)
    max_touch = fp.get("max_touch_points", 5 if is_mobile else 0)

    # Determine platform hint for Client Hints
    if plat == "Win32" or "windows" in fp.get("os", "").lower():
        platform_hint = "Windows"
        platform_ver = "15.0.0"
        arch = "x86"
        model = ""
    elif plat == "MacIntel" or "macos" in fp.get("os", "").lower():
        platform_hint = "macOS"
        platform_ver = "15.0.0"
        arch = "arm"
        model = ""
    elif plat in ["iPhone", "iPad"] or "ios" in fp.get("os", "").lower():
        platform_hint = "iOS"
        platform_ver = "18.0.0"
        arch = "arm"
        model = "iPhone" if plat == "iPhone" else "iPad"
    elif "android" in fp.get("os", "").lower() or plat.startswith("Linux arm"):
        platform_hint = "Android"
        platform_ver = "14.0.0"
        arch = "arm"
        model = "Pixel 8 Pro" if "pixel" in ua.lower() else ("SM-S928B" if "samsung" in ua.lower() else "23116PN5BC")
    else:
        platform_hint = "Linux"
        platform_ver = "6.5.0"
        arch = "x86"
        model = ""

    # 2. Prepare config for background & inject
    config_data = {
        "seed": fp.get("seed", 42),
        "user_agent": ua,
        "platform": plat,
        "platform_hint": platform_hint,
        "os": fp.get("os", "Windows 11"),
        "languages": languages,
        "timezone": fp.get("timezone", "Europe/Moscow"),
        "webgl_vendor": fp.get("webgl_vendor"),
        "webgl_renderer": fp.get("webgl_renderer"),
        "hardware_concurrency": fp.get("hardware_concurrency", 8 if is_mobile else 16),
        "device_memory": fp.get("device_memory", 8 if is_mobile else 16),
        "max_touch_points": max_touch,
        "screen_width": screen_w,
        "screen_height": screen_h,
        "scale_factor": scale_factor,
        "is_mobile": is_mobile,
        "canvas_noise": fp.get("canvas_noise", True),
        "audio_noise": fp.get("audio_noise", True),
        "proxy_auth": {
            "username": proxy_info.get("username"),
            "password": proxy_info.get("password")
        } if proxy_info and proxy_info.get("username") else None
    }

    with open(runtime_ext_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    # 3. Create declarativeNetRequest rules.json for network header spoofing
    is_ios = (platform_hint == "iOS" or plat in ["iPhone", "iPad"] or "ios" in fp.get("os", "").lower())
    if is_ios:
        req_headers = [
            { "header": "sec-ch-ua", "operation": "remove" },
            { "header": "sec-ch-ua-mobile", "operation": "remove" },
            { "header": "sec-ch-ua-platform", "operation": "remove" },
            { "header": "sec-ch-ua-platform-version", "operation": "remove" },
            { "header": "sec-ch-ua-arch", "operation": "remove" },
            { "header": "sec-ch-ua-bitness", "operation": "remove" },
            { "header": "sec-ch-ua-model", "operation": "remove" },
            { "header": "sec-ch-ua-full-version-list", "operation": "remove" },
            { "header": "User-Agent", "operation": "set", "value": ua },
            { "header": "Accept-Language", "operation": "set", "value": languages }
        ]
    else:
        req_headers = [
            { "header": "sec-ch-ua-platform", "operation": "set", "value": f'"{platform_hint}"' },
            { "header": "sec-ch-ua-platform-version", "operation": "set", "value": f'"{platform_ver}"' },
            { "header": "sec-ch-ua-arch", "operation": "set", "value": f'"{arch}"' },
            { "header": "sec-ch-ua-bitness", "operation": "set", "value": '"64"' },
            { "header": "sec-ch-ua-mobile", "operation": "set", "value": "?1" if is_mobile else "?0" },
            { "header": "sec-ch-ua-model", "operation": "set", "value": f'"{model}"' },
            { "header": "sec-ch-ua", "operation": "set", "value": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' },
            { "header": "User-Agent", "operation": "set", "value": ua },
            { "header": "Accept-Language", "operation": "set", "value": languages }
        ]

    rules = [
        {
            "id": 1,
            "priority": 1,
            "action": {
                "type": "modifyHeaders",
                "requestHeaders": req_headers
            },
            "condition": {
                "urlFilter": "*",
                "resourceTypes": [
                    "main_frame", "sub_frame", "stylesheet", "script", "image", "font", "object", "xmlhttprequest", "ping", "media", "websocket", "other"
                ]
            }
        }
    ]

    with open(runtime_ext_dir / "rules.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

    # 4. Create customized inject.js with config baked in
    with open(EXTENSION_SRC_DIR / "inject.js", "r", encoding="utf-8") as f:
        inject_base = f.read()

    import re
    cfg_json_str = json.dumps(config_data, ensure_ascii=False, indent=8)
    full_stealth_code = re.sub(
        r'const cfg = window\.__ROOT_DETECT_CONFIG__ \|\| \{[\s\S]*?\n    \};',
        f'const cfg = {cfg_json_str};',
        inject_base,
        count=1
    )
    with open(runtime_ext_dir / "inject.js", "w", encoding="utf-8") as f:
        f.write(full_stealth_code)

    # 5. Copy content.js and icons
    shutil.copy(EXTENSION_SRC_DIR / "content.js", runtime_ext_dir / "content.js")
    icons_src = EXTENSION_SRC_DIR / "icons"
    if icons_src.exists():
        shutil.copytree(icons_src, runtime_ext_dir / "icons", dirs_exist_ok=True)

    # Sync to local folder as well
    if runtime_ext_dir != local_ext_dir:
        shutil.copytree(runtime_ext_dir, local_ext_dir, dirs_exist_ok=True)

    try:
        for ext_d in [runtime_ext_dir, local_ext_dir]:
            for root, dirs, files in os.walk(str(ext_d)):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
    except Exception:
        pass

    return runtime_ext_dir



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
    
    # Clean up stale Chromium singleton locks and invalid Secure Preferences to prevent corruption alerts
    for s_file in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        try:
            (user_data_path / s_file).unlink(missing_ok=True)
        except Exception:
            pass

    sec_prefs = user_data_path / "Default" / "Secure Preferences"
    if sec_prefs.exists():
        try:
            sec_prefs.unlink(missing_ok=True)
        except Exception:
            pass

    fp = profile.get("fingerprint", {})
    proxy = profile.get("proxy")
    is_mobile = bool(fp.get("is_mobile", False))

    # Default startup URLs: 1. IP / WebRTC check, 2. JavaScript / Fingerprint check
    default_urls = ["https://browserleaks.com/ip", "https://browserleaks.com/javascript"]
    target_urls = [custom_url] if custom_url else default_urls

    if is_gecko_browser(browser_path):
        # --- GECKO / FIREFOX ENGINE LAUNCH ---
        prepare_firefox_profile(profile, user_data_path)
        flags = [
            browser_path,
            "-no-remote",
            "-profile",
            str(user_data_path.resolve())
        ] + target_urls
    else:
        # --- CHROMIUM ENGINE LAUNCH ---
        profile_base_dir = user_data_path.parent
        ext_dir = prepare_profile_extension(profile, profile_base_dir)

        flags = [
            browser_path,
            f"--user-data-dir={str(user_data_path.resolve())}",
            f"--disable-extensions-except={str(ext_dir.resolve())}",
            f"--load-extension={str(ext_dir.resolve())}",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--test-type",
            "--hide-crash-restore-bubble",
            "--disable-session-crashed-bubble",
            "--disable-features=Translate,ChromeForTestingAlert,OSCryptAsync",
            "--no-first-run",
            "--no-default-browser-check",
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-component-update",
            "--disable-sync",
            "--metrics-recording-only",
            "--enable-extension-developer-mode",
            "--force-webrtc-ip-handling-policy=disable_non_proxied_udp"
        ]

        if is_mobile:
            screen_w = fp.get("screen_width", 412)
            screen_h = fp.get("screen_height", 892)
            scale = fp.get("scale_factor", 2.625)
            flags.extend([
                f"--window-size={screen_w},{screen_h}",
                "--touch-events=enabled",
                "--enable-touch-drag-drop",
                f"--force-device-scale-factor={scale}",
                "--enable-viewport",
                "--use-mobile-user-agent"
            ])
        else:
            screen_w = fp.get("screen_width", 1920)
            screen_h = fp.get("screen_height", 1080)
            flags.append(f"--window-size={screen_w},{screen_h}")

        if fp.get("user_agent"):
            flags.append(f"--user-agent={fp['user_agent']}")

        primary_lang = "en-US"
        if fp.get("languages"):
            primary_lang = fp["languages"].split(",")[0].split(";")[0]
            flags.append(f"--lang={primary_lang}")
            flags.append(f"--accept-lang={fp['languages']}")

        if proxy and proxy.get("chrome_arg"):
            flags.append(f"--proxy-server={proxy['chrome_arg']}")

        flags.extend(target_urls)

    # Prepare environment variables with spoofed Timezone & Locale
    proc_env = os.environ.copy()
    if fp.get("timezone"):
        proc_env["TZ"] = fp["timezone"]
    if fp.get("languages"):
        primary_lang = fp["languages"].split(",")[0].split(";")[0]
        proc_env["LANG"] = f"{primary_lang.replace('-', '_')}.UTF-8"
        proc_env["LC_ALL"] = f"{primary_lang.replace('-', '_')}.UTF-8"

    try:
        if platform.system().lower() == "windows":
            subprocess.Popen(
                flags,
                env=proc_env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                close_fds=True
            )
        elif platform.system().lower() == "darwin":
            app_bundle = None
            p_obj = Path(browser_path)
            for parent in [p_obj] + list(p_obj.parents):
                if parent.name.endswith(".app"):
                    app_bundle = str(parent.resolve())
                    break

            launched = False
            if app_bundle:
                try:
                    open_cmd = ["open", "-n", "-a", app_bundle, "--args"] + flags[1:]
                    res = subprocess.run(open_cmd, env=proc_env, capture_output=True, text=True)
                    if res.returncode == 0:
                        launched = True
                except Exception:
                    pass

            if not launched:
                subprocess.Popen(
                    flags,
                    env=proc_env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )
        else: # Linux
            subprocess.Popen(
                flags,
                env=proc_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        return True, "Браузер успешно запущен"
    except Exception as e:
        return False, f"Ошибка при запуске браузера: {str(e)}"

