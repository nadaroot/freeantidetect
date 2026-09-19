/**
 * Root Detect Extension Background Service Worker
 * Handles declarativeNetRequest header rules, WebRTC leak prevention, and proxy authentication
 */

// 1. Prevent WebRTC non-proxied IP leaks
try {
    if (chrome.privacy && chrome.privacy.network && chrome.privacy.network.webRTCIPHandlingPolicy) {
        chrome.privacy.network.webRTCIPHandlingPolicy.set({
            value: 'disable_non_proxied_udp'
        }, () => {
            console.log('[RootDetect] WebRTC leak protection enabled');
        });
    }
} catch (e) {
    console.error('[RootDetect] WebRTC policy error:', e);
}

// 2. Dynamic DeclarativeNetRequest Rules & Proxy Authentication Setup
async function initExtension() {
    try {
        const url = chrome.runtime.getURL('config.json');
        const resp = await fetch(url);
        if (!resp.ok) return;
        const config = await resp.json();

        // 2.1 Dynamic Header Rules
        if (chrome.declarativeNetRequest && chrome.declarativeNetRequest.updateDynamicRules) {
            const platformStr = config.platform_hint || (config.platform === 'Win32' ? 'Windows' : (config.platform === 'MacIntel' ? 'macOS' : (config.platform.includes('iPhone') ? 'iOS' : (config.platform.toLowerCase().includes('android') ? 'Android' : 'Linux'))));
            const isMobile = !!config.is_mobile;
            const ua = config.user_agent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36';
            const lang = config.languages || 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7';

            let arch = 'x86';
            let bitness = '64';
            let platformVer = '15.0.0';
            let model = '';

            if (platformStr === 'Windows') {
                arch = 'x86'; bitness = '64'; platformVer = '15.0.0';
            } else if (platformStr === 'macOS') {
                arch = 'arm'; bitness = '64'; platformVer = '15.0.0';
            } else if (platformStr === 'iOS') {
                arch = 'arm'; bitness = '64'; platformVer = '18.0.0'; model = 'iPhone';
            } else if (platformStr === 'Android') {
                arch = 'arm'; bitness = '64'; platformVer = '14.0.0';
                model = ua.includes('Pixel 8') ? 'Pixel 8 Pro' : (ua.includes('SM-S928B') ? 'SM-S928B' : '23116PN5BC');
            } else {
                arch = 'x86'; bitness = '64'; platformVer = '6.5.0';
            }

            let requestHeaders = [];
            if (platformStr === 'iOS' || (config.platform && config.platform.includes('iPhone')) || (config.platform && config.platform.includes('iPad'))) {
                requestHeaders = [
                    { header: "sec-ch-ua", operation: "remove" },
                    { header: "sec-ch-ua-mobile", operation: "remove" },
                    { header: "sec-ch-ua-platform", operation: "remove" },
                    { header: "sec-ch-ua-platform-version", operation: "remove" },
                    { header: "sec-ch-ua-arch", operation: "remove" },
                    { header: "sec-ch-ua-bitness", operation: "remove" },
                    { header: "sec-ch-ua-model", operation: "remove" },
                    { header: "sec-ch-ua-full-version-list", operation: "remove" },
                    { header: "User-Agent", operation: "set", value: ua },
                    { header: "Accept-Language", operation: "set", value: lang }
                ];
            } else {
                requestHeaders = [
                    { header: "sec-ch-ua-platform", operation: "set", value: `"${platformStr}"` },
                    { header: "sec-ch-ua-platform-version", operation: "set", value: `"${platformVer}"` },
                    { header: "sec-ch-ua-arch", operation: "set", value: `"${arch}"` },
                    { header: "sec-ch-ua-bitness", operation: "set", value: `"${bitness}"` },
                    { header: "sec-ch-ua-mobile", operation: "set", value: isMobile ? "?1" : "?0" },
                    { header: "sec-ch-ua-model", operation: "set", value: `"${model}"` },
                    { header: "sec-ch-ua", operation: "set", value: `"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"` },
                    { header: "User-Agent", operation: "set", value: ua },
                    { header: "Accept-Language", operation: "set", value: lang }
                ];
            }

            const dynamicRule = {
                id: 1001,
                priority: 2,
                action: {
                    type: "modifyHeaders",
                    requestHeaders: requestHeaders
                },
                condition: {
                    urlFilter: "*",
                    resourceTypes: [
                        "main_frame", "sub_frame", "stylesheet", "script", "image", "font", "object", "xmlhttprequest", "ping", "media", "websocket", "other"
                    ]
                }
            };

            await chrome.declarativeNetRequest.updateDynamicRules({
                removeRuleIds: [1001],
                addRules: [dynamicRule]
            });
            console.log('[RootDetect] Dynamic header rules configured for platform:', platformStr);
        }

        // 2.2 Register dynamic content script in MAIN world
        if (chrome.scripting && chrome.scripting.registerContentScripts) {
            try {
                await chrome.scripting.unregisterContentScripts().catch(() => {});
                await chrome.scripting.registerContentScripts([
                    {
                        id: "root-detect-stealth-main",
                        js: ["inject.js"],
                        matches: ["<all_urls>"],
                        runAt: "document_start",
                        world: "MAIN",
                        allFrames: true
                    }
                ]);
                console.log('[RootDetect] Dynamic MAIN world script registered');
            } catch (scrErr) {
                console.warn('[RootDetect] Scripting registration notice:', scrErr);
            }
        }

        // 2.3 Proxy Auth Credentials
        if (config.proxy_auth && config.proxy_auth.username && config.proxy_auth.password) {
            if (chrome.webRequest && chrome.webRequest.onAuthRequired) {
                chrome.webRequest.onAuthRequired.addListener(
                    function (details) {
                        return {
                            authCredentials: {
                                username: config.proxy_auth.username,
                                password: config.proxy_auth.password
                            }
                        };
                    },
                    { urls: ["<all_urls>"] },
                    ["blocking"]
                );
                console.log('[RootDetect] Proxy authentication registered');
            }
        }
    } catch (err) {
        console.error('[RootDetect] Background initialization error:', err);
    }
}

// 3. Proactive navigation injection on document_start
if (chrome.webNavigation && chrome.webNavigation.onCommitted) {
    chrome.webNavigation.onCommitted.addListener((details) => {
        if (details.url && !details.url.startsWith('chrome://') && !details.url.startsWith('chrome-extension://')) {
            if (chrome.scripting && chrome.scripting.executeScript) {
                chrome.scripting.executeScript({
                    target: { tabId: details.tabId, frameIds: [details.frameId] },
                    world: 'MAIN',
                    files: ['inject.js'],
                    injectImmediately: true
                }).catch(() => {});
            }
        }
    });
}

chrome.runtime.onInstalled.addListener(initExtension);
chrome.runtime.onStartup.addListener(initExtension);
initExtension();
