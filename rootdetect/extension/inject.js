/**
 * Root Detect Master Stealth Engine
 * Injected at document_start in MAIN world & via content script.
 * Protects top window, all child dynamic iframes, window.open, Web Workers,
 * Navigator, Client Hints (NavigatorUAData), WebGL, Canvas, Audio, Screen, Touch, Speech, Plugins, Timezone, Intl.
 */
(function () {
    'use strict';

    const cfg = window.__ROOT_DETECT_CONFIG__ || {
        seed: 12345,
        user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36",
        platform: "Win32",
        os: "Windows 11",
        platform_hint: "Windows",
        languages: "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        timezone: "Europe/Moscow",
        webgl_vendor: "Google Inc. (NVIDIA)",
        webgl_renderer: "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        hardware_concurrency: 16,
        device_memory: 32,
        max_touch_points: 0,
        screen_width: 1920,
        screen_height: 1080,
        scale_factor: 1.0,
        is_mobile: false,
        canvas_noise: true,
        audio_noise: true
    };

    // --- 0. FUNCTION PROTOTYPE TOSTRING CAMOUFLAGE ---
    const nativeToStringMap = new WeakMap();
    const originalToString = Function.prototype.toString;

    function makeNative(fn, name) {
        if (!fn || typeof fn !== 'function') return fn;
        const fnName = name || fn.name || '';
        const str = `function ${fnName}() { [native code] }`;
        nativeToStringMap.set(fn, str);
        try {
            Object.defineProperty(fn, 'name', { value: fnName, configurable: true });
        } catch (e) {}
        return fn;
    }

    try {
        const customToString = function toString() {
            if (nativeToStringMap.has(this)) {
                return nativeToStringMap.get(this);
            }
            return originalToString.apply(this, arguments);
        };
        makeNative(customToString, 'toString');
        Object.defineProperty(Function.prototype, 'toString', {
            value: customToString,
            writable: true,
            configurable: true,
            enumerable: false
        });
    } catch (e) {}

    // Helper for pseudo-random deterministic noise
    function makePRNG(seed) {
        let s = (seed || 42) % 2147483647;
        if (s <= 0) s += 2147483646;
        return function () {
            s = (s * 16807) % 2147483647;
            return (s - 1) / 2147483646;
        };
    }
    const rng = makePRNG(cfg.seed || 42);

    const ua = cfg.user_agent || "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36";
    const appVer = ua.replace(/^Mozilla\//, '');
    const plat = cfg.platform || "Win32";
    const isMobile = !!cfg.is_mobile;
    const langList = (cfg.languages || "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7").split(',').map(s => s.split(';')[0].trim());
    const primaryLang = langList[0] || "ru-RU";
    const frozenLanguages = Object.freeze([...langList]);
    const maxTouch = isMobile ? (cfg.max_touch_points || 5) : (cfg.max_touch_points || 0);

    let uadPlatform = cfg.platform_hint || (plat === "Win32" ? "Windows" : (plat === "MacIntel" ? "macOS" : (plat.includes("iPhone") || plat.includes("iPad") ? "iOS" : (plat.toLowerCase().includes("android") || plat.includes("arm") ? "Android" : "Linux"))));
    const isIOS = plat === "iPhone" || plat === "iPad" || uadPlatform === "iOS" || (cfg.os && cfg.os.toLowerCase().includes("ios"));
    let uadPlatformVersion = "15.0.0";
    let uadArch = "x86";
    let uadBitness = "64";
    let uadModel = "";

    if (uadPlatform === "Windows") {
        uadPlatformVersion = "15.0.0";
        uadArch = "x86";
        uadBitness = "64";
    } else if (uadPlatform === "macOS") {
        uadPlatformVersion = "15.0.0";
        uadArch = "arm";
        uadBitness = "64";
    } else if (uadPlatform === "iOS" || isIOS) {
        uadPlatformVersion = "18.0.0";
        uadArch = "arm";
        uadBitness = "64";
        uadModel = plat.includes("iPad") ? "iPad" : "iPhone";
    } else if (uadPlatform === "Android") {
        uadPlatformVersion = "14.0.0";
        uadArch = "arm";
        uadBitness = "64";
        uadModel = ua.includes("Pixel 8") ? "Pixel 8 Pro" : (ua.includes("SM-S928B") ? "SM-S928B" : "23116PN5BC");
    } else {
        uadPlatformVersion = "6.5.0";
        uadArch = "x86";
        uadBitness = "64";
    }

    const customBrands = Object.freeze([
        { brand: "Google Chrome", version: "131" },
        { brand: "Chromium", version: "131" },
        { brand: "Not_A Brand", version: "24" }
    ]);

    const fullVersionList = Object.freeze([
        { brand: "Google Chrome", version: "131.0.6778.86" },
        { brand: "Chromium", version: "131.0.6778.86" },
        { brand: "Not_A Brand", version: "24.0.0.0" }
    ]);

    function overrideGetter(proto, prop, valOrGetter) {
        if (!proto) return;
        try {
            const getter = typeof valOrGetter === 'function' ? valOrGetter : () => valOrGetter;
            makeNative(getter, `get ${prop}`);
            Object.defineProperty(proto, prop, {
                get: getter,
                set: undefined,
                enumerable: true,
                configurable: true
            });
        } catch (e) {}
    }

    // --- CREATE CUSTOM USER AGENT DATA OBJECT ---
    function createFakeUAData(win) {
        const baseProto = (win && win.NavigatorUAData && win.NavigatorUAData.prototype)
            ? win.NavigatorUAData.prototype
            : Object.prototype;
        const uad = Object.create(baseProto);

        if (!win || !win.NavigatorUAData) {
            uad.brands = customBrands;
            uad.mobile = isMobile;
            uad.platform = uadPlatform;
            const getHighEntropyValues = function getHighEntropyValues(hints) {
                return Promise.resolve({
                    architecture: uadArch,
                    bitness: uadBitness,
                    brands: customBrands,
                    formFactors: isMobile ? ["Mobile"] : ["Desktop"],
                    fullVersionList: fullVersionList,
                    mobile: isMobile,
                    model: uadModel,
                    platform: uadPlatform,
                    platformVersion: uadPlatformVersion,
                    uaFullVersion: "131.0.6778.86",
                    wow64: false
                });
            };
            makeNative(getHighEntropyValues, 'getHighEntropyValues');
            uad.getHighEntropyValues = getHighEntropyValues;

            const toJSON = function toJSON() {
                return {
                    brands: customBrands,
                    mobile: isMobile,
                    platform: uadPlatform
                };
            };
            makeNative(toJSON, 'toJSON');
            uad.toJSON = toJSON;
        }

        return uad;
    }

    // --- CREATE CUSTOM PLUGIN ARRAY ---
    function createFakePlugins(win) {
        if (isMobile) {
            const emptyPlugins = Object.create(win.PluginArray ? win.PluginArray.prototype : Object.prototype);
            Object.defineProperty(emptyPlugins, 'length', { value: 0, configurable: true, enumerable: true });
            emptyPlugins.item = makeNative(function item(i) { return null; }, 'item');
            emptyPlugins.namedItem = makeNative(function namedItem(name) { return null; }, 'namedItem');
            emptyPlugins.refresh = makeNative(function refresh() {}, 'refresh');
            return emptyPlugins;
        }

        const rawPlugins = [
            { name: "PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" },
            { name: "Chrome PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" },
            { name: "Chromium PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format" },
            { name: "WebKit built-in PDF", filename: "internal-pdf-viewer", description: "Portable Document Format" }
        ];

        const pluginArray = Object.create(win.PluginArray ? win.PluginArray.prototype : Object.prototype);
        rawPlugins.forEach((p, idx) => {
            const pluginObj = Object.create(win.Plugin ? win.Plugin.prototype : Object.prototype);
            Object.assign(pluginObj, {
                name: p.name,
                filename: p.filename,
                description: p.description,
                length: 0
            });
            pluginObj.item = makeNative(function item(i) { return null; }, 'item');
            pluginObj.namedItem = makeNative(function namedItem(n) { return null; }, 'namedItem');

            Object.defineProperty(pluginArray, idx, { value: pluginObj, enumerable: true });
            Object.defineProperty(pluginArray, p.name, { value: pluginObj, enumerable: false });
        });
        Object.defineProperty(pluginArray, 'length', { value: rawPlugins.length, enumerable: true });
        pluginArray.item = makeNative(function item(i) { return pluginArray[i] || null; }, 'item');
        pluginArray.namedItem = makeNative(function namedItem(name) { return pluginArray[name] || null; }, 'namedItem');
        pluginArray.refresh = makeNative(function refresh() {}, 'refresh');
        return pluginArray;
    }

    function createFakeMimeTypes(win) {
        if (isMobile) {
            const emptyMimes = Object.create(win.MimeTypeArray ? win.MimeTypeArray.prototype : Object.prototype);
            Object.defineProperty(emptyMimes, 'length', { value: 0, configurable: true, enumerable: true });
            emptyMimes.item = makeNative(function item(i) { return null; }, 'item');
            emptyMimes.namedItem = makeNative(function namedItem(name) { return null; }, 'namedItem');
            return emptyMimes;
        }

        const mimeArray = Object.create(win.MimeTypeArray ? win.MimeTypeArray.prototype : Object.prototype);
        const rawMimes = [
            { type: "application/pdf", description: "Portable Document Format", suffixes: "pdf" },
            { type: "text/pdf", description: "Portable Document Format", suffixes: "pdf" }
        ];
        rawMimes.forEach((m, idx) => {
            const mimeObj = Object.create(win.MimeType ? win.MimeType.prototype : Object.prototype);
            Object.assign(mimeObj, m);
            Object.defineProperty(mimeArray, idx, { value: mimeObj, enumerable: true });
            Object.defineProperty(mimeArray, m.type, { value: mimeObj, enumerable: false });
        });
        Object.defineProperty(mimeArray, 'length', { value: rawMimes.length, enumerable: true });
        mimeArray.item = makeNative(function item(i) { return mimeArray[i] || null; }, 'item');
        mimeArray.namedItem = makeNative(function namedItem(t) { return mimeArray[t] || null; }, 'namedItem');
        return mimeArray;
    }

    const patchedWindows = new WeakSet();

    // --- MASTER WINDOW PATCHER ---
    function patchWindow(targetWin) {
        if (!targetWin || patchedWindows.has(targetWin)) return;
        try { patchedWindows.add(targetWin); } catch(e) {}

        // 0. Ensure toString camouflage on target window Function
        if (targetWin.Function && targetWin.Function.prototype) {
            try {
                Object.defineProperty(targetWin.Function.prototype, 'toString', {
                    value: customToString,
                    writable: true,
                    configurable: true,
                    enumerable: false
                });
            } catch(e) {}
        }

        const chromiumOnlyNavApis = [
            'hid', 'serial', 'usb', 'windowControlsOverlay', 'scheduling',
            'bluetooth', 'keyboard', 'virtualKeyboard', 'ink', 'managed',
            'presentation', 'gpu', 'xr', 'webkitTemporaryStorage', 'webkitPersistentStorage',
            'getInstalledRelatedApps', 'clearAppBadge', 'setAppBadge', 'userAgentData', 'deviceMemory'
        ];

        const desktopOnlyNavApis = [
            'hid', 'serial', 'windowControlsOverlay'
        ];

        const chromiumConstructors = [
            'HID', 'HIDDevice', 'Serial', 'SerialPort', 'USB', 'USBDevice',
            'WindowControlsOverlay', 'WindowControlsOverlayGeometryChangeEvent',
            'Scheduling', 'Scheduler', 'Bluetooth', 'BluetoothDevice',
            'Keyboard', 'KeyboardLayoutMap', 'VirtualKeyboard', 'Ink',
            'NavigatorUAData', 'GPU', 'GPUAdapter', 'XRSystem'
        ];

        // 1. Clean instance navigator properties
        try {
            if (targetWin.navigator) {
                delete targetWin.navigator.webdriver;
                delete targetWin.navigator.userAgent;
                delete targetWin.navigator.appVersion;
                delete targetWin.navigator.platform;
                delete targetWin.navigator.hardwareConcurrency;
                delete targetWin.navigator.deviceMemory;
                delete targetWin.navigator.maxTouchPoints;
                delete targetWin.navigator.language;
                delete targetWin.navigator.languages;
                delete targetWin.navigator.vendor;
                delete targetWin.navigator.vendorSub;
                delete targetWin.navigator.productSub;
                delete targetWin.navigator.oscpu;
                delete targetWin.navigator.userAgentData;
                delete targetWin.navigator.plugins;
                delete targetWin.navigator.mimeTypes;
                delete targetWin.navigator.webkitTemporaryStorage;
                delete targetWin.navigator.webkitPersistentStorage;
            }
        } catch(e) {}

        if (isIOS) {
            for (const api of chromiumOnlyNavApis) {
                try { delete targetWin.navigator[api]; } catch(e) {}
                try { if (targetWin.Navigator && targetWin.Navigator.prototype) delete targetWin.Navigator.prototype[api]; } catch(e) {}
            }
            for (const ctor of chromiumConstructors) {
                try { delete targetWin[ctor]; } catch(e) {}
            }
            try { delete targetWin.chrome; } catch(e) {}
        } else if (isMobile) {
            for (const api of desktopOnlyNavApis) {
                try { delete targetWin.navigator[api]; } catch(e) {}
                try { if (targetWin.Navigator && targetWin.Navigator.prototype) delete targetWin.Navigator.prototype[api]; } catch(e) {}
            }
            try {
                delete targetWin.HID;
                delete targetWin.HIDDevice;
                delete targetWin.Serial;
                delete targetWin.SerialPort;
                delete targetWin.WindowControlsOverlay;
            } catch(e) {}
        }

        const vendorVal = isIOS ? "Apple Computer, Inc." : "Google Inc.";
        const coresVal = cfg.hardware_concurrency || (isIOS ? (plat === "iPad" ? 8 : 6) : (isMobile ? 8 : 16));

        // 2. Navigator.prototype
        if (targetWin.Navigator && targetWin.Navigator.prototype) {
            const navProto = targetWin.Navigator.prototype;
            overrideGetter(navProto, 'webdriver', () => undefined);
            overrideGetter(navProto, 'userAgent', ua);
            overrideGetter(navProto, 'appVersion', appVer);
            overrideGetter(navProto, 'platform', plat);
            overrideGetter(navProto, 'hardwareConcurrency', coresVal);
            overrideGetter(navProto, 'maxTouchPoints', maxTouch);
            overrideGetter(navProto, 'language', primaryLang);
            overrideGetter(navProto, 'languages', frozenLanguages);
            overrideGetter(navProto, 'vendor', vendorVal);
            overrideGetter(navProto, 'vendorSub', "");
            overrideGetter(navProto, 'productSub', "20030107");
            overrideGetter(navProto, 'oscpu', plat.includes("Win") ? undefined : (plat.includes("Mac") ? undefined : (plat.includes("Linux x86") ? "Linux x86_64" : undefined)));

            if (isIOS) {
                for (const api of chromiumOnlyNavApis) {
                    try { delete navProto[api]; } catch(e) {}
                }
                try {
                    delete targetWin.NavigatorUAData;
                    delete targetWin.chrome;
                } catch(e) {}
            } else {
                overrideGetter(navProto, 'deviceMemory', cfg.device_memory || (isMobile ? 8 : 16));
                const fakeUAData = createFakeUAData(targetWin);
                overrideGetter(navProto, 'userAgentData', () => fakeUAData);
            }

            const fakePlugins = createFakePlugins(targetWin);
            overrideGetter(navProto, 'plugins', () => fakePlugins);

            const fakeMimes = createFakeMimeTypes(targetWin);
            overrideGetter(navProto, 'mimeTypes', () => fakeMimes);
        }

        // Direct fallback on targetWin.navigator instance
        if (targetWin.navigator) {
            overrideGetter(targetWin.navigator, 'platform', plat);
            overrideGetter(targetWin.navigator, 'userAgent', ua);
            overrideGetter(targetWin.navigator, 'appVersion', appVer);
            overrideGetter(targetWin.navigator, 'hardwareConcurrency', coresVal);
            overrideGetter(targetWin.navigator, 'vendor', vendorVal);
            overrideGetter(targetWin.navigator, 'maxTouchPoints', maxTouch);
            overrideGetter(targetWin.navigator, 'language', primaryLang);
            overrideGetter(targetWin.navigator, 'languages', frozenLanguages);
            overrideGetter(targetWin.navigator, 'plugins', createFakePlugins(targetWin));
            overrideGetter(targetWin.navigator, 'mimeTypes', createFakeMimeTypes(targetWin));

            if (isIOS) {
                for (const api of chromiumOnlyNavApis) {
                    try { delete targetWin.navigator[api]; } catch(e) {}
                }
                try {
                    delete targetWin.NavigatorUAData;
                    delete targetWin.chrome;
                } catch(e) {}
            } else {
                overrideGetter(targetWin.navigator, 'deviceMemory', cfg.device_memory || (isMobile ? 8 : 16));
                overrideGetter(targetWin.navigator, 'userAgentData', createFakeUAData(targetWin));
            }
        }

        // 3. NavigatorUAData.prototype if constructor exists (non-iOS)
        if (!isIOS && targetWin.NavigatorUAData && targetWin.NavigatorUAData.prototype) {
            const uadProto = targetWin.NavigatorUAData.prototype;
            overrideGetter(uadProto, 'brands', () => customBrands);
            overrideGetter(uadProto, 'mobile', () => isMobile);
            overrideGetter(uadProto, 'platform', () => uadPlatform);

            const fakeGetHighEntropy = function getHighEntropyValues(hints) {
                return Promise.resolve({
                    architecture: uadArch,
                    bitness: uadBitness,
                    brands: customBrands,
                    formFactors: isMobile ? ["Mobile"] : ["Desktop"],
                    fullVersionList: fullVersionList,
                    mobile: isMobile,
                    model: uadModel,
                    platform: uadPlatform,
                    platformVersion: uadPlatformVersion,
                    wow64: false
                });
            };
            makeNative(fakeGetHighEntropy, 'getHighEntropyValues');
            uadProto.getHighEntropyValues = fakeGetHighEntropy;

            const fakeToJSON = function toJSON() {
                return {
                    brands: customBrands,
                    mobile: isMobile,
                    platform: uadPlatform
                };
            };
            makeNative(fakeToJSON, 'toJSON');
            uadProto.toJSON = fakeToJSON;
        }

        // 4. Touch & MatchMedia
        if (isMobile || maxTouch > 0) {
            try {
                if (!('ontouchstart' in targetWin)) {
                    targetWin.ontouchstart = null;
                    targetWin.ontouchend = null;
                    targetWin.ontouchmove = null;
                    targetWin.ontouchcancel = null;
                }
                if (targetWin.Document && targetWin.Document.prototype && !('ontouchstart' in targetWin.Document.prototype)) {
                    targetWin.Document.prototype.ontouchstart = null;
                }
                if (targetWin.HTMLElement && targetWin.HTMLElement.prototype && !('ontouchstart' in targetWin.HTMLElement.prototype)) {
                    targetWin.HTMLElement.prototype.ontouchstart = null;
                }
            } catch(e) {}
        }

        if (targetWin.matchMedia) {
            const origMatchMedia = targetWin.matchMedia;
            const fakeMatchMedia = function matchMedia(query) {
                const res = origMatchMedia.apply(this, arguments);
                const q = (query || "").toLowerCase();
                if (isMobile) {
                    if (q.includes('(pointer: coarse)') || q.includes('(hover: none)') || q.includes('(any-pointer: coarse)') || q.includes('(any-hover: none)')) {
                        return Object.assign({}, res, { matches: true, media: query });
                    }
                    if (q.includes('(pointer: fine)') || q.includes('(hover: hover)') || q.includes('(any-pointer: fine)') || q.includes('(any-hover: hover)')) {
                        return Object.assign({}, res, { matches: false, media: query });
                    }
                } else {
                    if (q.includes('(pointer: fine)') || q.includes('(hover: hover)') || q.includes('(any-pointer: fine)') || q.includes('(any-hover: hover)')) {
                        return Object.assign({}, res, { matches: true, media: query });
                    }
                    if (q.includes('(pointer: coarse)') || q.includes('(hover: none)') || q.includes('(any-pointer: coarse)') || q.includes('(any-hover: none)')) {
                        return Object.assign({}, res, { matches: false, media: query });
                    }
                }
                return res;
            };
            makeNative(fakeMatchMedia, 'matchMedia');
            targetWin.matchMedia = fakeMatchMedia;
        }

        // 5. WebGL Spoofing
        const UNMASKED_VENDOR_WEBGL = 0x9245;
        const UNMASKED_RENDERER_WEBGL = 0x9246;
        const VENDOR_PARAM = 0x1F00;
        const RENDERER_PARAM = 0x1F01;

        function patchWebGL(proto) {
            if (!proto || !proto.getParameter) return;
            const origGetParam = proto.getParameter;
            const fakeGetParam = function getParameter(param) {
                if (param === UNMASKED_VENDOR_WEBGL || param === 37445) {
                    return cfg.webgl_vendor || "Google Inc. (NVIDIA)";
                }
                if (param === UNMASKED_RENDERER_WEBGL || param === 37446) {
                    return cfg.webgl_renderer || "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)";
                }
                if (param === VENDOR_PARAM) return "WebKit";
                if (param === RENDERER_PARAM) return "WebKit WebGL";
                return origGetParam.apply(this, arguments);
            };
            makeNative(fakeGetParam, 'getParameter');
            proto.getParameter = fakeGetParam;

            const origGetExt = proto.getExtension;
            const fakeGetExt = function getExtension(name) {
                const ext = origGetExt.apply(this, arguments);
                if (name === 'WEBGL_debug_renderer_info') {
                    return { UNMASKED_VENDOR_WEBGL: 37445, UNMASKED_RENDERER_WEBGL: 37446 };
                }
                return ext;
            };
            makeNative(fakeGetExt, 'getExtension');
            proto.getExtension = fakeGetExt;
        }

        if (targetWin.WebGLRenderingContext) patchWebGL(targetWin.WebGLRenderingContext.prototype);
        if (targetWin.WebGL2RenderingContext) patchWebGL(targetWin.WebGL2RenderingContext.prototype);

        // 6. SpeechSynthesis Voice Spoofing (Purge Apple/Mac voices on non-macOS)
        if (targetWin.speechSynthesis && targetWin.SpeechSynthesis) {
            function makeVoice(name, lang, isDef) {
                const voiceProto = targetWin.SpeechSynthesisVoice ? targetWin.SpeechSynthesisVoice.prototype : Object.prototype;
                const v = Object.create(voiceProto);
                Object.defineProperties(v, {
                    default: { value: !!isDef, enumerable: true },
                    lang: { value: lang, enumerable: true },
                    localService: { value: true, enumerable: true },
                    name: { value: name, enumerable: true },
                    voiceURI: { value: name, enumerable: true }
                });
                return v;
            }

            let spoofedVoices = [];
            if (uadPlatform === "Android") {
                spoofedVoices = [
                    makeVoice("Google US English", "en-US", true),
                    makeVoice("Google UK English Female", "en-GB", false),
                    makeVoice("Google UK English Male", "en-GB", false),
                    makeVoice("Google русский", "ru-RU", false),
                    makeVoice("Android Speech en-us-x-sfg#female_1-local", "en-US", false),
                    makeVoice("Android Speech ru-ru-x-dfc#female_1-local", "ru-RU", false)
                ];
            } else if (uadPlatform === "Windows") {
                spoofedVoices = [
                    makeVoice("Microsoft David - English (United States)", "en-US", true),
                    makeVoice("Microsoft Zira - English (United States)", "en-US", false),
                    makeVoice("Microsoft Mark - English (United States)", "en-US", false),
                    makeVoice("Microsoft Irina - Russian (Russia)", "ru-RU", false),
                    makeVoice("Microsoft Pavel - Russian (Russia)", "ru-RU", false)
                ];
            } else if (uadPlatform === "Linux") {
                spoofedVoices = [
                    makeVoice("English (America)", "en-US", true),
                    makeVoice("Russian", "ru-RU", false)
                ];
            } else {
                spoofedVoices = [
                    makeVoice("Samantha", "en-US", true),
                    makeVoice("Alex", "en-US", false),
                    makeVoice("Milena", "ru-RU", false),
                    makeVoice("Yuri", "ru-RU", false),
                    makeVoice("Thomas", "fr-FR", false),
                    makeVoice("Monica", "es-ES", false),
                    makeVoice("Anna", "de-DE", false)
                ];
            }

            const frozenVoices = Object.freeze([...spoofedVoices]);
            const fakeGetVoices = function getVoices() { return [...frozenVoices]; };
            makeNative(fakeGetVoices, 'getVoices');

            targetWin.SpeechSynthesis.prototype.getVoices = fakeGetVoices;
            targetWin.speechSynthesis.getVoices = fakeGetVoices;

            const origAddEv = targetWin.SpeechSynthesis.prototype.addEventListener;
            targetWin.SpeechSynthesis.prototype.addEventListener = function (type, listener, options) {
                if (type === 'voiceschanged' && typeof listener === 'function') {
                    setTimeout(() => {
                        try { listener.call(targetWin.speechSynthesis, new Event('voiceschanged')); } catch(e) {}
                    }, 0);
                }
                return origAddEv.apply(this, arguments);
            };
        }

        // 7. Screen & Geometry
        const sw = cfg.screen_width || (isMobile ? 412 : 1920);
        const sh = cfg.screen_height || (isMobile ? 892 : 1080);
        const scale = cfg.scale_factor || (isMobile ? 2.625 : 1.0);
        const availH = isMobile ? sh : Math.max(0, sh - 40);
        const origInnerW = targetWin.innerWidth || sw;
        const origInnerH = targetWin.innerHeight || sh;
        const mobileInnerH = isMobile ? Math.min(sh, Math.max(600, Math.round(sh * 0.82))) : origInnerH;

        if (targetWin.Screen && targetWin.Screen.prototype) {
            overrideGetter(targetWin.Screen.prototype, 'width', sw);
            overrideGetter(targetWin.Screen.prototype, 'height', sh);
            overrideGetter(targetWin.Screen.prototype, 'availWidth', sw);
            overrideGetter(targetWin.Screen.prototype, 'availHeight', availH);
            overrideGetter(targetWin.Screen.prototype, 'availLeft', 0);
            overrideGetter(targetWin.Screen.prototype, 'availTop', 0);
            overrideGetter(targetWin.Screen.prototype, 'colorDepth', 24);
            overrideGetter(targetWin.Screen.prototype, 'pixelDepth', 24);
        }

        if (targetWin.screen) {
            overrideGetter(targetWin.screen, 'width', sw);
            overrideGetter(targetWin.screen, 'height', sh);
            overrideGetter(targetWin.screen, 'availWidth', sw);
            overrideGetter(targetWin.screen, 'availHeight', availH);
            overrideGetter(targetWin.screen, 'availLeft', 0);
            overrideGetter(targetWin.screen, 'availTop', 0);
            overrideGetter(targetWin.screen, 'colorDepth', 24);
            overrideGetter(targetWin.screen, 'pixelDepth', 24);
        }

        overrideGetter(targetWin, 'devicePixelRatio', scale);
        overrideGetter(targetWin, 'innerWidth', isMobile ? sw : origInnerW);
        overrideGetter(targetWin, 'innerHeight', isMobile ? mobileInnerH : origInnerH);
        overrideGetter(targetWin, 'outerWidth', isMobile ? sw : origInnerW);
        overrideGetter(targetWin, 'outerHeight', isMobile ? sh : origInnerH);
        overrideGetter(targetWin, 'screenX', 0);
        overrideGetter(targetWin, 'screenY', 0);
        overrideGetter(targetWin, 'screenLeft', 0);
        overrideGetter(targetWin, 'screenTop', 0);

        // VisualViewport hooks
        if (targetWin.VisualViewport && targetWin.VisualViewport.prototype) {
            overrideGetter(targetWin.VisualViewport.prototype, 'width', isMobile ? sw : origInnerW);
            overrideGetter(targetWin.VisualViewport.prototype, 'height', isMobile ? mobileInnerH : origInnerH);
            overrideGetter(targetWin.VisualViewport.prototype, 'scale', 1.0);
            overrideGetter(targetWin.VisualViewport.prototype, 'pageLeft', 0);
            overrideGetter(targetWin.VisualViewport.prototype, 'pageTop', 0);
            overrideGetter(targetWin.VisualViewport.prototype, 'offsetLeft', 0);
            overrideGetter(targetWin.VisualViewport.prototype, 'offsetTop', 0);
        }

        // documentElement / body / viewport elements clientWidth & clientHeight & getBoundingClientRect hooks
        if (targetWin.Element && targetWin.Element.prototype) {
            const origClientWidthDesc = Object.getOwnPropertyDescriptor(targetWin.Element.prototype, 'clientWidth');
            const origClientHeightDesc = Object.getOwnPropertyDescriptor(targetWin.Element.prototype, 'clientHeight');
            const origScrollWidthDesc = Object.getOwnPropertyDescriptor(targetWin.Element.prototype, 'scrollWidth');
            const origGetBoundingClientRect = targetWin.Element.prototype.getBoundingClientRect;

            if (origClientWidthDesc && origClientWidthDesc.get) {
                Object.defineProperty(targetWin.Element.prototype, 'clientWidth', {
                    get: makeNative(function clientWidth() {
                        const val = origClientWidthDesc.get.call(this);
                        if (isMobile) {
                            const isRootOrViewport = (targetWin.document && (this === targetWin.document.documentElement || this === targetWin.document.body)) ||
                                                     (this.id && (this.id.toLowerCase() === 'viewport' || this.id.toLowerCase() === 'res')) ||
                                                     (this.className && typeof this.className === 'string' && this.className.toLowerCase().includes('viewport'));
                            if (isRootOrViewport) {
                                return sw;
                            }
                            if (typeof val === 'number' && val > sw) {
                                return sw;
                            }
                        }
                        return val;
                    }, 'get clientWidth'),
                    configurable: true,
                    enumerable: true
                });
            }

            if (origClientHeightDesc && origClientHeightDesc.get) {
                Object.defineProperty(targetWin.Element.prototype, 'clientHeight', {
                    get: makeNative(function clientHeight() {
                        const val = origClientHeightDesc.get.call(this);
                        if (isMobile) {
                            const isRootOrViewport = (targetWin.document && (this === targetWin.document.documentElement || this === targetWin.document.body)) ||
                                                     (this.id && (this.id.toLowerCase() === 'viewport' || this.id.toLowerCase() === 'res')) ||
                                                     (this.className && typeof this.className === 'string' && this.className.toLowerCase().includes('viewport'));
                            if (isRootOrViewport) {
                                return mobileInnerH;
                            }
                            if (typeof val === 'number' && val > sh) {
                                return sh;
                            }
                        }
                        return val;
                    }, 'get clientHeight'),
                    configurable: true,
                    enumerable: true
                });
            }

            if (origScrollWidthDesc && origScrollWidthDesc.get) {
                Object.defineProperty(targetWin.Element.prototype, 'scrollWidth', {
                    get: makeNative(function scrollWidth() {
                        const val = origScrollWidthDesc.get.call(this);
                        if (isMobile) {
                            const isRootOrViewport = (targetWin.document && (this === targetWin.document.documentElement || this === targetWin.document.body)) ||
                                                     (this.id && (this.id.toLowerCase() === 'viewport' || this.id.toLowerCase() === 'res'));
                            if (isRootOrViewport) {
                                return sw;
                            }
                        }
                        return val;
                    }, 'get scrollWidth'),
                    configurable: true,
                    enumerable: true
                });
            }

            if (origGetBoundingClientRect) {
                targetWin.Element.prototype.getBoundingClientRect = makeNative(function getBoundingClientRect() {
                    const rect = origGetBoundingClientRect.apply(this, arguments);
                    if (isMobile && rect) {
                        const isRootOrViewport = (targetWin.document && (this === targetWin.document.documentElement || this === targetWin.document.body)) ||
                                                 (this.id && (this.id.toLowerCase() === 'viewport' || this.id.toLowerCase() === 'res'));
                        if (isRootOrViewport) {
                            return new DOMRect(0, 0, sw, mobileInnerH);
                        }
                    }
                    return rect;
                }, 'getBoundingClientRect');
            }
        }

        if (targetWin.ScreenOrientation && targetWin.ScreenOrientation.prototype) {
            const orientType = isMobile ? "portrait-primary" : "landscape-primary";
            overrideGetter(targetWin.ScreenOrientation.prototype, 'type', orientType);
            overrideGetter(targetWin.ScreenOrientation.prototype, 'angle', 0);
        }

        // 8. Canvas Noise Protection
        if (cfg.canvas_noise && targetWin.HTMLCanvasElement) {
            if (targetWin.CanvasRenderingContext2D) {
                const origGetImageData = targetWin.CanvasRenderingContext2D.prototype.getImageData;
                targetWin.CanvasRenderingContext2D.prototype.getImageData = makeNative(function getImageData(sx, sy, sw, sh) {
                    const imgData = origGetImageData.apply(this, arguments);
                    if (imgData && imgData.data && imgData.data.length > 0) {
                        const step = Math.max(4, Math.floor(imgData.data.length / 50));
                        for (let i = 0; i < imgData.data.length; i += step) {
                            const noise = (rng() - 0.5) * 2;
                            imgData.data[i] = Math.min(255, Math.max(0, imgData.data[i] + Math.round(noise)));
                        }
                    }
                    return imgData;
                }, 'getImageData');
            }
        }

        // 9. Audio Noise Protection
        if (cfg.audio_noise && targetWin.AudioBuffer) {
            const origGetChannelData = targetWin.AudioBuffer.prototype.getChannelData;
            targetWin.AudioBuffer.prototype.getChannelData = makeNative(function getChannelData(channel) {
                const data = origGetChannelData.apply(this, arguments);
                if (data && data.length > 0) {
                    const step = Math.max(1, Math.floor(data.length / 100));
                    for (let i = 0; i < data.length; i += step) {
                        data[i] += (rng() - 0.5) * 0.0000001;
                    }
                }
                return data;
            }, 'getChannelData');
        }

        // 10. Intl Timezone, Locale & Date Spoofing
        const targetTz = cfg.timezone || "Europe/Moscow";

        if (targetWin.Intl) {
            if (targetWin.Intl.DateTimeFormat) {
                const origDTF = targetWin.Intl.DateTimeFormat;
                const origResolvedOptions = origDTF.prototype.resolvedOptions;

                const fakeDTF = function DateTimeFormat(locales, options) {
                    const l = locales || primaryLang;
                    const opts = Object.assign({}, options);
                    if (!opts.timeZone) opts.timeZone = targetTz;
                    return new origDTF(l, opts);
                };
                fakeDTF.prototype = origDTF.prototype;
                fakeDTF.supportedLocalesOf = origDTF.supportedLocalesOf;
                makeNative(fakeDTF, 'DateTimeFormat');
                targetWin.Intl.DateTimeFormat = fakeDTF;

                const fakeResolvedOptions = function resolvedOptions() {
                    const opts = origResolvedOptions.apply(this, arguments);
                    opts.timeZone = targetTz;
                    opts.locale = primaryLang;
                    return opts;
                };
                makeNative(fakeResolvedOptions, 'resolvedOptions');
                origDTF.prototype.resolvedOptions = fakeResolvedOptions;
            }

            if (targetWin.Intl.NumberFormat) {
                const origNF = targetWin.Intl.NumberFormat;
                const fakeNF = function NumberFormat(locales, options) {
                    return new origNF(locales || primaryLang, options);
                };
                fakeNF.prototype = origNF.prototype;
                fakeNF.supportedLocalesOf = origNF.supportedLocalesOf;
                makeNative(fakeNF, 'NumberFormat');
                targetWin.Intl.NumberFormat = fakeNF;
            }

            if (targetWin.Intl.PluralRules) {
                const origPR = targetWin.Intl.PluralRules;
                const fakePR = function PluralRules(locales, options) {
                    return new origPR(locales || primaryLang, options);
                };
                fakePR.prototype = origPR.prototype;
                fakePR.supportedLocalesOf = origPR.supportedLocalesOf;
                makeNative(fakePR, 'PluralRules');
                targetWin.Intl.PluralRules = fakePR;
            }

            if (targetWin.Intl.RelativeTimeFormat) {
                const origRTF = targetWin.Intl.RelativeTimeFormat;
                const fakeRTF = function RelativeTimeFormat(locales, options) {
                    return new origRTF(locales || primaryLang, options);
                };
                fakeRTF.prototype = origRTF.prototype;
                fakeRTF.supportedLocalesOf = origRTF.supportedLocalesOf;
                makeNative(fakeRTF, 'RelativeTimeFormat');
                targetWin.Intl.RelativeTimeFormat = fakeRTF;
            }
        }

        if (targetWin.Date && targetWin.Date.prototype) {
            const origToLocaleString = targetWin.Date.prototype.toLocaleString;
            const origToLocaleDateString = targetWin.Date.prototype.toLocaleDateString;
            const origToLocaleTimeString = targetWin.Date.prototype.toLocaleTimeString;

            targetWin.Date.prototype.toLocaleString = makeNative(function toLocaleString(locales, options) {
                const l = locales || primaryLang;
                const o = Object.assign({ timeZone: targetTz }, options);
                return origToLocaleString.call(this, l, o);
            }, 'toLocaleString');

            targetWin.Date.prototype.toLocaleDateString = makeNative(function toLocaleDateString(locales, options) {
                const l = locales || primaryLang;
                const o = Object.assign({ timeZone: targetTz }, options);
                return origToLocaleDateString.call(this, l, o);
            }, 'toLocaleDateString');

            targetWin.Date.prototype.toLocaleTimeString = makeNative(function toLocaleTimeString(locales, options) {
                const l = locales || primaryLang;
                const o = Object.assign({ timeZone: targetTz }, options);
                return origToLocaleTimeString.call(this, l, o);
            }, 'toLocaleTimeString');
        }
    }

    // --- APPLY PATCH TO TOP WINDOW ---
    patchWindow(window);

    // --- INTERCEPT ALL DYNAMIC IFRAMES & CHILD WINDOWS ---
    try {
        if (window.HTMLIFrameElement && HTMLIFrameElement.prototype) {
            const origContentWindowDesc = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
            if (origContentWindowDesc && origContentWindowDesc.get) {
                Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                    get: makeNative(function contentWindow() {
                        const win = origContentWindowDesc.get.apply(this, arguments);
                        if (win) {
                            try { patchWindow(win); } catch(e) {}
                        }
                        return win;
                    }, 'get contentWindow'),
                    configurable: true,
                    enumerable: true
                });
            }

            const origContentDocDesc = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentDocument');
            if (origContentDocDesc && origContentDocDesc.get) {
                Object.defineProperty(HTMLIFrameElement.prototype, 'contentDocument', {
                    get: makeNative(function contentDocument() {
                        const doc = origContentDocDesc.get.apply(this, arguments);
                        if (doc && doc.defaultView) {
                            try { patchWindow(doc.defaultView); } catch(e) {}
                        }
                        return doc;
                    }, 'get contentDocument'),
                    configurable: true,
                    enumerable: true
                });
            }
        }

        if (window.open) {
            const origOpen = window.open;
            window.open = makeNative(function open() {
                const win = origOpen.apply(this, arguments);
                if (win) {
                    try { patchWindow(win); } catch(e) {}
                }
                return win;
            }, 'open');
        }
    } catch(e) {}

})();
