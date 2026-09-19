/**
 * Root Detect Stealth Injection Script
 * Injected at document_start in MAIN world
 */
(function () {
    'use strict';

    // Load config injected via window.__ROOT_DETECT_CONFIG__ or default template
    const cfg = window.__ROOT_DETECT_CONFIG__ || {
        seed: 12345,
        webgl_vendor: "Google Inc. (Apple)",
        webgl_renderer: "ANGLE (Apple, ANGLE Metal Renderer: Apple M3 Max, Version 14.5)",
        platform: "MacIntel",
        hardware_concurrency: 12,
        device_memory: 16,
        canvas_noise: true,
        audio_noise: true
    };

    // --- 1. SCRIPT DETECT & WEBDRIVER CLEANUP ---
    try {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        delete navigator.__proto__.webdriver;
    } catch (e) {}

    // --- 2. HARDWARE & PLATFORM SPOOFING ---
    try {
        if (cfg.hardware_concurrency) {
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => cfg.hardware_concurrency,
                configurable: true
            });
        }
        if (cfg.device_memory) {
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => cfg.device_memory,
                configurable: true
            });
        }
        if (cfg.platform) {
            Object.defineProperty(navigator, 'platform', {
                get: () => cfg.platform,
                configurable: true
            });
        }
        if (cfg.max_touch_points !== undefined) {
            Object.defineProperty(navigator, 'maxTouchPoints', {
                get: () => cfg.max_touch_points,
                configurable: true
            });
            if (cfg.max_touch_points > 0 && !('ontouchstart' in window)) {
                window.ontouchstart = null;
            }
        }
    } catch (e) {}

    // --- 3. PSEUDO-RANDOM NOISE GENERATOR (DETERMINISTIC PER PROFILE) ---
    function makePRNG(seed) {
        let s = seed % 2147483647;
        if (s <= 0) s += 2147483646;
        return function () {
            s = (s * 16807) % 2147483647;
            return (s - 1) / 2147483646;
        };
    }
    const rng = makePRNG(cfg.seed || 42);

    // --- 4. WEBGL VENDOR & RENDERER SPOOFING ---
    const UNMASKED_VENDOR_WEBGL = 0x9245;
    const UNMASKED_RENDERER_WEBGL = 0x9246;

    function patchWebGL(proto) {
        if (!proto || !proto.getParameter) return;
        const originalGetParameter = proto.getParameter;
        proto.getParameter = function (param) {
            if (param === UNMASKED_VENDOR_WEBGL) {
                return cfg.webgl_vendor || "Google Inc. (NVIDIA)";
            }
            if (param === UNMASKED_RENDERER_WEBGL) {
                return cfg.webgl_renderer || "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 Direct3D11 vs_5_0 ps_5_0, D3D11)";
            }
            return originalGetParameter.apply(this, arguments);
        };
    }

    if (window.WebGLRenderingContext) patchWebGL(WebGLRenderingContext.prototype);
    if (window.WebGL2RenderingContext) patchWebGL(WebGL2RenderingContext.prototype);

    // --- 5. CANVAS FINGERPRINT NOISE ---
    if (cfg.canvas_noise && window.CanvasRenderingContext2D) {
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        CanvasRenderingContext2D.prototype.getImageData = function (x, y, w, h) {
            const imageData = originalGetImageData.apply(this, arguments);
            const data = imageData.data;
            // Add ultra-subtle deterministic noise (imperceptible to human eye)
            const step = Math.max(1, Math.floor(data.length / 100));
            for (let i = 0; i < data.length; i += step * 4) {
                const noise = Math.floor((rng() - 0.5) * 2);
                data[i] = Math.min(255, Math.max(0, data[i] + noise));
            }
            return imageData;
        };

        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function () {
            const ctx = this.getContext('2d');
            if (ctx && this.width > 0 && this.height > 0) {
                try {
                    const imgData = ctx.getImageData(0, 0, Math.min(this.width, 16), Math.min(this.height, 16));
                    // Touch slightly to trigger noise
                    ctx.putImageData(imgData, 0, 0);
                } catch (e) {}
            }
            return originalToDataURL.apply(this, arguments);
        };
    }

    // --- 6. AUDIOCONTEXT FINGERPRINT NOISE ---
    if (cfg.audio_noise) {
        if (window.AudioBuffer) {
            const origGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function () {
                const data = origGetChannelData.apply(this, arguments);
                const step = Math.max(1, Math.floor(data.length / 50));
                for (let i = 0; i < data.length; i += step) {
                    data[i] += (rng() - 0.5) * 0.000001;
                }
                return data;
            };
        }

        if (window.AnalyserNode) {
            const origGetFloatFreq = AnalyserNode.prototype.getFloatFrequencyData;
            AnalyserNode.prototype.getFloatFrequencyData = function (arr) {
                origGetFloatFreq.apply(this, arguments);
                for (let i = 0; i < arr.length; i += 10) {
                    arr[i] += (rng() - 0.5) * 0.01;
                }
            };
        }
    }

    // --- 7. CHROME RUNTIME & PERMISSIONS SHIM ---
    if (!window.chrome) {
        window.chrome = {};
    }
    if (!window.chrome.runtime) {
        window.chrome.runtime = {
            id: undefined,
            connect: () => {},
            sendMessage: () => {}
        };
    }
})();
