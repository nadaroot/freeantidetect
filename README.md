# FreeAntidetect (Root Detect)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-blue.svg)](https://python.org/)
[![Platform: Cross-Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/nadaroot/freeantidetect)

Автономный консольный антидетект-браузер (CLI & TUI) для изолированного управления профилями, прокси, фингерпринтами и автоматической загрузкой браузеров без облачных серверов, баз данных и подписок.

---

## Особенности

* **Минималистичный консольный TUI**: Управление всеми профилями, прокси и настройками прямо в терминале через аккуратное текстовое меню.
* **Два браузерных движка (Chromium & Gecko)**:
  * Поддержка **Google Chrome, Brave, Ungoogled Chromium, Thorium, Mozilla Firefox, LibreWolf**.
  * Автоматический поиск установленных браузеров в системе (macOS, Windows, Linux).
* **Встроенный загрузчик portable браузеров**:
  * Скачивание и распаковка официальных чистых сборок браузеров в 1 клик прямо из меню (Google Chrome for Testing, Ungoogled, Brave, Thorium, Firefox, LibreWolf).
* **Эмуляция любых ОС и устройств**:
  * **Windows**: 11, 10, 8.1, 7.
  * **macOS**: 15 (Sequoia), 14 (Sonoma), 13 (Ventura).
  * **iOS**: iPhone 16 Pro, iPhone 15 Pro Max, iPad Pro 12.9 (с сенсорным вводом `maxTouchPoints = 5`, Retina масштабированием и Apple GPU).
  * **Android**: Samsung Galaxy S24 Ultra, Google Pixel 8 Pro, Xiaomi 14 Pro (с Snapdragon 8 Gen 3, Adreno 750 / Mali G715 и Touch эмуляцией).
  * **Linux**: Ubuntu / Debian x86_64.
* **Глубокая подмена фингерпринтов (Stealth Engine)**:
  * Скрытие следов автоматизации (`navigator.webdriver = false`).
  * Эмуляция видеокарт WebGL (Apple Silicon M1/M2/M3, Apple GPU, NVIDIA RTX 4080/4090, AMD Radeon, Intel Iris, Qualcomm Adreno, ARM Mali).
  * Уникальный детерминированный микро-шум для Canvas и AudioContext под каждый профиль.
  * Тонкая настройка: ядер CPU (`hardwareConcurrency`), RAM (`deviceMemory`), разрешения экрана, локали и User-Agent.
  * Защита от утечки реального IP через WebRTC (`disable_non_proxied_udp` / `media.peerconnection.enabled = false`).
* **Поддержка прокси**:
  * Протоколы: HTTP, HTTPS, SOCKS4, SOCKS5.
  * Форматы: `ip:port`, `ip:port:user:pass`, `protocol://user:pass@ip:port`.
  * Автоматическая авторизация прокси на лету.
  * Встроенный чекер доступности, внешнего IP, страны и задержки (пинг).
* **100% Автономность**:
  * Работает полностью локально и оффлайн.
  * Запуск в 1 команду: `antidetect`.
  * Возможность сборки в единый автономный исполняемый файл (`antidetect.exe` / бинарник).

---

## Быстрый старт

### Способ 1: Установка как консольной команды (Рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone https://github.com/nadaroot/freeantidetect.git
cd freeantidetect
```

2. Установите пакет в систему:
```bash
pip install -e .
```

3. Запустите в терминале:
```bash
antidetect
```

---

### Способ 2: Прямой запуск без установки

```bash
pip install -r requirements.txt
python3 antidetect.py
```

---

## Сборка в один файл (.exe / binary)

Для создания полностью автономного файла без необходимости устанавливать Python:

```bash
python3 build_standalone.py
```
Готовый файл будет скомпилирован в папку `dist/antidetect` (или `dist/antidetect.exe` на Windows).

---

## Использование

После запуска команды `antidetect` откроется интерактивное меню:

1. **Запустить профиль**: Выберите профиль — мгновенно откроется окно браузера с изолированными куками, прокси и подмененными отпечатками.
2. **Создать профиль**: Быстрое создание профиля в 1 клик или детальный режим с ручным выбором ОС (Win/Mac/iOS/Android), GPU, CPU, RAM и разрешения.
3. **Редактировать**: Изменение имени, прокси или заметок.
4. **Проверить прокси**: Тестирование скорости отклика, страны и реального IP выбранного профиля.
5. **Удалить профиль**: Полная очистка данных и сессий профиля.
6. **Браузеры в системе**: Просмотр установленных браузеров и скачивание portable версий в 1 клик (Chrome, Ungoogled, Brave, Thorium, Firefox, LibreWolf).

---

## Лицензия

Распространяется под лицензией [MIT](./LICENSE).
