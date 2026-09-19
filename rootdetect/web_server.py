"""
Embedded Web Dashboard and REST API Server for Root Detect.
Zero external server dependencies (pure standard library HTTP server).
Clean, minimalist design without stickers/emojis, with categorized OS device tree.
"""

import os
import sys
import json
import time
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any

from rootdetect.profiles import ProfileManager
from rootdetect.browser import launch_browser, find_installed_browsers, get_default_browser_path
from rootdetect.proxy import check_proxy, parse_proxy_string
from rootdetect.fingerprints import OS_PRESETS, GPU_PRESETS, DESKTOP_RESOLUTIONS, generate_fingerprint_for_preset
from rootdetect.downloader import AVAILABLE_BROWSERS, download_browser

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Root Detect · Dashboard</title>
    <link rel="icon" type="image/png" href="/favicon.png">
    <style>
        :root {
            --bg: #09090b;
            --card: #121215;
            --card-hover: #18181b;
            --border: #27272a;
            --border-hover: #3f3f46;
            --text: #f4f4f5;
            --muted: #a1a1aa;
            --accent: #22c55e;
            --danger: #ef4444;
            --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --mono: "SF Mono", Menlo, Monaco, Consolas, monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--font);
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            line-height: 1.5;
            font-size: 14px;
        }

        header {
            padding: 16px 28px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #09090be0;
            backdrop-filter: blur(12px);
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .logo-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo {
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text);
        }
        .tag {
            font-size: 11px;
            color: var(--muted);
            font-family: var(--mono);
            border: 1px solid var(--border);
            padding: 2px 7px;
            border-radius: 4px;
        }

        .actions-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn {
            background: #27272a;
            color: var(--text);
            border: 1px solid var(--border);
            padding: 7px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }
        .btn:hover {
            background: #3f3f46;
            border-color: #52525b;
        }
        .btn-primary {
            background: var(--text);
            color: #09090b;
            border-color: var(--text);
            font-weight: 600;
        }
        .btn-primary:hover {
            background: #e4e4e7;
            border-color: #e4e4e7;
        }
        .btn-success {
            background: var(--accent);
            color: #000;
            border-color: var(--accent);
            font-weight: 600;
        }
        .btn-success:hover {
            background: #16a34a;
            border-color: #16a34a;
        }
        .btn-danger {
            background: transparent;
            color: var(--danger);
            border-color: transparent;
        }
        .btn-danger:hover {
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--danger);
        }
        .btn-sm {
            padding: 4px 10px;
            font-size: 12px;
        }

        main {
            flex: 1;
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            padding: 28px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 28px;
        }
        .stat-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }
        .stat-label {
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 4px;
        }
        .stat-val {
            font-size: 22px;
            font-weight: 600;
            font-family: var(--mono);
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .section-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
        }

        .table-wrap {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }
        th, td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
        }
        th {
            font-size: 12px;
            font-weight: 500;
            color: var(--muted);
            background: rgba(255, 255, 255, 0.02);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: var(--card-hover); }

        .profile-title {
            font-weight: 600;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .os-badge {
            font-size: 11px;
            font-family: var(--mono);
            padding: 2px 6px;
            border-radius: 4px;
            background: #27272a;
            color: var(--muted);
        }
        .os-badge.mobile {
            background: #1e1b4b;
            color: #a5b4fc;
        }
        .proxy-cell {
            font-family: var(--mono);
            font-size: 12px;
            color: #d4d4d8;
        }
        .empty-state {
            padding: 48px 20px;
            text-align: center;
            color: var(--muted);
        }

        /* Modal */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(6px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }
        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }
        .modal {
            background: #121215;
            border: 1px solid var(--border);
            border-radius: 10px;
            width: 90%;
            max-width: 640px;
            max-height: 90vh;
            overflow-y: auto;
            padding: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }
        .modal-title {
            font-size: 16px;
            font-weight: 600;
        }
        .close-btn {
            background: transparent;
            border: none;
            color: var(--muted);
            font-size: 20px;
            cursor: pointer;
        }
        .close-btn:hover { color: var(--text); }

        .form-group {
            margin-bottom: 16px;
        }
        .form-label {
            display: block;
            font-size: 12px;
            font-weight: 500;
            color: var(--muted);
            margin-bottom: 6px;
        }
        .form-input, .form-select {
            width: 100%;
            padding: 9px 12px;
            background: #18181b;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-size: 13px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.15s;
        }
        .form-input:focus, .form-select:focus {
            border-color: #71717a;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        /* Categorized OS Tree */
        .category-tabs {
            display: flex;
            gap: 6px;
            margin-bottom: 12px;
            overflow-x: auto;
            padding-bottom: 4px;
        }
        .cat-tab {
            background: #18181b;
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            color: var(--muted);
            transition: all 0.15s;
            white-space: nowrap;
        }
        .cat-tab:hover {
            color: var(--text);
            border-color: #52525b;
        }
        .cat-tab.active {
            background: #27272a;
            color: var(--text);
            border-color: var(--text);
        }

        .device-sublist {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-bottom: 16px;
        }
        .device-item {
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 12px;
            cursor: pointer;
            background: #18181b;
            transition: all 0.15s;
        }
        .device-item:hover {
            border-color: #52525b;
        }
        .device-item.selected {
            border-color: var(--text);
            background: #27272a;
        }
        .dev-title {
            font-weight: 600;
            font-size: 13px;
            color: var(--text);
        }
        .dev-desc {
            font-size: 11px;
            color: var(--muted);
            margin-top: 2px;
        }

        /* Toast notification */
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #18181b;
            border: 1px solid var(--border);
            padding: 12px 18px;
            border-radius: 6px;
            color: var(--text);
            font-size: 13px;
            z-index: 150;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.2s ease;
        }
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-group">
            <img src="/logo.png" alt="Logo" style="width: 26px; height: 26px; border-radius: 6px; box-shadow: 0 0 10px rgba(34, 197, 94, 0.25);">
            <div class="logo">Root Detect</div>
            <span class="tag">AntiDetect Browser</span>
        </div>
        <div class="actions-group">
            <button class="btn" onclick="openBrowsersModal()">Браузеры</button>
            <button class="btn btn-primary" onclick="openCreateModal()">+ Новый профиль</button>
        </div>
    </header>

    <main>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Всего профилей</div>
                <div class="stat-val" id="stat-total">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">С прокси</div>
                <div class="stat-val" id="stat-proxy">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Мобильные (iOS/Android)</div>
                <div class="stat-val" id="stat-mobile">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Запусков всего</div>
                <div class="stat-val" id="stat-launches">0</div>
            </div>
        </div>

        <div class="section-header">
            <div class="section-title">Список профилей</div>
            <button class="btn btn-sm" onclick="loadProfiles()">Обновить</button>
        </div>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Имя профиля</th>
                        <th>Платформа / ОС</th>
                        <th>Прокси</th>
                        <th>GPU</th>
                        <th>Запуски</th>
                        <th style="text-align: right;">Действия</th>
                    </tr>
                </thead>
                <tbody id="profiles-tbody">
                    <tr><td colspan="6" class="empty-state">Загрузка...</td></tr>
                </tbody>
            </table>
        </div>
    </main>

    <!-- Modal Create Profile -->
    <div class="modal-overlay" id="modal-create">
        <div class="modal">
            <div class="modal-header">
                <div class="modal-title">Создание профиля</div>
                <button class="close-btn" onclick="closeModal('modal-create')">&times;</button>
            </div>
            
            <div class="form-group">
                <label class="form-label">Имя профиля</label>
                <input type="text" id="p-name" class="form-input" placeholder="Например: Buyer #1">
            </div>

            <div class="form-group">
                <label class="form-label">Операционная система и устройство</label>
                <!-- Category Tabs -->
                <div class="category-tabs" id="cat-tabs">
                    <div class="cat-tab active" onclick="switchCategory('windows', this)">Windows</div>
                    <div class="cat-tab" onclick="switchCategory('macos', this)">macOS</div>
                    <div class="cat-tab" onclick="switchCategory('ios', this)">iOS (Apple)</div>
                    <div class="cat-tab" onclick="switchCategory('android', this)">Android</div>
                    <div class="cat-tab" onclick="switchCategory('linux', this)">Linux</div>
                </div>

                <!-- Sub-Device Grid -->
                <div class="device-sublist" id="device-sublist">
                    <!-- Populated dynamically based on category -->
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Прокси (ip:port или http://user:pass@ip:port)</label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="p-proxy" class="form-input" placeholder="http://user:pass@1.2.3.4:8080">
                    <button class="btn btn-sm" onclick="testProxyInput()" type="button">Тест</button>
                </div>
                <div id="proxy-test-res" style="font-size: 11px; margin-top: 4px; font-family: var(--mono);"></div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Ядра CPU</label>
                    <select id="p-cores" class="form-select">
                        <option value="4">4 ядра</option>
                        <option value="6">6 ядер</option>
                        <option value="8" selected>8 ядер</option>
                        <option value="12">12 ядер</option>
                        <option value="16">16 ядер</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Память RAM</label>
                    <select id="p-ram" class="form-select">
                        <option value="8">8 GB</option>
                        <option value="16" selected>16 GB</option>
                        <option value="32">32 GB</option>
                        <option value="64">64 GB</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Заметки</label>
                <input type="text" id="p-notes" class="form-input" placeholder="Любые заметки">
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px;">
                <button class="btn" onclick="closeModal('modal-create')">Отмена</button>
                <button class="btn btn-primary" onclick="submitCreateProfile()">Создать профиль</button>
            </div>
        </div>
    </div>

    <!-- Modal Browsers -->
    <div class="modal-overlay" id="modal-browsers">
        <div class="modal">
            <div class="modal-header">
                <div class="modal-title">Управление браузерами</div>
                <button class="close-btn" onclick="closeModal('modal-browsers')">&times;</button>
            </div>
            
            <div class="form-label" style="margin-bottom: 10px;">Скачать чистый portable браузер:</div>
            <div id="browsers-download-list" style="display: flex; flex-direction: column; gap: 8px;">
                <!-- Populated via JS -->
            </div>

            <div style="margin-top: 20px; text-align: right;">
                <button class="btn" onclick="closeModal('modal-browsers')">Закрыть</button>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let currentCategory = 'windows';
        let selectedDeviceKey = 'windows_11';

        const deviceCatalog = {
            windows: [
                { key: 'windows_11', name: 'Windows 11', desc: 'NVIDIA RTX 4090 / Intel Iris' },
                { key: 'windows_10', name: 'Windows 10', desc: 'NVIDIA RTX 3080 / AMD' },
                { key: 'windows_8_1', name: 'Windows 8.1', desc: 'Legacy Windows x64' },
                { key: 'windows_7', name: 'Windows 7', desc: 'Legacy Windows NT 6.1' }
            ],
            macos: [
                { key: 'macos_15', name: 'macOS 15 (Sequoia)', desc: 'Apple M3 Max / Pro' },
                { key: 'macos_14', name: 'macOS 14 (Sonoma)', desc: 'Apple M2 Pro / M1' },
                { key: 'macos_13', name: 'macOS 13 (Ventura)', desc: 'Intel Iris Plus / AMD' }
            ],
            ios: [
                { key: 'ios_iphone_16', name: 'iPhone 16 Pro', desc: 'iOS 18 Safari Touch · A17 Pro' },
                { key: 'ios_iphone_15', name: 'iPhone 15 Pro Max', desc: 'iOS 17.5 Safari Touch · A16' },
                { key: 'ios_ipad_pro', name: 'iPad Pro 12.9', desc: 'iPadOS Retina · Apple GPU' }
            ],
            android: [
                { key: 'android_samsung_s24', name: 'Samsung Galaxy S24 Ultra', desc: 'Snapdragon 8 Gen 3 · Adreno 750' },
                { key: 'android_pixel_8', name: 'Google Pixel 8 Pro', desc: 'Google Tensor G3 · Mali G715' },
                { key: 'android_xiaomi_14', name: 'Xiaomi 14 Pro', desc: 'Snapdragon 8 Gen 3 · Adreno 750' }
            ],
            linux: [
                { key: 'linux', name: 'Ubuntu 24.04 / Debian', desc: 'Linux x86_64 Desktop' }
            ]
        };

        function switchCategory(cat, el) {
            currentCategory = cat;
            document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
            if (el) {
                el.classList.add('active');
            } else {
                const tabs = document.querySelectorAll('.cat-tab');
                tabs.forEach(t => {
                    if (t.innerText.toLowerCase().includes(cat.toLowerCase())) {
                        t.classList.add('active');
                    }
                });
            }
            
            // Auto select first device in category
            const devices = deviceCatalog[cat] || [];
            if (devices.length > 0) {
                selectedDeviceKey = devices[0].key;
            }
            renderDeviceSublist();
        }

        function renderDeviceSublist() {
            const list = document.getElementById('device-sublist');
            const devices = deviceCatalog[currentCategory] || [];
            list.innerHTML = devices.map(d => `
                <div class="device-item ${d.key === selectedDeviceKey ? 'selected' : ''}" onclick="selectDevice('${d.key}')">
                    <div class="dev-title">${d.name}</div>
                    <div class="dev-desc">${d.desc}</div>
                </div>
            `).join('');
        }

        function selectDevice(key) {
            selectedDeviceKey = key;
            renderDeviceSublist();
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 3000);
        }

        function openCreateModal() {
            document.getElementById('p-name').value = 'profile-' + Math.floor(Math.random() * 1000);
            document.getElementById('p-proxy').value = '';
            document.getElementById('p-notes').value = '';
            document.getElementById('proxy-test-res').innerText = '';
            currentCategory = 'windows';
            selectedDeviceKey = 'windows_11';
            
            document.querySelectorAll('.cat-tab').forEach((t, i) => {
                if (i === 0) t.classList.add('active');
                else t.classList.remove('active');
            });
            renderDeviceSublist();
            document.getElementById('modal-create').classList.add('active');
        }

        function openBrowsersModal() {
            loadAvailableBrowsers();
            document.getElementById('modal-browsers').classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        async function loadProfiles() {
            try {
                const res = await fetch('/api/profiles');
                const data = await res.json();
                const tbody = document.getElementById('profiles-tbody');

                document.getElementById('stat-total').innerText = data.length;
                document.getElementById('stat-proxy').innerText = data.filter(p => p.proxy_raw).length;
                document.getElementById('stat-mobile').innerText = data.filter(p => p.fingerprint && p.fingerprint.is_mobile).length;
                document.getElementById('stat-launches').innerText = data.reduce((acc, p) => acc + (p.launch_count || 0), 0);

                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Нет созданных профилей. Создайте первый профиль по кнопке выше.</td></tr>';
                    return;
                }

                tbody.innerHTML = data.map((p, idx) => {
                    const isMobile = p.fingerprint && p.fingerprint.is_mobile;
                    const osName = p.fingerprint ? p.fingerprint.os : 'Unknown';
                    const gpu = p.fingerprint ? p.fingerprint.webgl_renderer : 'Default';
                    const gpuShort = gpu.includes('NVIDIA') ? 'NVIDIA RTX' : (gpu.includes('Apple') ? 'Apple Silicon' : (gpu.includes('Adreno') ? 'Adreno GPU' : (gpu.includes('Mali') ? 'ARM Mali' : gpu.substring(0, 18))));
                    const proxy = p.proxy_raw ? p.proxy_raw : '<span style="color: var(--muted);">direct</span>';

                    return `
                        <tr>
                            <td>
                                <div class="profile-title">
                                    <span>${p.name}</span>
                                    <span style="font-size: 11px; color: var(--muted); font-family: var(--mono);">${p.id}</span>
                                </div>
                            </td>
                            <td>
                                <span class="os-badge ${isMobile ? 'mobile' : ''}">${osName}</span>
                            </td>
                            <td class="proxy-cell">${proxy}</td>
                            <td style="color: var(--muted); font-size: 12px;">${gpuShort}</td>
                            <td style="font-family: var(--mono); font-size: 12px;">${p.launch_count || 0}</td>
                            <td style="text-align: right;">
                                <button class="btn btn-sm btn-success" onclick="launchProfile('${p.id}')">Запустить</button>
                                <button class="btn btn-sm btn-danger" onclick="deleteProfile('${p.id}', '${p.name}')">Удалить</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } catch (e) {
                console.error(e);
            }
        }

        async function launchProfile(id) {
            showToast('Запуск браузера...');
            const res = await fetch(`/api/profiles/${id}/launch`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                showToast('Браузер открыт');
                loadProfiles();
            } else {
                alert('Ошибка запуска: ' + data.message);
            }
        }

        async function deleteProfile(id, name) {
            if (!confirm(`Удалить профиль "${name}"?`)) return;
            await fetch(`/api/profiles/${id}`, { method: 'DELETE' });
            showToast('Профиль удален');
            loadProfiles();
        }

        async function submitCreateProfile() {
            const name = document.getElementById('p-name').value;
            const proxy = document.getElementById('p-proxy').value;
            const notes = document.getElementById('p-notes').value;
            const cores = parseInt(document.getElementById('p-cores').value);
            const ram = parseInt(document.getElementById('p-ram').value);

            const payload = {
                name: name,
                os_type: selectedDeviceKey,
                proxy_str: proxy,
                notes: notes,
                cores: cores,
                memory: ram
            };

            const res = await fetch('/api/profiles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                closeModal('modal-create');
                showToast('Профиль создан');
                loadProfiles();
            } else {
                alert('Ошибка создания профиля');
            }
        }

        async function testProxyInput() {
            const proxy = document.getElementById('p-proxy').value;
            const resDiv = document.getElementById('proxy-test-res');
            if (!proxy) {
                resDiv.innerText = 'Введите прокси';
                resDiv.style.color = '#ef4444';
                return;
            }
            resDiv.innerText = 'Проверка...';
            resDiv.style.color = '#a1a1aa';

            const res = await fetch('/api/check_proxy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proxy: proxy })
            });
            const data = await res.json();
            if (data.status === 'online') {
                resDiv.innerHTML = `<span style="color: #22c55e;">Online</span> | IP: ${data.ip} | ${data.country} (${data.latency_ms}ms)`;
            } else {
                resDiv.innerHTML = `<span style="color: #ef4444;">Offline</span>: ${data.message}`;
            }
        }

        async function loadAvailableBrowsers() {
            const container = document.getElementById('browsers-download-list');
            container.innerHTML = '<div style="color: var(--muted); padding: 12px 0;">Загрузка списка браузеров...</div>';
            
            try {
                const res = await fetch('/api/browsers');
                const data = await res.json();
                
                if (!data.available || data.available.length === 0) {
                    container.innerHTML = '<div style="color: var(--muted);">Нет доступных браузеров</div>';
                    return;
                }

                container.innerHTML = data.available.map(b => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #18181b; padding: 10px 14px; border-radius: 6px; border: 1px solid var(--border);">
                        <div>
                            <div style="font-weight: 600; font-size: 13px;">${b.name}</div>
                            <div style="font-size: 11px; color: var(--muted);">${b.desc}</div>
                        </div>
                        <button class="btn btn-sm" onclick="downloadBrowserItem('${b.id}', '${b.name}', this)">Скачать</button>
                    </div>
                `).join('');
            } catch (err) {
                container.innerHTML = `<div style="color: var(--danger);">Ошибка загрузки: ${err.message}</div>`;
            }
        }

        async function downloadBrowserItem(id, name, btn) {
            if (btn) {
                btn.disabled = true;
                btn.innerText = 'Загрузка...';
            }
            showToast(`Загрузка ${name}... Пожалуйста, подождите 30-60 сек`);
            try {
                const res = await fetch('/api/browsers/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ browser_id: id })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`${name} успешно установлен!`);
                    loadAvailableBrowsers();
                    loadProfiles();
                } else {
                    alert('Ошибка скачивания браузера: ' + (data.message || 'Не удалось скачать'));
                }
            } catch (err) {
                alert('Ошибка сети при скачивании браузера: ' + err.message);
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerText = 'Скачать';
                }
            }
        }

        // Init
        renderDeviceSublist();
        loadProfiles();
    </script>
</body>
</html>
"""

class WebRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Silence standard HTTP logs

    def _send_json(self, data, status=200):
        try:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def _send_html(self, html, status=200):
        try:
            body = html.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/' or path == '/index.html':
            self._send_html(HTML_TEMPLATE)
            return

        if path in ['/logo.png', '/favicon.png', '/favicon.ico']:
            if getattr(sys, '_MEIPASS', None):
                asset_file = Path(sys._MEIPASS) / "rootdetect" / "assets" / "logo.png"
            else:
                asset_file = Path(__file__).parent / "assets" / "logo.png"
            if asset_file.exists():
                with open(asset_file, "rb") as f:
                    img_data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Content-Length', str(len(img_data)))
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(img_data)
                return

        if path == '/api/profiles':
            mgr = ProfileManager()
            self._send_json(mgr.list_profiles())
            return

        if path == '/api/browsers':
            installed = find_installed_browsers()
            self._send_json({
                "installed": installed,
                "available": AVAILABLE_BROWSERS
            })
            return

        self._send_json({"error": "Not Found"}, status=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(length).decode('utf-8') if length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except Exception:
            body = {}

        if path == '/api/profiles':
            mgr = ProfileManager()
            name = body.get('name', 'Profile')
            os_type = body.get('os_type', 'windows_11')
            proxy_str = body.get('proxy_str')
            notes = body.get('notes', '')
            cores = body.get('cores')
            memory = body.get('memory')

            fp = generate_fingerprint_for_preset(
                preset_key=os_type,
                custom_cores=cores,
                custom_memory=memory
            )
            created = mgr.create_profile(
                name=name,
                os_type=os_type,
                proxy_str=proxy_str,
                notes=notes,
                custom_fp=fp
            )
            self._send_json(created, status=201)
            return

        if path.startswith('/api/profiles/') and path.endswith('/launch'):
            p_id = path.split('/')[3]
            mgr = ProfileManager()
            p = mgr.get_profile(p_id)
            if not p:
                self._send_json({"success": False, "message": "Профиль не найден"}, status=404)
                return
            success, msg = launch_browser(p)
            if success:
                mgr.mark_launched(p_id)
            self._send_json({"success": success, "message": msg})
            return

        if path == '/api/check_proxy':
            proxy_str = body.get('proxy', '')
            res = check_proxy(proxy_str)
            self._send_json(res)
            return

        if path == '/api/browsers/download':
            browser_id = body.get('browser_id', 'chrome_cft')
            path_res = download_browser(browser_id)
            if path_res:
                self._send_json({"success": True, "path": path_res})
            else:
                self._send_json({"success": False, "message": "Ошибка скачивания браузера"}, status=500)
            return

        self._send_json({"error": "Not Found"}, status=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith('/api/profiles/'):
            p_id = path.split('/')[3]
            mgr = ProfileManager()
            deleted = mgr.delete_profile(p_id)
            self._send_json({"success": deleted})
            return
        self._send_json({"error": "Not Found"}, status=404)

class ThreadedHTTPServer(HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc_type = sys.exc_info()[0]
        if exc_type in (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return
        super().handle_error(request, client_address)

def start_web_server(port: int = 5050) -> HTTPServer:
    for p in range(port, port + 20):
        try:
            server = ThreadedHTTPServer(('127.0.0.1', p), WebRequestHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            return server
        except OSError:
            continue
    raise RuntimeError("Не удалось найти свободный порт для веб-сервера")


