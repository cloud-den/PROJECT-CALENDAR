import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import calendar
from datetime import datetime
import os

EVENTS_FILE = "events.txt"
FUNNY_FILE = "funny_days.txt"

events = {}
funny_events = {}
open_windows = {}
last_width = 0
last_height = 0

def load_events():
    if not os.path.exists(EVENTS_FILE):
        return
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "|" in line:
                date_str, event_text = line.split("|", 1)
                events.setdefault(date_str, []).append(event_text)

def load_funny_events():
    if not os.path.exists(FUNNY_FILE):
        return
    with open(FUNNY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "|" in line:
                md_str, event_text = line.split("|", 1)
                funny_events.setdefault(md_str, []).append(event_text)

def save_events():
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        for date_str, ev_list in events.items():
            for event in ev_list:
                f.write(f"{date_str}|{event}\n")

def draw_calendar(year, month):
    for widget in calendar_frame.winfo_children():
        widget.destroy()

    
    root.update_idletasks()
    window_width = root.winfo_width() if root.winfo_width() > 0 else 400
    window_height = root.winfo_height() if root.winfo_height() > 0 else 400
    button_width = max(4, window_width // 70)
    font_size = max(8, window_width // 40)

    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    for i, day in enumerate(days):
        tk.Label(calendar_frame, text=day, font=('Arial', font_size, 'bold'),
                 width=button_width, bg="#151515", fg="white").grid(row=0, column=i, sticky="nsew")

    today = datetime.today()
    month_calendar = calendar.monthcalendar(year, month)

    for r, week in enumerate(month_calendar, start=1):
        for c, day in enumerate(week):
            if day != 0:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                md_key = f"{month:02d}-{day:02d}"

                has_event = date_str in events
                has_funny = md_key in funny_events

                if today.year == year and today.month == month and today.day == day:
                    bg_color = "#00aa00"
                elif has_event and has_funny:
                    bg_color = "#660099"
                elif has_event:
                    bg_color = "#003399"
                elif has_funny:
                    bg_color = "#cc6600"
                else:
                    bg_color = "#1a1a1a"

                btn_text = str(day)
                if has_event:
                    btn_text += "*"
                if has_funny:
                    btn_text += "🎉"

                btn = tk.Button(calendar_frame, text=btn_text, width=button_width,
                                font=('Arial', font_size), bg=bg_color, fg="white",
                                activebackground="#1a5eff", relief=tk.FLAT,
                                command=lambda d=day: select_date(d, month, year))
                btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

                def on_enter(e, button=btn):
                    button['background'] = "#1a5eff"
                def on_leave(e, button=btn, original_bg=bg_color):
                    button['background'] = original_bg

                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)


    for i in range(7):
        calendar_frame.grid_columnconfigure(i, weight=1, uniform="calendar")
    for i in range(len(month_calendar) + 1):
        calendar_frame.grid_rowconfigure(i, weight=1, uniform="calendar")

def select_date(day, month, year):
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    md_key = f"{month:02d}-{day:02d}"
    funny_list = funny_events.get(md_key, [])

    if date_str in open_windows and open_windows[date_str].winfo_exists():
        open_windows[date_str].lift()
        return

    window = tk.Toplevel(root)
    window.title(f"События на {day:02d}.{month:02d}.{year}")
    window.configure(bg="#151515")
    window_width = max(300, root.winfo_width() // 2)
    window_height = max(300, root.winfo_height() // 2)
    window.geometry(f"{window_width}x{window_height}")

    window.update_idletasks()
    x = (window.winfo_screenwidth() - window_width) // 2
    y = (window.winfo_screenheight() - window_height) // 2
    window.geometry(f"+{x}+{y}")

    def on_close():
        if date_str in open_windows:
            del open_windows[date_str]
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(window, text=f"{day:02d}.{month:02d}.{year}", font=('Arial', 12, 'bold'),
             bg="#151515", fg="white").pack(pady=5)

    list_frame = tk.Frame(window, bg="#151515")
    list_frame.pack(fill=tk.BOTH, expand=True)

    def refresh_list():
        for widget in list_frame.winfo_children():
            widget.destroy()

        current_events = events.get(date_str, [])
        all_events = funny_list + current_events

        for i, event in enumerate(all_events):
            row = tk.Frame(list_frame, bg="#151515")
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=event, anchor="w", bg="#151515", fg="white").pack(side=tk.LEFT, expand=True)

            if i < len(funny_list):
                tk.Label(row, text="🎉", bg="#151515", fg="#ffaa00").pack(side=tk.RIGHT)
            else:
                real_index = i - len(funny_list)
                tk.Button(row, text="🗑", command=lambda idx=real_index: delete_event(idx), width=3,
                          bg="#cc3333", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT)

    def add_event():
        new_event = simpledialog.askstring("Новое событие", f"{day:02d}.{month:02d}.{year}\nВведите событие:")
        if new_event:
            events.setdefault(date_str, []).append(new_event)
            save_events()
            on_close()
            select_date(day, month, year)
            update_calendar()
            selected_label.config(text=f"Добавлено: {new_event}")

    def delete_event(index):
        current_events = events.get(date_str, [])
        if index < len(current_events) and messagebox.askyesno("Удалить", f"Удалить: {current_events[index]}?"):
            removed = current_events.pop(index)
            if not current_events:
                events.pop(date_str)
            save_events()
            refresh_list()
            update_calendar()
            selected_label.config(text=f"Удалено: {removed}")

    refresh_list()

    tk.Button(window, text="Добавить событие", command=add_event,
              bg="#1a5eff", fg="white", relief=tk.FLAT).pack(pady=10)

    selected_label.config(text=f"Управление событиями: {day:02d}.{month:02d}.{year}")

def update_calendar():
    year = int(year_var.get())
    month = month_names.index(month_var.get()) + 1
    draw_calendar(year, month)

def on_resize(event):
    global last_width, last_height
    current_width = root.winfo_width()
    current_height = root.winfo_height()
    if current_width != last_width or current_height != last_height:
        last_width, last_height = current_width, current_height
        update_calendar()

root = tk.Tk()
root.title("Календарь с событиями")
root.configure(bg="#0a0a0a")
root.geometry("400x400")
root.minsize(300, 300)

root.update_idletasks()
x = (root.winfo_screenwidth() - 400) // 2
y = (root.winfo_screenheight() - 400) // 2
root.geometry(f"+{x}+{y}")

controls_frame = tk.Frame(root, bg="#0a0a0a")
controls_frame.pack(pady=10, fill=tk.X)

month_names = list(calendar.month_name)[1:]
month_var = tk.StringVar(value=month_names[datetime.now().month - 1])
month_box = ttk.Combobox(controls_frame, values=month_names,
                         textvariable=month_var, state="readonly", width=12)
month_box.grid(row=0, column=0, padx=5)

year_var = tk.StringVar(value=str(datetime.now().year))
year_box = ttk.Combobox(controls_frame, values=[str(i) for i in range(1900, 2101)],
                        textvariable=year_var, state="readonly", width=7)
year_box.grid(row=0, column=1, padx=5)

tk.Button(controls_frame, text="Показать", command=update_calendar,
          bg="#1a5eff", fg="white", relief=tk.FLAT).grid(row=0, column=2, padx=5)

calendar_frame = tk.Frame(root, bg="#151515")
calendar_frame.pack(fill=tk.BOTH, expand=True)

selected_label = tk.Label(root, text="Выберите дату", font=("Arial", 12), bg="#0a0a0a", fg="white")
selected_label.pack(pady=10, fill=tk.X)


root.bind("<Configure>", on_resize)

load_events()
load_funny_events()
draw_calendar(int(year_var.get()), month_names.index(month_var.get()) + 1)

root.mainloop()