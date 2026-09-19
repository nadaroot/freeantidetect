(function() {
    'use strict';
    let injected = false;
    function doInject() {
        if (injected) return true;
        try {
            const container = document.head || document.documentElement || document.body;
            if (container) {
                const script = document.createElement('script');
                script.src = chrome.runtime.getURL('inject.js');
                script.async = false;
                container.insertBefore(script, container.firstChild);
                injected = true;
                return true;
            }
        } catch (e) {}
        return false;
    }

    if (!doInject()) {
        const observer = new MutationObserver((mutations, obs) => {
            if (doInject()) {
                obs.disconnect();
            }
        });
        observer.observe(document, { childList: true, subtree: true });
        document.addEventListener('readystatechange', () => {
            if (doInject()) observer.disconnect();
        }, { once: true });
    }
})();
