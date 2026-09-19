"""
Terminal User Interface (TUI) and CLI entrypoint for Root Detect.
Minimalist, clean typography and monochrome aesthetic.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich import box
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

from rootdetect.profiles import ProfileManager
from rootdetect.browser import find_installed_browsers, launch_browser, get_default_browser_path
from rootdetect.proxy import check_proxy, parse_proxy_string
from rootdetect.fingerprints import generate_random_fingerprint

console = Console() if HAVE_RICH else None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    if HAVE_RICH:
        console.print()
        console.print("[bold white]root-detect[/bold white] [dim]· v1.0.0[/dim]")
        console.print("[dim]локальный автономный антидетект-браузер[/dim]")
        console.print("[dim]──────────────────────────────────────────────────────────[/dim]")
        console.print()
    else:
        print("\nroot-detect · v1.0.0")
        print("локальный автономный антидетект-браузер")
        print("──────────────────────────────────────────────────────────\n")

def render_profiles_table(manager: ProfileManager):
    profiles = manager.list_profiles()
    if not profiles:
        if HAVE_RICH:
            console.print("[dim]• Профилей пока нет. Создайте первый профиль через пункт [2][/dim]\n")
        else:
            print("• Профилей пока нет. Создайте первый профиль через пункт [2]\n")
        return

    if HAVE_RICH:
        table = Table(
            box=box.SIMPLE_HEAD,
            border_style="dim",
            header_style="bold white",
            pad_edge=False
        )
        table.add_column("#", style="dim", justify="right", width=3)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Имя", style="bold white", min_width=16)
        table.add_column("ОС", style="dim", width=10)
        table.add_column("Прокси", style="white", min_width=22)
        table.add_column("GPU", style="dim", width=16)
        table.add_column("Старт", justify="right", style="dim", width=6)

        for idx, p in enumerate(profiles, 1):
            fp = p.get("fingerprint", {})
            proxy_raw = p.get("proxy_raw")
            if proxy_raw:
                proxy_display = proxy_raw if len(proxy_raw) <= 24 else proxy_raw[:22] + ".."
            else:
                proxy_display = "[dim]direct[/dim]"

            gpu_str = fp.get("webgl_renderer", "Default")
            if "NVIDIA" in gpu_str:
                gpu_display = "NVIDIA RTX"
            elif "Apple" in gpu_str:
                gpu_display = "Apple Silicon"
            elif "AMD" in gpu_str:
                gpu_display = "AMD Radeon"
            elif "Intel" in gpu_str:
                gpu_display = "Intel Iris"
            else:
                gpu_display = gpu_str[:14]

            os_name = fp.get("os", "auto").capitalize()

            table.add_row(
                str(idx),
                p["id"],
                p["name"],
                os_name,
                proxy_display,
                gpu_display,
                str(p.get("launch_count", 0))
            )
        console.print(table)
        console.print()
    else:
        print("  #   ID         ИМЯ              ОС         ПРОКСИ")
        print("──────────────────────────────────────────────────────────")
        for idx, p in enumerate(profiles, 1):
            proxy = p.get("proxy_raw") or "direct"
            fp = p.get("fingerprint", {})
            print(f"  {idx:<3} {p['id']:<10} {p['name']:<16} {fp.get('os', 'auto'):<10} {proxy}")
        print()

from rootdetect.fingerprints import generate_random_fingerprint, generate_fingerprint_for_preset, OS_PRESETS, GPU_PRESETS

def handle_create_profile(manager: ProfileManager):
    clear_screen()
    print_header()
    if HAVE_RICH:
        console.print("[bold white]Создание профиля[/bold white]\n")
        name = Prompt.ask("[white]Имя профиля[/white]", default=f"profile-{int(time.time()) % 1000}")
        
        console.print("\n[dim]Платформа и эмуляция устройства:[/dim]")
        preset_list = [
            ("windows_11", "Windows 11", "Desktop · NVIDIA RTX / AMD / Intel"),
            ("windows_10", "Windows 10", "Desktop · NVIDIA / AMD"),
            ("windows_8_1", "Windows 8.1", "Desktop · Legacy"),
            ("windows_7", "Windows 7", "Desktop · Legacy"),
            ("macos_15", "macOS 15 (Sequoia)", "Desktop · Apple M3 Max / Pro"),
            ("macos_14", "macOS 14 (Sonoma)", "Desktop · Apple M2 / M1"),
            ("ios_iphone_16", "iOS (iPhone 16 Pro)", "Mobile · Safari Touch / Apple GPU"),
            ("ios_iphone_15", "iOS (iPhone 15 Pro Max)", "Mobile · Safari Touch / Apple GPU"),
            ("ios_ipad_pro", "iPadOS (iPad Pro 12.9)", "Tablet · Mobile Safari / Apple GPU"),
            ("android_samsung_s24", "Android (Samsung Galaxy S24 Ultra)", "Mobile · Snapdragon 8 Gen 3 / Adreno 750"),
            ("android_pixel_8", "Android (Google Pixel 8 Pro)", "Mobile · Google Tensor G3 / Mali G715"),
            ("android_xiaomi_14", "Android (Xiaomi 14 Pro)", "Mobile · Snapdragon 8 Gen 3 / Adreno 750"),
            ("linux", "Linux (Ubuntu / Debian)", "Desktop · x86_64")
        ]

        for idx, (key, title, desc) in enumerate(preset_list, 1):
            console.print(f"  [white][{idx:>2}][/white] {title:<36} [dim]{desc}[/dim]")
        console.print("  [dim][ 0] Автоматический выбор[/dim]\n")

        valid_choices = [str(i) for i in range(len(preset_list) + 1)]
        os_choice = Prompt.ask("[dim]root-detect[/dim] [white]›[/white]", choices=valid_choices, default="1")

        if os_choice == "0":
            selected_preset_key = "windows_11"
        else:
            selected_preset_key = preset_list[int(os_choice) - 1][0]

        # Mode: Quick vs Custom
        console.print("\n[dim]Режим настройки:[/dim]")
        console.print("  [white][1][/white] Быстрый (автоматические реалистичные параметры)")
        console.print("  [white][2][/white] Детальный (выбор GPU, ядер CPU, RAM, разрешения экрана)")
        mode_choice = Prompt.ask("\n[dim]root-detect[/dim] [white]›[/white]", choices=["1", "2"], default="1")

        custom_cores = None
        custom_memory = None
        custom_res = None

        if mode_choice == "2":
            console.print("\n[dim]Количество ядер CPU (hardwareConcurrency):[/dim]")
            cores_input = Prompt.ask("Ядра CPU", choices=["2", "4", "6", "8", "12", "16", "24", "32"], default="8")
            custom_cores = int(cores_input)

            console.print("\n[dim]Объем оперативной памяти RAM (GB):[/dim]")
            mem_input = Prompt.ask("RAM (GB)", choices=["4", "6", "8", "12", "16", "24", "32", "64"], default="16")
            custom_memory = int(mem_input)

            console.print("\n[dim]Разрешение экрана:[/dim]")
            console.print("  [white]1[/white] · 1920x1080 (Full HD)")
            console.print("  [white]2[/white] · 2560x1440 (2K QHD)")
            console.print("  [white]3[/white] · 1440x900 (MacBook)")
            console.print("  [white]4[/white] · 3840x2160 (4K UHD)")
            console.print("  [white]5[/white] · Авто по выбранному устройству")
            res_choice = Prompt.ask("Выбор", choices=["1", "2", "3", "4", "5"], default="5")
            if res_choice == "1":
                custom_res = (1920, 1080)
            elif res_choice == "2":
                custom_res = (2560, 1440)
            elif res_choice == "3":
                custom_res = (1440, 900)
            elif res_choice == "4":
                custom_res = (3840, 2160)

        console.print("\n[dim]Прокси (Enter если без прокси, формат ip:port или ip:port:user:pass):[/dim]")
        proxy_input = Prompt.ask("Прокси", default="")
        notes = Prompt.ask("Заметка к профилю", default="")

        fp = generate_fingerprint_for_preset(
            preset_key=selected_preset_key,
            custom_cores=custom_cores,
            custom_memory=custom_memory,
            custom_res=custom_res
        )
    else:
        name = input("Имя: ") or f"profile-{int(time.time()) % 1000}"
        selected_preset_key = "windows_11"
        proxy_input = input("Прокси: ")
        notes = input("Заметка: ")
        fp = generate_fingerprint_for_preset(selected_preset_key)

    new_profile = manager.create_profile(
        name=name,
        os_type=selected_preset_key,
        proxy_str=proxy_input.strip() or None,
        notes=notes,
        custom_fp=fp
    )

    if HAVE_RICH:
        console.print(f"\n[green]• Профиль '{new_profile['name']}' ({fp['os']}) успешно создан[/green]")
        time.sleep(1.2)

def handle_launch_profile(manager: ProfileManager):
    profiles = manager.list_profiles()
    if not profiles:
        if HAVE_RICH:
            console.print("[dim]• Нет доступных профилей для запуска[/dim]")
            time.sleep(1.2)
        return

    render_profiles_table(manager)
    if HAVE_RICH:
        choice = Prompt.ask("[white]Номер или ID профиля для запуска[/white] [dim](0 — отмена)[/dim]")
    else:
        choice = input("Номер или ID профиля (0 — отмена): ")

    if choice == "0" or not choice.strip():
        return

    selected_profile = None
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(profiles):
            selected_profile = profiles[idx - 1]
    
    if not selected_profile:
        selected_profile = manager.get_profile(choice.strip())

    if not selected_profile:
        if HAVE_RICH:
            console.print("[red]• Профиль не найден[/red]")
            time.sleep(1.0)
        return

    if HAVE_RICH:
        console.print(f"[dim]• Запуск браузера для профиля '{selected_profile['name']}'...[/dim]")
    
    success, msg = launch_browser(selected_profile)
    if success:
        manager.mark_launched(selected_profile["id"])
        if HAVE_RICH:
            console.print(f"[green]• Браузер открыт в изолированном окне[/green]")
            time.sleep(1.5)
    else:
        if HAVE_RICH:
            console.print(f"[red]• Ошибка: {msg}[/red]")
            Prompt.ask("\nНажмите Enter для продолжения...")

def handle_check_proxy(manager: ProfileManager):
    profiles = manager.list_profiles()
    if not profiles:
        return

    render_profiles_table(manager)
    choice = Prompt.ask("[white]Номер профиля[/white]") if HAVE_RICH else input("Номер профиля: ")
    if not choice.isdigit():
        return
    idx = int(choice)
    if not (1 <= idx <= len(profiles)):
        return

    p = profiles[idx - 1]
    proxy_str = p.get("proxy_raw")
    if not proxy_str:
        if HAVE_RICH:
            console.print("[dim]• У этого профиля прямое подключение (без прокси)[/dim]")
            time.sleep(1.2)
        return

    if HAVE_RICH:
        console.print(f"[dim]• Проверка {proxy_str}...[/dim]")
    
    res = check_proxy(proxy_str)
    if HAVE_RICH:
        if res.get("status") == "online":
            panel_text = (
                f"[bold white]Статус:[/bold white] [green]Online[/green]\n"
                f"[bold white]IP:[/bold white] {res.get('ip')}\n"
                f"[bold white]Локация:[/bold white] {res.get('city')}, {res.get('country')} ({res.get('country_code')})\n"
                f"[bold white]Провайдер:[/bold white] {res.get('isp')}\n"
                f"[bold white]Пинг:[/bold white] {res.get('latency_ms')} ms"
            )
            console.print(Panel(panel_text, title="[dim]Прокси[/dim]", border_style="dim", expand=False))
        else:
            panel_text = (
                f"[bold white]Статус:[/bold white] [red]Offline[/red]\n"
                f"[bold white]Ошибка:[/bold white] {res.get('message', 'Неизвестная ошибка')}\n"
                f"[bold white]Задержка:[/bold white] {res.get('latency_ms')} ms"
            )
            console.print(Panel(panel_text, title="[dim]Прокси[/dim]", border_style="dim", expand=False))
        Prompt.ask("\nНажмите Enter для возврата...")

def handle_delete_profile(manager: ProfileManager):
    profiles = manager.list_profiles()
    if not profiles:
        return

    render_profiles_table(manager)
    choice = Prompt.ask("[white]Номер профиля для удаления[/white] [dim](0 — отмена)[/dim]") if HAVE_RICH else input("Номер: ")
    if choice == "0" or not choice.isdigit():
        return

    idx = int(choice)
    if not (1 <= idx <= len(profiles)):
        return

    p = profiles[idx - 1]
    if HAVE_RICH:
        if Confirm.ask(f"[dim]Удалить профиль '{p['name']}'?[/dim]", default=False):
            manager.delete_profile(p["id"])
            console.print(f"[green]• Профиль '{p['name']}' удален[/green]")
            time.sleep(1.0)
    else:
        ans = input(f"Удалить '{p['name']}'? (y/n): ")
        if ans.lower() == 'y':
            manager.delete_profile(p["id"])

def handle_edit_profile(manager: ProfileManager):
    profiles = manager.list_profiles()
    if not profiles:
        return

    render_profiles_table(manager)
    choice = Prompt.ask("[white]Номер профиля[/white]") if HAVE_RICH else input("Номер: ")
    if not choice.isdigit():
        return
    idx = int(choice)
    if not (1 <= idx <= len(profiles)):
        return

    p = profiles[idx - 1]
    if HAVE_RICH:
        console.print(f"\n[dim]Редактирование: {p['name']}[/dim]")
        new_name = Prompt.ask("Имя", default=p["name"])
        new_proxy = Prompt.ask("Прокси", default=p.get("proxy_raw", ""))
        new_notes = Prompt.ask("Заметка", default=p.get("notes", ""))
        
        manager.update_profile(p["id"], {
            "name": new_name,
            "proxy_raw": new_proxy,
            "notes": new_notes
        })
        console.print("[green]• Профиль обновлен[/green]")
        time.sleep(1.0)

from rootdetect.downloader import download_browser, AVAILABLE_BROWSERS

def handle_browsers_info():
    clear_screen()
    print_header()
    browsers = find_installed_browsers()
    if HAVE_RICH:
        console.print("[bold white]Управление браузерами[/bold white]\n")
        table = Table(box=box.SIMPLE_HEAD, border_style="dim", header_style="bold white")
        table.add_column("Браузер", style="white")
        table.add_column("Исполняемый файл", style="dim")
        
        for b in browsers:
            table.add_row(b["name"], b["path"])
        
        console.print(table)
        default_p = get_default_browser_path()
        console.print(f"\n[dim]По умолчанию:[/dim] {default_p}\n")
        
        console.print("[dim]Скачать portable браузер:[/dim]")
        for idx, b in enumerate(AVAILABLE_BROWSERS, 1):
            console.print(f"  [white][{idx}][/white] {b['name']} [dim]— {b['desc']}[/dim]")
        console.print("  [dim][0] Назад[/dim]\n")
        
        valid_choices = [str(i) for i in range(len(AVAILABLE_BROWSERS) + 1)]
        choice = Prompt.ask("[dim]root-detect[/dim] [white]›[/white]", choices=valid_choices, default="0")
        
        if choice != "0" and choice.isdigit():
            chosen_browser = AVAILABLE_BROWSERS[int(choice) - 1]
            path = download_browser(chosen_browser["id"])
            if path:
                console.print(f"\n[green]• {chosen_browser['name']} успешно установлен: {path}[/green]")
            else:
                console.print(f"\n[red]• Не удалось скачать {chosen_browser['name']}[/red]")
            time.sleep(1.8)
    else:
        print("Браузеры в системе:")
        for b in browsers:
            print(f"- {b['name']}: {b['path']}")
        print("\nСкачать браузер:")
        for idx, b in enumerate(AVAILABLE_BROWSERS, 1):
            print(f"{idx}. {b['name']}")
        print("0. Назад")
        c = input("Выбор: ")
        if c.isdigit() and 1 <= int(c) <= len(AVAILABLE_BROWSERS):
            download_browser(AVAILABLE_BROWSERS[int(c) - 1]["id"])



def main():
    manager = ProfileManager()

    while True:
        clear_screen()
        print_header()
        render_profiles_table(manager)

        if HAVE_RICH:
            console.print("[dim]Действия:[/dim]")
            console.print("  [white][1][/white] Запустить профиль")
            console.print("  [white][2][/white] Создать профиль")
            console.print("  [white][3][/white] Редактировать")
            console.print("  [white][4][/white] Проверить прокси")
            console.print("  [white][5][/white] Удалить профиль")
            console.print("  [white][6][/white] Браузеры в системе")
            console.print("  [dim][0] Выход[/dim]\n")

            choice = Prompt.ask("[dim]root-detect[/dim] [white]›[/white]", choices=["0", "1", "2", "3", "4", "5", "6"], default="1")
        else:
            print("1. Запустить профиль")
            print("2. Создать профиль")
            print("3. Редактировать")
            print("4. Проверить прокси")
            print("5. Удалить профиль")
            print("6. Браузеры в системе")
            print("0. Выход")
            choice = input("root-detect > ")

        if choice == "1":
            handle_launch_profile(manager)
        elif choice == "2":
            handle_create_profile(manager)
        elif choice == "3":
            handle_edit_profile(manager)
        elif choice == "4":
            handle_check_proxy(manager)
        elif choice == "5":
            handle_delete_profile(manager)
        elif choice == "6":
            handle_browsers_info()
        elif choice == "0":
            clear_screen()
            print("Сессия завершена.")
            sys.exit(0)

if __name__ == "__main__":
    main()
