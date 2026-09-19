"""
Comprehensive fingerprint generator and device presets for Root Detect.
Supports Windows (11, 10, 8.1, 7), macOS (Sequoia, Sonoma, Ventura),
iOS (iPhone 16/15, iPad), Android (Samsung S24, Pixel 8, Xiaomi 14), and Linux.
"""

import random
import time
from typing import Dict, Any, Optional, List, Tuple

CHROME_VER = "131.0.6778.86"

OS_PRESETS = {
    "windows_11": {
        "name": "Windows 11",
        "category": "desktop",
        "platform": "Win32",
        "ua": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "windows",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "windows_10": {
        "name": "Windows 10",
        "category": "desktop",
        "platform": "Win32",
        "ua": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "windows",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "windows_8_1": {
        "name": "Windows 8.1",
        "category": "desktop",
        "platform": "Win32",
        "ua": f"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "windows_legacy",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "windows_7": {
        "name": "Windows 7",
        "category": "desktop",
        "platform": "Win32",
        "ua": f"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36",
        "default_gpu_category": "windows_legacy",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "macos_15": {
        "name": "macOS 15 (Sequoia)",
        "category": "desktop",
        "platform": "MacIntel",
        "ua": f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "macos_apple_silicon",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "macos_14": {
        "name": "macOS 14 (Sonoma)",
        "category": "desktop",
        "platform": "MacIntel",
        "ua": f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "macos_apple_silicon",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "macos_13": {
        "name": "macOS 13 (Ventura)",
        "category": "desktop",
        "platform": "MacIntel",
        "ua": f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "macos_intel",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    },
    "ios_iphone_16": {
        "name": "iOS (iPhone 16 Pro)",
        "category": "mobile",
        "platform": "iPhone",
        "ua": f"Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{CHROME_VER} Mobile/15E148 Safari/604.1",
        "default_gpu_category": "ios",
        "is_mobile": True,
        "touch": True,
        "max_touch_points": 5,
        "default_res": (393, 852),
        "scale_factor": 3.0
    },
    "ios_iphone_15": {
        "name": "iOS (iPhone 15 Pro Max)",
        "category": "mobile",
        "platform": "iPhone",
        "ua": f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{CHROME_VER} Mobile/15E148 Safari/604.1",
        "default_gpu_category": "ios",
        "is_mobile": True,
        "touch": True,
        "max_touch_points": 5,
        "default_res": (430, 932),
        "scale_factor": 3.0
    },
    "ios_ipad_pro": {
        "name": "iPadOS (iPad Pro 12.9)",
        "category": "mobile",
        "platform": "iPad",
        "ua": f"Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{CHROME_VER} Mobile/15E148 Safari/604.1",
        "default_gpu_category": "ios",
        "is_mobile": True,
        "touch": True,
        "max_touch_points": 5,
        "default_res": (1024, 1366),
        "scale_factor": 2.0
    },
    "android_samsung_s24": {
        "name": "Android (Samsung Galaxy S24 Ultra)",
        "category": "mobile",
        "platform": "Linux armv8l",
        "ua": f"Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Mobile Safari/537.36",
        "default_gpu_category": "android_adreno",
        "is_mobile": True,
        "touch": True,
        "max_touch_points": 5,
        "default_res": (412, 915),
        "scale_factor": 3.0
    },
    "android_pixel_8": {
        "name": "Android (Google Pixel 8 Pro)",
        "category": "mobile",
        "platform": "Linux armv8l",
        "ua": f"Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Mobile Safari/537.36",
        "default_gpu_category": "android_mali",
        "is_mobile": True,
        "touch": True,
        "max_touch_points": 5,
        "default_res": (412, 892),
        "scale_factor": 2.625
    },
    "android_xiaomi_14": {
        "name": "Android (Xiaomi 14 Pro)",
        "category": "mobile",
        "platform": "Linux armv8l",
        "ua": f"Mozilla/5.0 (Linux; Android 14; 23116PN5BC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Mobile Safari/537.36",
        "default_gpu_category": "android_adreno",
        "is_mobile": True,
        "touch": True,
        "max_touch_points": 5,
        "default_res": (393, 873),
        "scale_factor": 3.0
    },
    "linux": {
        "name": "Linux (Ubuntu / Debian x86_64)",
        "category": "desktop",
        "platform": "Linux x86_64",
        "ua": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VER} Safari/537.36",
        "default_gpu_category": "linux",
        "is_mobile": False,
        "touch": False,
        "max_touch_points": 0
    }
}

GPU_PRESETS = {
    "windows": [
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 7900 XTX Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"}
    ],
    "windows_legacy": [
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11)"},
        {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D11 vs_5_0 ps_5_0, D3D11)"}
    ],
    "macos_apple_silicon": [
        {"vendor": "Google Inc. (Apple)", "renderer": "ANGLE (Apple, ANGLE Metal Renderer: Apple M3 Max, Version 15.0)"},
        {"vendor": "Google Inc. (Apple)", "renderer": "ANGLE (Apple, ANGLE Metal Renderer: Apple M3 Pro, Version 14.5)"},
        {"vendor": "Google Inc. (Apple)", "renderer": "ANGLE (Apple, ANGLE Metal Renderer: Apple M2 Pro, Version 14.2)"},
        {"vendor": "Google Inc. (Apple)", "renderer": "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Version 13.6)"}
    ],
    "macos_intel": [
        {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) Iris(R) Plus Graphics 655, OpenGL 4.1)"},
        {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon Pro 5500M, OpenGL 4.1)"}
    ],
    "ios": [
        {"vendor": "Apple Inc.", "renderer": "Apple GPU"},
        {"vendor": "Apple Inc.", "renderer": "Apple A17 Pro GPU"},
        {"vendor": "Apple Inc.", "renderer": "Apple A16 Bionic GPU"}
    ],
    "android_adreno": [
        {"vendor": "Qualcomm", "renderer": "Adreno (TM) 750"},
        {"vendor": "Qualcomm", "renderer": "Adreno (TM) 740"},
        {"vendor": "Qualcomm", "renderer": "Adreno (TM) 730"}
    ],
    "android_mali": [
        {"vendor": "ARM", "renderer": "Mali-G720 Immortalis"},
        {"vendor": "ARM", "renderer": "Mali-G715-Immortalis MC11"},
        {"vendor": "ARM", "renderer": "Mali-G78 MP14"}
    ],
    "linux": [
        {"vendor": "Google Inc. (NVIDIA Corporation)", "renderer": "ANGLE (NVIDIA Corporation, NVIDIA GeForce RTX 4070/PCIe/SSE2, OpenGL 4.5.0)"},
        {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 6700 XT, OpenGL 4.6)"}
    ]
}

DESKTOP_RESOLUTIONS = [
    (1920, 1080),
    (2560, 1440),
    (1920, 1200),
    (1680, 1050),
    (1536, 864),
    (1440, 900),
    (3840, 2160)
]

LOCALES = [
    {"lang": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "tz": "Europe/Moscow"},
    {"lang": "en-US,en;q=0.9", "tz": "America/New_York"},
    {"lang": "en-US,en;q=0.9", "tz": "America/Los_Angeles"},
    {"lang": "en-GB,en;q=0.9", "tz": "Europe/London"},
    {"lang": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7", "tz": "Europe/Berlin"},
    {"lang": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7", "tz": "Europe/Kyiv"},
    {"lang": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7", "tz": "Europe/Paris"}
]

def generate_fingerprint_for_preset(
    preset_key: str = "windows_11",
    custom_gpu: Optional[Dict[str, str]] = None,
    custom_res: Optional[Tuple[int, int]] = None,
    custom_cores: Optional[int] = None,
    custom_memory: Optional[int] = None,
    custom_lang: Optional[str] = None,
    custom_tz: Optional[str] = None
) -> Dict[str, Any]:
    """Generates a complete fingerprint according to selected OS/device preset."""
    if preset_key not in OS_PRESETS:
        preset_key = "windows_11"

    os_info = OS_PRESETS[preset_key]
    gpu_cat = os_info.get("default_gpu_category", "windows")
    gpu_pool = GPU_PRESETS.get(gpu_cat, GPU_PRESETS["windows"])
    
    gpu = custom_gpu or random.choice(gpu_pool)

    # Resolution
    if custom_res:
        res_w, res_h = custom_res
    elif os_info.get("default_res"):
        res_w, res_h = os_info["default_res"]
    else:
        res_w, res_h = random.choice(DESKTOP_RESOLUTIONS)

    # Cores and memory
    if preset_key.startswith("ios_"):
        cores = 8 if preset_key == "ios_ipad_pro" else 6
        memory = None  # WebKit on iOS does not expose deviceMemory
    elif os_info.get("is_mobile"):
        cores = custom_cores or random.choice([6, 8])
        memory = custom_memory or random.choice([6, 8, 12])
    else:
        cores = custom_cores or random.choice([6, 8, 12, 16, 24])
        memory = custom_memory or random.choice([8, 16, 32, 64])

    locale_cfg = random.choice(LOCALES)
    lang = custom_lang or locale_cfg["lang"]
    tz = custom_tz or locale_cfg["tz"]
    seed = int(time.time() * 1000) % 1000000 + random.randint(100, 99999)

    return {
        "preset_key": preset_key,
        "os": os_info["name"],
        "category": os_info["category"],
        "platform": os_info["platform"],
        "user_agent": os_info["ua"],
        "webgl_vendor": gpu["vendor"],
        "webgl_renderer": gpu["renderer"],
        "screen_width": res_w,
        "screen_height": res_h,
        "scale_factor": os_info.get("scale_factor", 1.0),
        "hardware_concurrency": cores,
        "device_memory": memory,
        "languages": lang,
        "timezone": tz,
        "is_mobile": os_info.get("is_mobile", False),
        "touch": os_info.get("touch", False),
        "max_touch_points": os_info.get("max_touch_points", 0),
        "seed": seed,
        "canvas_noise": True,
        "audio_noise": True
    }

def generate_random_fingerprint(os_type: Optional[str] = None) -> Dict[str, Any]:
    """Compatibility wrapper for random fingerprint generation."""
    if not os_type or os_type == "auto":
        preset_key = random.choice(["windows_11", "macos_15", "macos_14", "windows_10"])
    elif os_type in OS_PRESETS:
        preset_key = os_type
    elif os_type == "windows":
        preset_key = random.choice(["windows_11", "windows_10"])
    elif os_type == "macos":
        preset_key = random.choice(["macos_15", "macos_14"])
    elif os_type == "ios":
        preset_key = random.choice(["ios_iphone_16", "ios_iphone_15", "ios_ipad_pro"])
    elif os_type == "android":
        preset_key = random.choice(["android_samsung_s24", "android_pixel_8", "android_xiaomi_14"])
    else:
        preset_key = "windows_11"

    return generate_fingerprint_for_preset(preset_key)

def sanitize_fingerprint(fp: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures all fingerprint fields are internally consistent with their preset and OS."""
    if not isinstance(fp, dict):
        return generate_fingerprint_for_preset("windows_11")

    preset_key = fp.get("preset_key")
    os_name = fp.get("os", "").lower()
    ua = fp.get("user_agent", "").lower()

    if not preset_key or preset_key not in OS_PRESETS:
        if "pixel" in os_name or "pixel" in ua:
            preset_key = "android_pixel_8"
        elif "samsung" in os_name or "sm-s9" in ua:
            preset_key = "android_samsung_s24"
        elif "xiaomi" in os_name or "23116" in ua:
            preset_key = "android_xiaomi_14"
        elif "iphone 16" in os_name or "iphone os 18" in ua:
            preset_key = "ios_iphone_16"
        elif "iphone 15" in os_name or "iphone os 17" in ua:
            preset_key = "ios_iphone_15"
        elif "ipad" in os_name or "ipad" in ua:
            preset_key = "ios_ipad_pro"
        elif "windows 11" in os_name or "windows 11" in ua:
            preset_key = "windows_11"
        elif "windows 10" in os_name or "windows 10" in ua:
            preset_key = "windows_10"
        elif "windows 8" in os_name or "windows nt 6.3" in ua:
            preset_key = "windows_8_1"
        elif "windows 7" in os_name or "windows nt 6.1" in ua:
            preset_key = "windows_7"
        elif "macos 15" in os_name or "sequoia" in os_name:
            preset_key = "macos_15"
        elif "macos 14" in os_name or "sonoma" in os_name:
            preset_key = "macos_14"
        elif "macos 13" in os_name or "ventura" in os_name:
            preset_key = "macos_13"
        elif "linux" in os_name or "x11; linux" in ua:
            preset_key = "linux"
        else:
            preset_key = "windows_11"

    preset = OS_PRESETS[preset_key]
    fp["preset_key"] = preset_key
    fp["os"] = preset["name"]
    fp["category"] = preset["category"]
    fp["platform"] = preset["platform"]
    fp["user_agent"] = preset["ua"]
    fp["is_mobile"] = preset.get("is_mobile", False)
    fp["touch"] = preset.get("touch", False)
    fp["max_touch_points"] = preset.get("max_touch_points", 0)

    if preset_key.startswith("ios_"):
        fp["hardware_concurrency"] = 8 if preset_key == "ios_ipad_pro" else 6
        fp["device_memory"] = None
        def_res = preset.get("default_res", (393, 852))
        fp["screen_width"] = def_res[0]
        fp["screen_height"] = def_res[1]
        fp["scale_factor"] = preset.get("scale_factor", 3.0)
    elif preset.get("is_mobile"):
        def_res = preset.get("default_res", (412, 892))
        if fp.get("screen_width", 0) > 1000 or not fp.get("screen_width"):
            fp["screen_width"] = def_res[0]
            fp["screen_height"] = def_res[1]
        fp["scale_factor"] = preset.get("scale_factor", 2.625)
    else:
        if fp.get("screen_width", 0) < 1000:
            fp["screen_width"] = 1920
            fp["screen_height"] = 1080
        fp["scale_factor"] = 1.0

    gpu_cat = preset.get("default_gpu_category", "windows")
    gpu_pool = GPU_PRESETS.get(gpu_cat, GPU_PRESETS["windows"])
    curr_vendor = fp.get("webgl_vendor", "")
    curr_renderer = fp.get("webgl_renderer", "")
    valid_gpu = any(g["renderer"] == curr_renderer for g in gpu_pool)
    if not valid_gpu or not curr_vendor or not curr_renderer:
        g = random.choice(gpu_pool)
        fp["webgl_vendor"] = g["vendor"]
        fp["webgl_renderer"] = g["renderer"]

    if not fp.get("timezone"):
        fp["timezone"] = "Europe/Moscow"
    if not fp.get("languages"):
        fp["languages"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"

    return fp

