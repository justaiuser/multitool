import tkinter as tk
import subprocess
import psutil

root = tk.Tk() # окно приложения
root.title("Multitool")
root.geometry("300x400")

notepad_on = tk.BooleanVar(value=False) # привязана к чекбоксу, если чекбокс отмечен, то процесс ping запущен
notepad_process = None # процесс ping

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
            except (psutil.NoSuchProcess, psutil.AccesDenied):
                pass
print(is_running("Lightshot.exe"))
notepad_checkbutton.pack()
root.after(1000, check_process)

root.mainloop()