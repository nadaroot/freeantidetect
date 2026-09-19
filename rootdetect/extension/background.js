/**
 * Root Detect Extension Background Service Worker
 * Handles WebRTC leak prevention and proxy authentication
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

// 2. Proxy Authentication Handler
// If proxy requires credentials, config will be loaded from chrome.storage or fetched
chrome.runtime.onInstalled.addListener(async () => {
    try {
        const url = chrome.runtime.getURL('config.json');
        const resp = await fetch(url);
        if (resp.ok) {
            const config = await resp.json();
            if (config.proxy_auth && config.proxy_auth.username && config.proxy_auth.password) {
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
        // No proxy credentials configured or config.json optional
    }
});
