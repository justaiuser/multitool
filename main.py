import tkinter as tk
import subprocess
import psutil

root = tk.Tk() # окно приложения
root.title("Multitool")
root.geometry("300x400")

cpu_label = tk.Label(root, text="CPU: -")
cpu_label.pack()

vram_label = tk.Label(root, text="GPU: -")
vram_label.pack()

ram_label = tk.Label(root, text="RAM: -")
ram_label.pack()


notepad_on = tk.BooleanVar(value=False) # привязана к чекбоксу, если чекбокс отмечен, то процесс ping запущен
notepad_process = None # процесс ping

def update_cpu():
    cpu = psutil.cpu_percent(interval=None)
    cpu_label.config(text=f"CPU: {cpu:.0f}%")
    root.after(1000, update_cpu)  # повторить через 1 сек

def update_ram():
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)
    ram_label.config(text=f"RAM: {used_gb:.1f}/{total_gb:.1f} GB ({mem.percent:.0f}%)")
    root.after(1000, update_ram)

def update_vram():
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-Counter '\\GPU Adapter Memory(*)\\Dedicated Usage').CounterSamples | ForEach-Object { $_.CookedValue }"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        values = [
            float(line.strip())
            for line in result.stdout.splitlines()
            if line.strip()
        ]
        used_bytes = max(values) if values else 0
        used_gb = used_bytes / (1024 ** 3)
        total_gb = VRAM_TOTAL_GB
        percent = (used_gb / total_gb) * 100
        vram_label.config(text=f"VRAM: {used_gb:.1f}/{total_gb:.1f} GB ({percent:.0f}%)")
    except Exception:
        vram_label.config(text="VRAM: N/A")
    root.after(1000, update_vram)  # повторить через 1 сек — даже после ошибки

# WMI AdapterRAM часто врёт (>4 GB режется до ~4). Для известных карт — свои значения.
KNOWN_VRAM_GB = {
    "7600": 8,
}

def get_amd_vram_total_gb():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Json",
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        import json
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
        for gpu in data:
            name = (gpu.get("Name") or "").lower()
            if "amd" not in name and "radeon" not in name:
                continue
            for key, gb in KNOWN_VRAM_GB.items():
                if key in name:
                    return float(gb)
            ram = gpu.get("AdapterRAM")
            if ram:
                gb = ram / (1024 ** 3)
                # ~4 GB из WMI на картах >4 GB — не доверяем
                if 3.9 <= gb <= 4.1:
                    return None
                return gb
        return None
    except Exception:
        return None

VRAM_TOTAL_GB = get_amd_vram_total_gb() or 8.0

def get_amd_gpu_name():
    try:
        result=subprocess.run([
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'AMD|Radeon' } | Select-Object -First 1 -ExpandProperty Name)"
        ],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
        )
        name = result.stdout.strip()
        return name or "AMD GPU"
    except Exception:
        return "AMD GPU"
vram_label.config(text=f"GPU: {get_amd_gpu_name()}")

def notepad_on_click():
    global notepad_process # global сообщает Python, что внутри функции мы хотим работать с переменной, объявленной вне функции
    if notepad_on.get():
        notepad_process = subprocess.Popen([
            r"C:\Program Files (x86)\Skillbrains\lightshot\lightshot.exe"
            ])
    else: # если чекбокс не отмечен, то процесс ping завершается
        kill_by_name("Lightshot.exe")
        notepad_process = None

notepad_checkbutton = tk.Checkbutton(root, text="Скриншотер",variable=notepad_on, command=notepad_on_click)

def check_process():
    # global notepad_process
    running = is_running("Lightshot.exe")
    notepad_on.set(running)
    root.after(1000, check_process)

def is_running(process_name: str) -> bool:
    for proc in psutil.process_iter(["name"]):
        name = proc.info["name"]
        if name and name.lower() == process_name.lower():
            return True
    return False

def kill_by_name(process_name: str) -> None:
    for proc in psutil.process_iter(["name"]):
        name = proc.info["name"]
        if name and name.lower() == process_name.lower():
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
print(is_running("Lightshot.exe"))
notepad_checkbutton.pack()
root.after(1000, check_process)
root.after(1000, update_cpu)
root.after(1000, update_vram)
root.after(1000, update_ram)

root.mainloop()