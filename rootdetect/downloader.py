"""
Multi-browser downloader and portable browser catalog for Root Detect.
Supports Chrome for Testing, Ungoogled Chromium, Brave, Thorium, Firefox, and LibreWolf.
"""

import os
import sys
import json
import shutil
import zipfile
import tarfile
import platform
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable

try:
    from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
    from rich.console import Console
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

CFT_API_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

AVAILABLE_BROWSERS = [
    {
        "id": "chrome_cft",
        "name": "Google Chrome (Testing)",
        "engine": "chromium",
        "desc": "Официальный чистый портативный билд от Google без привязки к аккаунту"
    },
    {
        "id": "ungoogled",
        "name": "Ungoogled Chromium",
        "engine": "chromium",
        "desc": "Максимальная приватность: вырезаны фоновые сервисы и телеметрия Google"
    }
]

def get_browsers_storage_dir() -> Path:
    """Returns directory for storing downloaded portable browsers."""
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent.parent
    local_base = app_dir / "profiles_data" / "browsers"
    try:
        local_base.mkdir(parents=True, exist_ok=True)
        return local_base
    except (PermissionError, OSError):
        pass
    base = Path.home() / ".rootdetect" / "browsers"
    base.mkdir(parents=True, exist_ok=True)
    return base

def get_platform_key() -> Optional[str]:
    """Determines platform identifier (mac-arm64, mac-x64, win64, linux64)."""
    system = platform.system().lower()
    arch = platform.machine().lower()

    if "darwin" in system:
        if "arm" in arch or "aarch64" in arch:
            return "mac-arm64"
        return "mac-x64"
    elif "windows" in system:
        if "64" in arch or "amd64" in arch:
            return "win64"
        return "win32"
    elif "linux" in system:
        return "linux64"
    return None

def fetch_chrome_cft_info() -> Optional[Dict[str, str]]:
    plat_key = get_platform_key()
    if not plat_key:
        return None

    try:
        req = urllib.request.Request(CFT_API_URL, headers={"User-Agent": "RootDetect/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            stable = data.get("channels", {}).get("Stable", {})
            version = stable.get("version", "latest")
            downloads = stable.get("downloads", {}).get("chrome", [])
            for item in downloads:
                if item.get("platform") == plat_key:
                    return {
                        "id": "chrome_cft",
                        "name": "Google Chrome (Testing)",
                        "version": version,
                        "platform": plat_key,
                        "url": item.get("url"),
                        "archive_type": "zip"
                    }
    except Exception:
        pass

    fallback_urls = {
        "mac-arm64": "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.86/mac-arm64/chrome-mac-arm64.zip",
        "mac-x64": "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.86/mac-x64/chrome-mac-x64.zip",
        "win64": "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.86/win64/chrome-win64.zip",
        "linux64": "https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.86/linux64/chrome-linux64.zip"
    }
    if plat_key in fallback_urls:
        return {
            "id": "chrome_cft",
            "name": "Google Chrome (Testing)",
            "version": "131.0.6778.86",
            "platform": plat_key,
            "url": fallback_urls[plat_key],
            "archive_type": "zip"
        }
    return None

def fetch_ungoogled_info() -> Optional[Dict[str, str]]:
    plat_key = get_platform_key()
    urls = {
        "mac-arm64": {
            "url": "https://github.com/ungoogled-software/ungoogled-chromium-macos/releases/download/130.0.6723.69-1.1/ungoogled-chromium_130.0.6723.69-1.1_arm64-macos.dmg",
            "version": "130.0.6723.69",
            "archive_type": "dmg"
        },
        "mac-x64": {
            "url": "https://github.com/ungoogled-software/ungoogled-chromium-macos/releases/download/130.0.6723.69-1.1/ungoogled-chromium_130.0.6723.69-1.1_x86-64-macos.dmg",
            "version": "130.0.6723.69",
            "archive_type": "dmg"
        },
        "win64": {
            "url": "https://github.com/ungoogled-software/ungoogled-chromium-windows/releases/download/130.0.6723.69-1.1/ungoogled-chromium_130.0.6723.69-1.1_windows_x64.zip",
            "version": "130.0.6723.69",
            "archive_type": "zip"
        },
        "linux64": {
            "url": "https://github.com/ungoogled-software/ungoogled-chromium-portablelinux/releases/download/130.0.6723.69-1/ungoogled-chromium_130.0.6723.69-1_linux.tar.xz",
            "version": "130.0.6723.69",
            "archive_type": "tar"
        }
    }
    if plat_key in urls:
        item = urls[plat_key]
        return {
            "id": "ungoogled",
            "name": "Ungoogled Chromium",
            "version": item["version"],
            "platform": plat_key,
            "url": item["url"],
            "archive_type": item["archive_type"]
        }
    return None

def fetch_brave_info() -> Optional[Dict[str, str]]:
    plat_key = get_platform_key()
    urls = {
        "mac-arm64": {
            "url": "https://github.com/brave/brave-browser/releases/download/v1.73.97/Brave-Browser-arm64.dmg",
            "version": "1.73.97",
            "archive_type": "dmg"
        },
        "mac-x64": {
            "url": "https://github.com/brave/brave-browser/releases/download/v1.73.97/Brave-Browser-x64.dmg",
            "version": "1.73.97",
            "archive_type": "dmg"
        },
        "win64": {
            "url": "https://github.com/brave/brave-browser/releases/download/v1.73.97/BraveBrowserStandaloneSetup.exe",
            "version": "1.73.97",
            "archive_type": "exe"
        },
        "linux64": {
            "url": "https://github.com/brave/brave-browser/releases/download/v1.73.97/brave-browser-1.73.97-linux-amd64.zip",
            "version": "1.73.97",
            "archive_type": "zip"
        }
    }
    if plat_key in urls:
        item = urls[plat_key]
        return {
            "id": "brave",
            "name": "Brave Browser",
            "version": item["version"],
            "platform": plat_key,
            "url": item["url"],
            "archive_type": item["archive_type"]
        }
    return None

def fetch_thorium_info() -> Optional[Dict[str, str]]:
    plat_key = get_platform_key()
    urls = {
        "mac-arm64": {
            "url": "https://github.com/Alex313031/Thorium-MacOS/releases/download/M124.0.6367.208/Thorium_MacOS_ARM64.dmg",
            "version": "124.0.6367.208",
            "archive_type": "dmg"
        },
        "mac-x64": {
            "url": "https://github.com/Alex313031/Thorium-MacOS/releases/download/M124.0.6367.208/Thorium_MacOS_X64.dmg",
            "version": "124.0.6367.208",
            "archive_type": "dmg"
        },
        "win64": {
            "url": "https://github.com/Alex313031/Thorium-Win/releases/download/M124.0.6367.208/Thorium_AVX2.zip",
            "version": "124.0.6367.208",
            "archive_type": "zip"
        },
        "linux64": {
            "url": "https://github.com/Alex313031/Thorium/releases/download/M124.0.6367.208/Thorium_Browser_124.0.6367.208_AVX2.AppImage",
            "version": "124.0.6367.208",
            "archive_type": "appimage"
        }
    }
    if plat_key in urls:
        item = urls[plat_key]
        return {
            "id": "thorium",
            "name": "Thorium Browser",
            "version": item["version"],
            "platform": plat_key,
            "url": item["url"],
            "archive_type": item["archive_type"]
        }
    return None

def fetch_firefox_info() -> Optional[Dict[str, str]]:
    plat_key = get_platform_key()
    urls = {
        "mac-arm64": {
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=osx&lang=en-US",
            "version": "latest",
            "archive_type": "dmg"
        },
        "mac-x64": {
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=osx&lang=en-US",
            "version": "latest",
            "archive_type": "dmg"
        },
        "win64": {
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US",
            "version": "latest",
            "archive_type": "exe"
        },
        "linux64": {
            "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US",
            "version": "latest",
            "archive_type": "tar"
        }
    }
    if plat_key in urls:
        item = urls[plat_key]
        return {
            "id": "firefox",
            "name": "Mozilla Firefox",
            "version": item["version"],
            "platform": plat_key,
            "url": item["url"],
            "archive_type": item["archive_type"]
        }
    return None

def fetch_librewolf_info() -> Optional[Dict[str, str]]:
    plat_key = get_platform_key()
    urls = {
        "mac-arm64": {
            "url": "https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/latest/LibreWolf.arm64.dmg",
            "version": "latest",
            "archive_type": "dmg"
        },
        "mac-x64": {
            "url": "https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/latest/LibreWolf.x86_64.dmg",
            "version": "latest",
            "archive_type": "dmg"
        },
        "win64": {
            "url": "https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/latest/librewolf-win64-portable.zip",
            "version": "latest",
            "archive_type": "zip"
        },
        "linux64": {
            "url": "https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/latest/LibreWolf.x86_64.AppImage",
            "version": "latest",
            "archive_type": "appimage"
        }
    }
    if plat_key in urls:
        item = urls[plat_key]
        return {
            "id": "librewolf",
            "name": "LibreWolf (Firefox Privacy)",
            "version": item["version"],
            "platform": plat_key,
            "url": item["url"],
            "archive_type": item["archive_type"]
        }
    return None

def get_browser_download_info(browser_id: str) -> Optional[Dict[str, str]]:
    if browser_id == "chrome_cft":
        return fetch_chrome_cft_info()
    elif browser_id == "ungoogled":
        return fetch_ungoogled_info()
    elif browser_id == "brave":
        return fetch_brave_info()
    elif browser_id == "thorium":
        return fetch_thorium_info()
    elif browser_id == "firefox":
        return fetch_firefox_info()
    elif browser_id == "librewolf":
        return fetch_librewolf_info()
    return None

def find_downloaded_browsers() -> List[Dict[str, str]]:
    """Lists already downloaded portable browsers in storage directory."""
    browsers_dir = get_browsers_storage_dir()
    found = []
    try:
        if not browsers_dir.exists():
            return found

        for item in browsers_dir.iterdir():
            if item.is_dir():
                bin_path = _locate_binary_in_folder(item)
                if bin_path:
                    engine = "gecko" if ("firefox" in item.name.lower() or "librewolf" in item.name.lower()) else "chromium"
                    found.append({
                        "name": f"{item.name}",
                        "path": str(bin_path.resolve()),
                        "type": "portable",
                        "engine": engine,
                        "folder": str(item.resolve())
                    })
    except (PermissionError, OSError):
        pass
    return found

def _locate_binary_in_folder(folder: Path) -> Optional[Path]:
    system = platform.system().lower()
    
    if "darwin" in system:
        candidates = list(folder.glob("**/*.app/Contents/MacOS/*"))
        for cand in candidates:
            if cand.is_file() and os.access(cand, os.X_OK):
                return cand
            elif cand.is_file():
                try:
                    os.chmod(cand, 0o755)
                    return cand
                except Exception:
                    pass
        
        for name in ["chrome", "chromium", "brave", "thorium", "firefox", "librewolf"]:
            raws = list(folder.glob(f"**/{name}"))
            if raws and os.access(raws[0], os.X_OK):
                return raws[0]

    elif "windows" in system or sys.platform == "win32":
        preferred = ["rootdetectbrowser.exe", "root detect.exe", "rootdetect.exe", "chrome.exe", "chromium.exe", "brave.exe", "thorium.exe", "firefox.exe", "librewolf.exe"]
        for p in preferred:
            for cand in folder.rglob("*.exe"):
                if cand.is_file() and cand.name.lower() == p:
                    return cand
        for cand in folder.rglob("*.exe"):
            if cand.is_file() and not cand.name.lower().startswith(("setup", "install", "update", "crash", "notification", "elevation")):
                return cand
    else: # Linux
        for cand in folder.glob("**/*"):
            if cand.is_file() and os.access(cand, os.X_OK) and not cand.name.endswith(('.so', '.json', '.pak', '.bin')):
                return cand

    return None

def download_browser(browser_id: str = "chrome_cft") -> Optional[str]:
    """
    Downloads, unpacks, and prepares chosen portable browser.
    Returns executable path or None.
    """
    info = get_browser_download_info(browser_id)
    if not info:
        return None

    url = info["url"]
    version = info["version"]
    plat = info["platform"]
    archive_type = info["archive_type"]
    b_name = info["name"]

    browsers_dir = get_browsers_storage_dir()
    target_folder = browsers_dir / f"{browser_id}-{version}"
    
    existing_bin = _locate_binary_in_folder(target_folder)
    if existing_bin:
        return str(existing_bin.resolve())

    temp_file = browsers_dir / f"temp_download_{browser_id}.{archive_type}"

    # Download with progress
    if HAVE_RICH:
        console = Console()
        console.print(f"[dim]• Загрузка {b_name}...[/dim]")
        with Progress(
            TextColumn("[dim]{task.description}[/dim]"),
            BarColumn(complete_style="white", finished_style="green"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            transient=True
        ) as progress:
            task = progress.add_task("Загрузка", total=None)

            def update_bar(blocks_count, block_size, total_size):
                if total_size > 0:
                    progress.update(task, total=total_size, completed=blocks_count * block_size)

            req = urllib.request.Request(url, headers={"User-Agent": "RootDetect/1.0"})
            with urllib.request.urlopen(req) as resp, open(temp_file, 'wb') as out_f:
                total_size = int(resp.headers.get('Content-Length', 0))
                downloaded = 0
                block_size = 65536
                while True:
                    chunk = resp.read(block_size)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress.update(task, total=total_size, completed=downloaded)
    else:
        print(f"• Загрузка {b_name}...")
        urllib.request.urlretrieve(url, str(temp_file))

    # Extraction
    if HAVE_RICH:
        console = Console()
        console.print("[dim]• Распаковка и подготовка браузера...[/dim]")
    else:
        print("• Распаковка и подготовка браузера...")

    target_folder.mkdir(parents=True, exist_ok=True)

    try:
        if archive_type == "zip":
            with zipfile.ZipFile(temp_file, "r") as zf:
                zf.extractall(target_folder)
        elif archive_type in ["tar", "tar.gz", "tar.xz", "tar.bz2"]:
            with tarfile.open(temp_file, "r:*") as tf:
                tf.extractall(target_folder)
        elif archive_type == "dmg" and sys.platform == "darwin":
            mount_point = browsers_dir / "dmg_mount"
            mount_point.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["hdiutil", "attach", str(temp_file), "-mountpoint", str(mount_point), "-nobrowse", "-quiet", "-readonly"],
                check=True
            )
            try:
                for app in mount_point.glob("*.app"):
                    dest_app = target_folder / app.name
                    if dest_app.exists():
                        shutil.rmtree(dest_app)
                    shutil.copytree(app, dest_app)
            finally:
                subprocess.run(["hdiutil", "detach", str(mount_point), "-quiet"], check=False)
                if mount_point.exists():
                    shutil.rmtree(mount_point, ignore_errors=True)
        elif archive_type == "appimage":
            target_bin = target_folder / f"{browser_id}.AppImage"
            shutil.copy(temp_file, target_bin)
            os.chmod(target_bin, 0o755)
    except Exception as e:
        if HAVE_RICH:
            Console().print(f"[red]• Ошибка при распаковке: {e}[/red]")
        return None
    finally:
        if temp_file.exists():
            temp_file.unlink()

    # Pre-configure portable Chromium with master preferences & icons
    if getattr(sys, '_MEIPASS', None):
        assets_dir = Path(sys._MEIPASS) / "rootdetect" / "assets"
    else:
        assets_dir = Path(__file__).parent / "assets"

    # 1. Copy app.ico
    ico_src = assets_dir / "app.ico"
    if ico_src.exists():
        try:
            shutil.copy(ico_src, target_folder / "app.ico")
        except Exception:
            pass

    # 2. Configure initial_preferences / master_preferences for clean stealth startup
    init_prefs = {
        "distribution": {
            "skip_first_run_ui": True,
            "show_welcome_page": False,
            "import_bookmarks": False,
            "import_history": False,
            "import_search_engine": False,
            "import_saved_passwords": False,
            "do_not_create_desktop_shortcut": True,
            "do_not_create_quick_launch_shortcut": True,
            "do_not_register_for_update_launch": True,
            "make_chrome_default": False,
            "make_chrome_default_for_user": False,
            "suppress_first_run_bubble": True,
            "suppress_first_run_default_browser_prompt": True
        }
    }
    for sub in [target_folder] + [d for d in target_folder.iterdir() if d.is_dir()]:
        for pref_name in ["initial_preferences", "master_preferences"]:
            try:
                with open(sub / pref_name, "w", encoding="utf-8") as pf:
                    json.dump(init_prefs, pf, indent=2)
            except Exception:
                pass

    if sys.platform == "win32" or "windows" in platform.system().lower():
        try:
            for exe_file in list(target_folder.rglob("chrome.exe")):
                rd_exe = exe_file.parent / "RootDetectBrowser.exe"
                if not rd_exe.exists():
                    shutil.copy2(exe_file, rd_exe)
        except Exception:
            pass

    if sys.platform == "darwin":
        try:
            subprocess.run(["chmod", "-R", "+x", str(target_folder.resolve())], check=False)
            subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(target_folder.resolve())], check=False)
            
            # 1. Rename any Chromium / Google Chrome app bundles to "Root Detect.app"
            for old_app in list(target_folder.glob("**/*.app")):
                if "chrome" in old_app.name.lower() or "chromium" in old_app.name.lower():
                    new_app = old_app.parent / "Root Detect.app"
                    if not new_app.exists():
                        old_app.rename(new_app)

            icns_src = assets_dir / "app.icns"
            
            for app_dir in target_folder.glob("**/*.app"):
                # 2. Rename executable inside MacOS/
                macos_dir = app_dir / "Contents" / "MacOS"
                if macos_dir.is_dir():
                    for exe_file in macos_dir.iterdir():
                        if exe_file.is_file() and exe_file.name != "Root Detect" and not exe_file.name.endswith(".dylib"):
                            new_exe = macos_dir / "Root Detect"
                            exe_file.rename(new_exe)
                            os.chmod(new_exe, 0o755)
                            break

                # 3. Patch Info.plist
                plist_file = app_dir / "Contents" / "Info.plist"
                if plist_file.is_file():
                    import plistlib
                    try:
                        with open(plist_file, "rb") as f:
                            pl = plistlib.load(f)
                        pl["CFBundleDisplayName"] = "Root Detect"
                        pl["CFBundleName"] = "Root Detect"
                        pl["CFBundleExecutable"] = "Root Detect"
                        pl["CFBundleIconFile"] = "app.icns"
                        if "CFBundleIconName" in pl:
                            del pl["CFBundleIconName"]
                        pl["LSHasLocalizedDisplayName"] = False
                        with open(plist_file, "wb") as f:
                            plistlib.dump(pl, f)
                    except Exception:
                        pass

                # 4. Remove Assets.car to force icon loading from app.icns
                for car in app_dir.glob("**/Assets.car"):
                    try:
                        car.unlink()
                    except Exception:
                        pass

                # 5. Copy app.icns
                if icns_src.exists():
                    for r_dir in [app_dir / "Contents" / "Resources"] + list(app_dir.glob("**/Contents/Resources")):
                        if r_dir.is_dir():
                            try:
                                shutil.copy(icns_src, r_dir / "app.icns")
                            except Exception:
                                pass

                # 6. Update InfoPlist.strings in all language bundles
                for strings_file in app_dir.glob("**/InfoPlist.strings"):
                    try:
                        with open(strings_file, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        lines = [l for l in content.splitlines() if not l.startswith("CFBundleDisplayName") and not l.startswith("CFBundleName")]
                        lines.insert(0, 'CFBundleDisplayName = "Root Detect";')
                        lines.insert(1, 'CFBundleName = "Root Detect";')
                        with open(strings_file, "w", encoding="utf-8") as f:
                            f.write("\n".join(lines) + "\n")
                    except Exception:
                        pass

                # 7. Strip extended attributes without following symlinks and ad-hoc sign
                subprocess.run(["xattr", "-rcs", str(app_dir.resolve())], check=False)
                subprocess.run(["codesign", "--force", "--deep", "-s", "-", str(app_dir.resolve())], check=False)
                
                # 8. Register with LaunchServices
                lsregister = "/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister"
                if os.path.exists(lsregister):
                    subprocess.run([lsregister, "-f", "-R", "-trusted", str(app_dir.resolve())], check=False)
                subprocess.run(["touch", str(app_dir.resolve())], check=False)
        except Exception:
            pass

    bin_path = _locate_binary_in_folder(target_folder)
    if bin_path:
        try:
            os.chmod(bin_path, 0o755)
        except Exception:
            pass
        return str(bin_path.resolve())

    return None

def download_chromium() -> Optional[str]:
    return download_browser("chrome_cft")

