/**
 * Root Detect Master Stealth Engine
 * Injected at document_start in MAIN world & via content script.
 * Complete undetectable fingerprint spoofing for Windows, macOS, Linux, iOS, Android.
 */
(function () {
    'use strict';

    // Injected config or fallback defaults
    const cfg = window.__ROOT_DETECT_CONFIG__ || /* __ROOT_DETECT_CONFIG_START__ */ {
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
    } /* __ROOT_DETECT_CONFIG_END__ */;
    try { window.__ROOT_DETECT_CONFIG__ = cfg; } catch(e) {}

    // --- 0. FUNCTION PROTOTYPE TOSTRING CAMOUFLAGE ---
    const nativeToStringMap = new WeakMap();
    const originalToString = Function.prototype.toString;

    function makeNative(fn, name, argLength) {
        if (!fn || typeof fn !== 'function') return fn;
        const fnName = name !== undefined ? name : (fn.name || '');
        const str = `function ${fnName}() { [native code] }`;
        nativeToStringMap.set(fn, str);
        try {
            Object.defineProperty(fn, 'name', {
                value: fnName,
                writable: false,
                enumerable: false,
                configurable: true
            });
        } catch (e) {}
        if (argLength !== undefined) {
            try {
                Object.defineProperty(fn, 'length', {
                    value: argLength,
                    writable: false,
                    enumerable: false,
                    configurable: true
                });
            } catch (e) {}
        }
        return fn;
    }

    try {
        const customToString = function toString() {
            if (nativeToStringMap.has(this)) {
                return nativeToStringMap.get(this);
            }
            return originalToString.apply(this, arguments);
        };
        makeNative(customToString, 'toString', 0);
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
            overrideGetter(navProto, 'webdriver', () => false);
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
            overrideGetter(navProto, 'cookieEnabled', true);
            overrideGetter(navProto, 'onLine', true);
            overrideGetter(navProto, 'pdfViewerEnabled', () => !isIOS && !isMobile);
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
            overrideGetter(targetWin.navigator, 'webdriver', () => false);
            overrideGetter(targetWin.navigator, 'platform', plat);
            overrideGetter(targetWin.navigator, 'userAgent', ua);
            overrideGetter(targetWin.navigator, 'appVersion', appVer);
            overrideGetter(targetWin.navigator, 'hardwareConcurrency', coresVal);
            overrideGetter(targetWin.navigator, 'vendor', vendorVal);
            overrideGetter(targetWin.navigator, 'maxTouchPoints', maxTouch);
            overrideGetter(targetWin.navigator, 'language', primaryLang);
            overrideGetter(targetWin.navigator, 'languages', frozenLanguages);
            overrideGetter(targetWin.navigator, 'cookieEnabled', true);
            overrideGetter(targetWin.navigator, 'onLine', true);
            overrideGetter(targetWin.navigator, 'pdfViewerEnabled', () => !isIOS && !isMobile);
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
            makeNative(fakeGetHighEntropy, 'getHighEntropyValues', 1);
            uadProto.getHighEntropyValues = fakeGetHighEntropy;

            const fakeToJSON = function toJSON() {
                return {
                    brands: customBrands,
                    mobile: isMobile,
                    platform: uadPlatform
                };
            };
            makeNative(fakeToJSON, 'toJSON', 0);
            uadProto.toJSON = fakeToJSON;
        }

        // 4. Window.chrome Object Simulation (Desktop Chromium)
        if (!isIOS && !targetWin.chrome) {
            try {
                targetWin.chrome = {
                    app: {
                        isInstalled: false,
                        InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                        RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' },
                        getIsInstalled: makeNative(function getIsInstalled() { return false; }, 'getIsInstalled', 0),
                        getDetails: makeNative(function getDetails() { return null; }, 'getDetails', 0),
                        runningState: makeNative(function runningState() { return 'cannot_run'; }, 'runningState', 0)
                    },
                    csi: makeNative(function csi() { return { startE: Date.now(), onloadT: Date.now(), pageT: 0, tran: 0 }; }, 'csi', 0),
                    loadTimes: makeNative(function loadTimes() {
                        const now = Date.now() / 1000;
                        return {
                            requestTime: now,
                            startLoadTime: now,
                            commitLoadTime: now,
                            finishDocumentLoadTime: now,
                            finishLoadTime: now,
                            firstPaintTime: now,
                            firstPaintAfterLoadTime: 0,
                            navigationType: 'Other',
                            wasFetchedViaSpdy: false,
                            wasNpnNegotiated: false,
                            npnNegotiatedProtocol: '',
                            wasAlternateProtocolAvailable: false,
                            connectionInfo: 'http/1.1'
                        };
                    }, 'loadTimes', 0),
                    runtime: {
                        OnInstalledReason: { CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' },
                        OnRestartRequiredReason: { APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' },
                        PlatformArch: { ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
                        PlatformNaclArch: { ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
                        PlatformOs: { ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' },
                        RequestUpdateCheckStatus: { NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available' }
                    }
                };
            } catch(e) {}
        }

        // 5. Touch & MatchMedia
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
            makeNative(fakeMatchMedia, 'matchMedia', 1);
            targetWin.matchMedia = fakeMatchMedia;
        }

        // 6. WebGL Spoofing
        const UNMASKED_VENDOR_WEBGL = 0x9245;
        const UNMASKED_RENDERER_WEBGL = 0x9246;
        const VENDOR_PARAM = 0x1F00;
        const RENDERER_PARAM = 0x1F01;
        const VERSION_PARAM = 0x1F02;
        const SHADING_LANG_PARAM = 0x8B8C;

        function patchWebGL(proto, isWebGL2) {
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
                if (param === VERSION_PARAM) return isWebGL2 ? "WebGL 2.0 (OpenGL ES 3.0 Chromium)" : "WebGL 1.0 (OpenGL ES 2.0 Chromium)";
                if (param === SHADING_LANG_PARAM) return isWebGL2 ? "WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)" : "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)";
                return origGetParam.apply(this, arguments);
            };
            makeNative(fakeGetParam, 'getParameter', 1);
            proto.getParameter = fakeGetParam;

            const origGetExt = proto.getExtension;
            const fakeGetExt = function getExtension(name) {
                const ext = origGetExt.apply(this, arguments);
                if (name === 'WEBGL_debug_renderer_info') {
                    return { UNMASKED_VENDOR_WEBGL: 37445, UNMASKED_RENDERER_WEBGL: 37446 };
                }
                return ext;
            };
            makeNative(fakeGetExt, 'getExtension', 1);
            proto.getExtension = fakeGetExt;

            const origGetSupportedExt = proto.getSupportedExtensions;
            const fakeGetSupportedExt = function getSupportedExtensions() {
                const list = origGetSupportedExt ? origGetSupportedExt.apply(this, arguments) : [];
                if (list && Array.isArray(list) && !list.includes('WEBGL_debug_renderer_info')) {
                    return [...list, 'WEBGL_debug_renderer_info'];
                }
                return list;
            };
            makeNative(fakeGetSupportedExt, 'getSupportedExtensions', 0);
            proto.getSupportedExtensions = fakeGetSupportedExt;

            if (cfg.canvas_noise && proto.readPixels) {
                const origReadPixels = proto.readPixels;
                proto.readPixels = makeNative(function readPixels(x, y, w, h, format, type, pixels) {
                    origReadPixels.apply(this, arguments);
                    if (pixels && pixels.length > 0) {
                        const step = Math.max(4, Math.floor(pixels.length / 64));
                        for (let i = 0; i < pixels.length; i += step) {
                            pixels[i] = Math.min(255, Math.max(0, pixels[i] + (rng() > 0.5 ? 1 : -1)));
                        }
                    }
                }, 'readPixels', 7);
            }
        }

        if (targetWin.WebGLRenderingContext) patchWebGL(targetWin.WebGLRenderingContext.prototype, false);
        if (targetWin.WebGL2RenderingContext) patchWebGL(targetWin.WebGL2RenderingContext.prototype, true);

        // 7. SpeechSynthesis Voice Spoofing (Purge Apple/Mac voices on non-macOS)
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
            makeNative(fakeGetVoices, 'getVoices', 0);

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

        // 8. Screen & Geometry
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
                }, 'getBoundingClientRect', 0);
            }
        }

        if (targetWin.ScreenOrientation && targetWin.ScreenOrientation.prototype) {
            const orientType = isMobile ? "portrait-primary" : "landscape-primary";
            overrideGetter(targetWin.ScreenOrientation.prototype, 'type', orientType);
            overrideGetter(targetWin.ScreenOrientation.prototype, 'angle', 0);
        }

        // 9. Canvas Noise & Hash Coherence Protection
        if (cfg.canvas_noise) {
            if (targetWin.CanvasRenderingContext2D && targetWin.CanvasRenderingContext2D.prototype) {
                const origGetImageData = targetWin.CanvasRenderingContext2D.prototype.getImageData;
                const origPutImageData = targetWin.CanvasRenderingContext2D.prototype.putImageData;

                targetWin.CanvasRenderingContext2D.prototype.getImageData = makeNative(function getImageData(sx, sy, sw, sh) {
                    const imgData = origGetImageData.apply(this, arguments);
                    if (imgData && imgData.data && imgData.data.length > 0) {
                        const step = Math.max(4, Math.floor(imgData.data.length / 64));
                        for (let i = 0; i < imgData.data.length; i += step) {
                            const delta = (rng() > 0.5 ? 1 : -1);
                            imgData.data[i] = Math.min(255, Math.max(0, imgData.data[i] + delta));
                        }
                    }
                    return imgData;
                }, 'getImageData', 4);

                if (targetWin.HTMLCanvasElement && targetWin.HTMLCanvasElement.prototype) {
                    const origToDataURL = targetWin.HTMLCanvasElement.prototype.toDataURL;
                    targetWin.HTMLCanvasElement.prototype.toDataURL = makeNative(function toDataURL(type, encoderOptions) {
                        if (this.width > 0 && this.height > 0) {
                            try {
                                const ctx2d = this.getContext('2d');
                                if (ctx2d) {
                                    const p = origGetImageData.call(ctx2d, 0, 0, 1, 1);
                                    if (p && p.data && p.data.length >= 4) {
                                        p.data[0] = (p.data[0] + ((cfg.seed % 3) + 1)) % 256;
                                        origPutImageData.call(ctx2d, p, 0, 0);
                                    }
                                }
                            } catch(e) {}
                        }
                        return origToDataURL.apply(this, arguments);
                    }, 'toDataURL', 0);

                    const origToBlob = targetWin.HTMLCanvasElement.prototype.toBlob;
                    targetWin.HTMLCanvasElement.prototype.toBlob = makeNative(function toBlob(callback, type, quality) {
                        if (this.width > 0 && this.height > 0) {
                            try {
                                const ctx2d = this.getContext('2d');
                                if (ctx2d) {
                                    const p = origGetImageData.call(ctx2d, 0, 0, 1, 1);
                                    if (p && p.data && p.data.length >= 4) {
                                        p.data[0] = (p.data[0] + ((cfg.seed % 3) + 1)) % 256;
                                        origPutImageData.call(ctx2d, p, 0, 0);
                                    }
                                }
                            } catch(e) {}
                        }
                        return origToBlob.apply(this, arguments);
                    }, 'toBlob', 1);
                }
            }
        }

        // 10. Audio Noise Protection
        if (cfg.audio_noise) {
            if (targetWin.AudioBuffer && targetWin.AudioBuffer.prototype) {
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
                }, 'getChannelData', 1);

                const origCopyFromChannel = targetWin.AudioBuffer.prototype.copyFromChannel;
                if (origCopyFromChannel) {
                    targetWin.AudioBuffer.prototype.copyFromChannel = makeNative(function copyFromChannel(destination, channelNumber, startInChannel) {
                        origCopyFromChannel.apply(this, arguments);
                        if (destination && destination.length > 0) {
                            const step = Math.max(1, Math.floor(destination.length / 100));
                            for (let i = 0; i < destination.length; i += step) {
                                destination[i] += (rng() - 0.5) * 0.0000001;
                            }
                        }
                    }, 'copyFromChannel', 2);
                }
            }

            if (targetWin.AnalyserNode && targetWin.AnalyserNode.prototype) {
                const origGetFloatFreq = targetWin.AnalyserNode.prototype.getFloatFrequencyData;
                if (origGetFloatFreq) {
                    targetWin.AnalyserNode.prototype.getFloatFrequencyData = makeNative(function getFloatFrequencyData(array) {
                        origGetFloatFreq.apply(this, arguments);
                        if (array && array.length > 0) {
                            for (let i = 0; i < array.length; i += 8) {
                                array[i] += (rng() - 0.5) * 0.01;
                            }
                        }
                    }, 'getFloatFrequencyData', 1);
                }

                const origGetByteFreq = targetWin.AnalyserNode.prototype.getByteFrequencyData;
                if (origGetByteFreq) {
                    targetWin.AnalyserNode.prototype.getByteFrequencyData = makeNative(function getByteFrequencyData(array) {
                        origGetByteFreq.apply(this, arguments);
                        if (array && array.length > 0) {
                            for (let i = 0; i < array.length; i += 8) {
                                array[i] = Math.min(255, Math.max(0, array[i] + Math.round((rng() - 0.5) * 2)));
                            }
                        }
                    }, 'getByteFrequencyData', 1);
                }
            }
        }

        // 11. Intl Timezone, Locale & Date Spoofing
        const targetTz = cfg.timezone || "Europe/Moscow";

        function calcTzOffsetMinutes(date) {
            try {
                const d = date instanceof Date && !isNaN(date.getTime()) ? date : new Date();
                const invDate = new Date(d.toLocaleString('en-US', { timeZone: targetTz }));
                const diff = (invDate.getTime() - d.getTime());
                return -Math.round(diff / 60000);
            } catch(e) {
                return -180;
            }
        }

        function formatTzStrings(date) {
            try {
                const d = date instanceof Date && !isNaN(date.getTime()) ? date : new Date();
                const offsetMin = -calcTzOffsetMinutes(d);
                const sign = offsetMin >= 0 ? '+' : '-';
                const absMin = Math.abs(offsetMin);
                const h = String(Math.floor(absMin / 60)).padStart(2, '0');
                const m = String(absMin % 60).padStart(2, '0');
                const gmtStr = `GMT${sign}${h}${m}`;

                const dtFmt = new Intl.DateTimeFormat('en-US', {
                    timeZone: targetTz,
                    weekday: 'short',
                    year: 'numeric',
                    month: 'short',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false,
                    timeZoneName: 'long'
                });
                const dtParts = dtFmt.formatToParts(d);
                const pMap = {};
                for (const p of dtParts) pMap[p.type] = p.value;
                const tzName = pMap.timeZoneName || targetTz;

                const fullStr = `${pMap.weekday} ${pMap.month} ${pMap.day} ${pMap.year} ${pMap.hour}:${pMap.minute}:${pMap.second} ${gmtStr} (${tzName})`;
                const timeStr = `${pMap.hour}:${pMap.minute}:${pMap.second} ${gmtStr} (${tzName})`;
                const dateStr = `${pMap.weekday} ${pMap.month} ${pMap.day} ${pMap.year}`;
                return { fullStr, timeStr, dateStr };
            } catch(e) {
                return null;
            }
        }

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
                makeNative(fakeDTF, 'DateTimeFormat', 0);
                targetWin.Intl.DateTimeFormat = fakeDTF;

                const fakeResolvedOptions = function resolvedOptions() {
                    const opts = origResolvedOptions.apply(this, arguments);
                    opts.timeZone = targetTz;
                    opts.locale = primaryLang;
                    return opts;
                };
                makeNative(fakeResolvedOptions, 'resolvedOptions', 0);
                origDTF.prototype.resolvedOptions = fakeResolvedOptions;
            }

            if (targetWin.Intl.NumberFormat) {
                const origNF = targetWin.Intl.NumberFormat;
                const fakeNF = function NumberFormat(locales, options) {
                    return new origNF(locales || primaryLang, options);
                };
                fakeNF.prototype = origNF.prototype;
                fakeNF.supportedLocalesOf = origNF.supportedLocalesOf;
                makeNative(fakeNF, 'NumberFormat', 0);
                targetWin.Intl.NumberFormat = fakeNF;
            }

            if (targetWin.Intl.PluralRules) {
                const origPR = targetWin.Intl.PluralRules;
                const fakePR = function PluralRules(locales, options) {
                    return new origPR(locales || primaryLang, options);
                };
                fakePR.prototype = origPR.prototype;
                fakePR.supportedLocalesOf = origPR.supportedLocalesOf;
                makeNative(fakePR, 'PluralRules', 0);
                targetWin.Intl.PluralRules = fakePR;
            }

            if (targetWin.Intl.RelativeTimeFormat) {
                const origRTF = targetWin.Intl.RelativeTimeFormat;
                const fakeRTF = function RelativeTimeFormat(locales, options) {
                    return new origRTF(locales || primaryLang, options);
                };
                fakeRTF.prototype = origRTF.prototype;
                fakeRTF.supportedLocalesOf = origRTF.supportedLocalesOf;
                makeNative(fakeRTF, 'RelativeTimeFormat', 0);
                targetWin.Intl.RelativeTimeFormat = fakeRTF;
            }
        }

        if (targetWin.Date && targetWin.Date.prototype) {
            const origGetTimezoneOffset = targetWin.Date.prototype.getTimezoneOffset;
            const origToString = targetWin.Date.prototype.toString;
            const origToTimeString = targetWin.Date.prototype.toTimeString;
            const origToDateString = targetWin.Date.prototype.toDateString;
            const origToLocaleString = targetWin.Date.prototype.toLocaleString;
            const origToLocaleDateString = targetWin.Date.prototype.toLocaleDateString;
            const origToLocaleTimeString = targetWin.Date.prototype.toLocaleTimeString;

            targetWin.Date.prototype.getTimezoneOffset = makeNative(function getTimezoneOffset() {
                return calcTzOffsetMinutes(this);
            }, 'getTimezoneOffset', 0);

            targetWin.Date.prototype.toString = makeNative(function toString() {
                const res = formatTzStrings(this);
                return res ? res.fullStr : origToString.call(this);
            }, 'toString', 0);

            targetWin.Date.prototype.toTimeString = makeNative(function toTimeString() {
                const res = formatTzStrings(this);
                return res ? res.timeStr : origToTimeString.call(this);
            }, 'toTimeString', 0);

            targetWin.Date.prototype.toDateString = makeNative(function toDateString() {
                const res = formatTzStrings(this);
                return res ? res.dateStr : origToDateString.call(this);
            }, 'toDateString', 0);

            targetWin.Date.prototype.toLocaleString = makeNative(function toLocaleString(locales, options) {
                const l = locales || primaryLang;
                const o = Object.assign({ timeZone: targetTz }, options);
                return origToLocaleString.call(this, l, o);
            }, 'toLocaleString', 0);

            targetWin.Date.prototype.toLocaleDateString = makeNative(function toLocaleDateString(locales, options) {
                const l = locales || primaryLang;
                const o = Object.assign({ timeZone: targetTz }, options);
                return origToLocaleDateString.call(this, l, o);
            }, 'toLocaleDateString', 0);

            targetWin.Date.prototype.toLocaleTimeString = makeNative(function toLocaleTimeString(locales, options) {
                const l = locales || primaryLang;
                const o = Object.assign({ timeZone: targetTz }, options);
                return origToLocaleTimeString.call(this, l, o);
            }, 'toLocaleTimeString', 0);
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
            }, 'open', 0);
        }
    } catch(e) {}

})();

