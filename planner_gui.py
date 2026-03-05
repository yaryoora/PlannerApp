import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import json
import os
import csv
from datetime import datetime

# File to store tasks
TASKS_FILE = "tasks.json"
SETTINGS_FILE = "settings.json"

# Colors and styling - Light theme (default)
THEMES = {
    "light": {
        "PRIMARY_COLOR": "#4A90E2",
        "SECONDARY_COLOR": "#F5F5F5",
        "ACCENT_COLOR": "#50C878",
        "WARNING_COLOR": "#FF6B6B",
        "TEXT_COLOR": "#333333",
        "BG_COLOR": "#FFFFFF",
        "LISTBOX_BG": "#F5F5F5",
        "LISTBOX_SELECT": "#4A90E2"
    },
    "dark": {
        "PRIMARY_COLOR": "#5DADE2",
        "SECONDARY_COLOR": "#2C3E50",
        "ACCENT_COLOR": "#58D68D",
        "WARNING_COLOR": "#E74C3C",
        "TEXT_COLOR": "#ECF0F1",
        "BG_COLOR": "#34495E",
        "LISTBOX_BG": "#2C3E50",
        "LISTBOX_SELECT": "#5DADE2"
    }
}

current_theme = "light"

# Load and save tasks
def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_settings():
    """Save user settings"""
    settings = {
        "theme": current_theme,
        "sort_by": sort_var.get(),
        "filter_by": filter_var.get()
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except:
        pass  # Silently fail if settings can't be saved

def load_settings():
    """Load user settings"""
    global current_theme
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                current_theme = settings.get("theme", "light")
                return settings
        except:
            pass
    return {"theme": "light", "sort_by": "none", "filter_by": "all"}

def check_due_dates():
    """Check for tasks due today or overdue and show notifications"""
    today = datetime.now().date()
    due_today = []
    overdue = []
    
    for task in tasks:
        if task.get("due_date") and not task["completed"]:
            try:
                due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                if due_date == today:
                    due_today.append(task)
                elif due_date < today:
                    overdue.append(task)
            except:
                continue
    
    if overdue:
        messagebox.showwarning("⚠️ Overdue Tasks", 
                             f"You have {len(overdue)} overdue task(s)!\n\n" + 
                             "\n".join([f"• {t['text']} (Due: {t['due_date']})" for t in overdue[:5]]))
    
    if due_today:
        messagebox.showinfo("📅 Tasks Due Today", 
                           f"You have {len(due_today)} task(s) due today:\n\n" + 
                           "\n".join([f"• {t['text']}" for t in due_today]))

def import_csv():
    """Import tasks from CSV file"""
    from tkinter import filedialog
    
    filename = filedialog.askopenfilename(
        title="Select CSV file to import",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not filename:
        return
    
    try:
        imported_count = 0
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                task = {
                    "text": row.get("text", "").strip(),
                    "completed": row.get("completed", "False").lower() == "true",
                    "due_date": row.get("due_date", "").strip() or None,
                    "priority": row.get("priority", "medium").strip()
                }
                if task["text"]:  # Only add if text is not empty
                    tasks.append(task)
                    imported_count += 1
        
        if imported_count > 0:
            save_tasks()
            refresh_all_tabs()
            messagebox.showinfo("Success", f"Imported {imported_count} task(s) from {filename}")
            status_label.config(text=f"📥 Imported {imported_count} tasks", fg=ACCENT_COLOR)
        else:
            messagebox.showwarning("Warning", "No valid tasks found in the CSV file.")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")

def switch_theme():
    """Switch between light and dark themes"""
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    
    # Update colors
    theme = THEMES[current_theme]
    globals().update(theme)
    
    # Update UI elements
    root.configure(bg=BG_COLOR)
    sidebar.configure(bg=PRIMARY_COLOR)
    content_area.configure(bg=BG_COLOR)
    
    # Update all frames and labels
    for widget in root.winfo_children():
        if isinstance(widget, tk.LabelFrame):
            widget.configure(bg=BG_COLOR, fg=PRIMARY_COLOR)
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=BG_COLOR)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=BG_COLOR, fg=TEXT_COLOR)
    
    # Update listbox
    task_listbox.configure(bg=LISTBOX_BG, selectbackground=LISTBOX_SELECT)
    
    # Update buttons
    for button in [add_button, complete_button, edit_button, remove_button, 
                   export_button, import_button, notify_button, clear_button]:
        try:
            if "Mark Complete" in button.cget("text"):
                button.configure(bg=ACCENT_COLOR)
            elif "Edit Task" in button.cget("text"):
                button.configure(bg=PRIMARY_COLOR)
            elif "Remove Task" in button.cget("text") or "Cancel" in button.cget("text"):
                button.configure(bg=WARNING_COLOR)
            elif "Export" in button.cget("text"):
                button.configure(bg="#3498DB")
            elif "Import" in button.cget("text"):
                button.configure(bg="#27AE60")
            elif "Check Due Dates" in button.cget("text"):
                button.configure(bg="#E67E22")
            elif "Clear All" in button.cget("text"):
                button.configure(bg="#FF9500")
            else:
                button.configure(bg=SECONDARY_COLOR, fg=TEXT_COLOR)
        except:
            pass
    
    # Update nav buttons
    for name, btn in nav_buttons.items():
        if current_page == page_frames.get(name):
            btn.configure(bg=ACCENT_COLOR, relief=tk.SUNKEN)
        else:
            btn.configure(bg=PRIMARY_COLOR, relief=tk.FLAT)
    
    save_settings()
    status_label.config(text=f"🎨 Switched to {current_theme} theme", fg=PRIMARY_COLOR)
    
    # Refresh current page content
    if current_page == page_frames["dashboard"]:
        create_dashboard()
    elif current_page == page_frames["calendar"]:
        create_calendar_page()
    elif current_page == page_frames["settings"]:
        create_settings_page()

# Task functions
def add_task():
    task_text = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    priority = priority_var.get()

    if not task_text:
        messagebox.showwarning("Warning", "Task cannot be empty.")
        return

    # Validate due date if provided
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

    task = {
        "text": task_text,
        "completed": False,
        "due_date": due_date if due_date else None,
        "priority": priority
    }

    tasks.append(task)
    save_tasks()
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    priority_var.set("medium")
    refresh_all_tabs()
    status_label.config(text=f"✓ Task added: {task_text}", fg=ACCENT_COLOR)



def clear_tasks():
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks?"):
        tasks.clear()
        save_tasks()
        refresh_all_tabs()
        status_label.config(text="🧹 All tasks cleared", fg=WARNING_COLOR)

def search_tasks():
    search_term = search_entry.get().strip().lower()
    if not search_term:
        refresh_all_tabs()
        return

    # Filter tasks based on search
    filtered_tasks = [t for t in tasks if search_term in t["text"].lower()]
    
    # Clear all canvases
    for canvas, scrollable in task_canvases.values():
        for widget in scrollable.winfo_children():
            widget.destroy()
    
    # Display filtered tasks in all tab
    display_tasks_as_cards(filtered_tasks, task_canvases["all"][1])
    
    # Show pending and completed as empty for search
    display_tasks_as_cards([], task_canvases["pending"][1])
    display_tasks_as_cards([], task_canvases["completed"][1])
    
    status_label.config(text=f"🔍 Found {len(filtered_tasks)} task(s) matching '{search_term}'", fg=PRIMARY_COLOR)

def get_current_filtered_tasks():
    """Get currently displayed tasks considering filters"""
    sort_by = sort_var.get()
    filter_by = filter_var.get()
    
    filtered_tasks = []
    for t in tasks:
        if filter_by == "completed" and not t["completed"]:
            continue
        elif filter_by == "pending" and t["completed"]:
            continue
        elif filter_by.startswith("priority_") and t.get("priority", "medium") != filter_by[9:]:
            continue
        filtered_tasks.append(t)
    
    # Sort tasks
    if sort_by == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_tasks.sort(key=lambda x: (priority_order.get(x.get("priority", "medium"), 1), x.get("due_date") or "9999-99-99"))
    elif sort_by == "due_date":
        filtered_tasks.sort(key=lambda x: (x.get("due_date") is None, x.get("due_date") or "9999-99-99"))
    elif sort_by == "status":
        filtered_tasks.sort(key=lambda x: (not x["completed"], x.get("due_date") or "9999-99-99"))
    
    return filtered_tasks



def export_tasks():
    """Export tasks to CSV file"""
    if not tasks:
        messagebox.showwarning("Warning", "No tasks to export.")
        return
    
    try:
        filename = f"tasks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['text', 'completed', 'due_date', 'priority']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for task in tasks:
                writer.writerow({
                    'text': task['text'],
                    'completed': task['completed'],
                    'due_date': task.get('due_date', ''),
                    'priority': task.get('priority', 'medium')
                })
        
        messagebox.showinfo("Success", f"Tasks exported to {filename}")
        status_label.config(text=f"📤 Tasks exported to {filename}", fg=ACCENT_COLOR)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export tasks: {str(e)}")

# Dashboard content
def create_dashboard():
    # Clear existing widgets
    for widget in dashboard_frame.winfo_children():
        widget.destroy()
    
    # Title
    tk.Label(dashboard_frame, text="🏠 Dashboard", font=("Segoe UI", 20, "bold"),
             bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(20,10))
    
    # Summary stats
    stats_frame = tk.LabelFrame(dashboard_frame, text="📊 Summary", font=("Segoe UI", 14, "bold"),
                               bg=BG_COLOR, fg=PRIMARY_COLOR, padx=20, pady=15)
    stats_frame.pack(fill=tk.X, padx=20, pady=10)
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["completed"])
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = 0
    today = datetime.now().date()
    for t in tasks:
        if t.get("due_date") and not t["completed"]:
            try:
                due_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                if due_date < today:
                    overdue_tasks += 1
            except:
                pass
    
    # Stats grid
    tk.Label(stats_frame, text=f"Total Tasks: {total_tasks}", font=("Segoe UI", 12),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Label(stats_frame, text=f"✅ Completed: {completed_tasks}", font=("Segoe UI", 12),
             bg=BG_COLOR, fg=ACCENT_COLOR).grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Label(stats_frame, text=f"⏳ Pending: {pending_tasks}", font=("Segoe UI", 12),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk.Label(stats_frame, text=f"⚠️ Overdue: {overdue_tasks}", font=("Segoe UI", 12),
             bg=BG_COLOR, fg=WARNING_COLOR).grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    # Pending tasks
    pending_frame = tk.LabelFrame(dashboard_frame, text="⏳ Pending Tasks", font=("Segoe UI", 14, "bold"),
                                 bg=BG_COLOR, fg=PRIMARY_COLOR, padx=20, pady=15)
    pending_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    pending_listbox = tk.Listbox(pending_frame, height=8, font=("Segoe UI", 10),
                                bg=SECONDARY_COLOR, selectbackground=PRIMARY_COLOR,
                                selectforeground="white", relief=tk.FLAT)
    pending_listbox.pack(fill=tk.BOTH, expand=True)
    
    for t in tasks:
        if not t["completed"]:
            priority = t.get("priority", "medium")
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
            due = f" 📅 {t['due_date']}" if t.get('due_date') else ""
            pending_listbox.insert(tk.END, f"{priority_icon} {t['text']}{due}")
    
    # Today's tasks
    today_frame = tk.LabelFrame(dashboard_frame, text="📅 Today's Tasks", font=("Segoe UI", 14, "bold"),
                               bg=BG_COLOR, fg=PRIMARY_COLOR, padx=20, pady=15)
    today_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    today_listbox = tk.Listbox(today_frame, height=8, font=("Segoe UI", 10),
                              bg=SECONDARY_COLOR, selectbackground=PRIMARY_COLOR,
                              selectforeground="white", relief=tk.FLAT)
    today_listbox.pack(fill=tk.BOTH, expand=True)
    
    for t in tasks:
        if t.get("due_date"):
            try:
                due_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                if due_date == today:
                    status = "✅" if t["completed"] else "⏳"
                    priority = t.get("priority", "medium")
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
                    today_listbox.insert(tk.END, f"{status} {priority_icon} {t['text']}")
            except:
                pass
    
    if today_listbox.size() == 0:
        today_listbox.insert(tk.END, "No tasks due today! 🎉")

# Calendar page content
def create_calendar_page():
    # Clear existing widgets
    for widget in calendar_frame.winfo_children():
        widget.destroy()
    
    # Header
    tk.Label(calendar_frame, text="📅 Task Calendar", font=("Segoe UI", 20, "bold"),
             bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(20,10))
    
    # Create calendar display
    calendar_display_frame = tk.Frame(calendar_frame, bg=BG_COLOR)
    calendar_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Group tasks by due date
    tasks_by_date = {}
    tasks_without_date = []
    
    for task in tasks:
        due_date = task.get('due_date')
        if due_date:
            if due_date not in tasks_by_date:
                tasks_by_date[due_date] = []
            tasks_by_date[due_date].append(task)
        else:
            tasks_without_date.append(task)
    
    # Sort dates
    sorted_dates = sorted(tasks_by_date.keys())
    
    # Display tasks
    text_widget = scrolledtext.ScrolledText(calendar_display_frame, wrap=tk.WORD, font=("Segoe UI", 10),
                                           bg=SECONDARY_COLOR, height=25)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Configure tags for styling
    text_widget.tag_configure("date_header", font=("Segoe UI", 12, "bold"), foreground=PRIMARY_COLOR)
    text_widget.tag_configure("task_completed", foreground=ACCENT_COLOR)
    text_widget.tag_configure("task_pending", foreground=TEXT_COLOR)
    text_widget.tag_configure("high_priority", background="#FFE6E6")
    text_widget.tag_configure("medium_priority", background="#FFF9E6")
    text_widget.tag_configure("low_priority", background="#E6FFE6")
    
    # Show tasks with due dates
    for date in sorted_dates:
        text_widget.insert(tk.END, f"\n📅 {date}\n", "date_header")
        text_widget.insert(tk.END, "="*50 + "\n")
        
        for task in tasks_by_date[date]:
            status = "✅" if task["completed"] else "⏳"
            priority = task.get("priority", "medium")
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
            
            task_text = f"  {status} {priority_icon} {task['text']}\n"
            
            # Apply priority background color
            if priority == "high":
                text_widget.insert(tk.END, task_text, "high_priority")
            elif priority == "medium":
                text_widget.insert(tk.END, task_text, "medium_priority")
            else:
                text_widget.insert(tk.END, task_text, "low_priority")
    
    # Show tasks without due dates
    if tasks_without_date:
        text_widget.insert(tk.END, f"\n📋 Tasks without due dates\n", "date_header")
        text_widget.insert(tk.END, "="*50 + "\n")
        
        for task in tasks_without_date:
            status = "✅" if task["completed"] else "⏳"
            priority = task.get("priority", "medium")
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
            
            task_text = f"  {status} {priority_icon} {task['text']}\n"
            
            if priority == "high":
                text_widget.insert(tk.END, task_text, "high_priority")
            elif priority == "medium":
                text_widget.insert(tk.END, task_text, "medium_priority")
            else:
                text_widget.insert(tk.END, task_text, "low_priority")
    
    text_widget.config(state=tk.DISABLED)

# Settings page content
def create_settings_page():
    # Clear existing widgets
    for widget in settings_frame.winfo_children():
        widget.destroy()
    
    # Title
    tk.Label(settings_frame, text="⚙️ Settings", font=("Segoe UI", 20, "bold"),
             bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(20,10))
    
    # Theme settings
    theme_frame = tk.LabelFrame(settings_frame, text="🎨 Theme", font=("Segoe UI", 14, "bold"),
                               bg=BG_COLOR, fg=PRIMARY_COLOR, padx=20, pady=15)
    theme_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(theme_frame, text="Current Theme:", font=("Segoe UI", 12),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    theme_var = tk.StringVar(value=current_theme)
    light_radio = tk.Radiobutton(theme_frame, text="☀️ Light", variable=theme_var, value="light",
                                bg=BG_COLOR, font=("Segoe UI", 10), command=lambda: switch_theme_from_settings("light"))
    light_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    dark_radio = tk.Radiobutton(theme_frame, text="🌙 Dark", variable=theme_var, value="dark",
                               bg=BG_COLOR, font=("Segoe UI", 10), command=lambda: switch_theme_from_settings("dark"))
    dark_radio.grid(row=0, column=2, padx=10, pady=5, sticky="w")
    
    # Notification settings
    notify_frame = tk.LabelFrame(settings_frame, text="🔔 Notifications", font=("Segoe UI", 14, "bold"),
                                bg=BG_COLOR, fg=PRIMARY_COLOR, padx=20, pady=15)
    notify_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(notify_frame, text="Check for due dates on startup:", font=("Segoe UI", 12),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    notify_on_startup = tk.BooleanVar(value=True)  # Default to True
    notify_check = tk.Checkbutton(notify_frame, variable=notify_on_startup, bg=BG_COLOR)
    notify_check.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    tk.Button(notify_frame, text="🔔 Check Due Dates Now", command=check_due_dates,
              bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5).grid(row=1, column=0, columnspan=2, pady=10)
    
    # Data management
    data_frame = tk.LabelFrame(settings_frame, text="💾 Data Management", font=("Segoe UI", 14, "bold"),
                              bg=BG_COLOR, fg=PRIMARY_COLOR, padx=20, pady=15)
    data_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Button(data_frame, text="📤 Export Tasks to CSV", command=export_tasks,
              bg="#3498DB", fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5).grid(row=0, column=0, padx=10, pady=5)
    
    tk.Button(data_frame, text="📥 Import Tasks from CSV", command=import_csv,
              bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5).grid(row=0, column=1, padx=10, pady=5)
    
    tk.Button(data_frame, text="🧹 Clear All Tasks", command=clear_tasks,
              bg=WARNING_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5).grid(row=1, column=0, columnspan=2, pady=10)

def switch_theme_from_settings(new_theme):
    global current_theme
    if new_theme != current_theme:
        switch_theme()
        # Recreate pages to apply theme
        create_dashboard()
        create_calendar_page()
        create_settings_page()



# Main app window
root = tk.Tk()
root.title("✨ TaskMaster - Smart Task Planner")
root.geometry("1000x700")
root.resizable(True, True)

# Load settings and apply theme
settings = load_settings()
current_theme = settings["theme"]
theme = THEMES[current_theme]
globals().update(theme)

# Apply theme to root
try:
    root.configure(bg=BG_COLOR)
except NameError:
    root.configure(bg="#FFFFFF")

# Set up styles
style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
style.configure("TLabel", font=("Segoe UI", 10), background=BG_COLOR)
style.configure("TEntry", font=("Segoe UI", 10), padding=5)

tasks = load_tasks()

# Global variables for UI elements
sort_var = tk.StringVar(value="none")
filter_var = tk.StringVar(value="all")

# Main container
main_container = tk.Frame(root, bg=BG_COLOR)
main_container.pack(fill=tk.BOTH, expand=True)

# Sidebar navigation
sidebar_width = 200
sidebar = tk.Frame(main_container, bg=PRIMARY_COLOR, width=sidebar_width)
sidebar.pack(side=tk.LEFT, fill=tk.Y)
sidebar.pack_propagate(False)

# Content area
content_area = tk.Frame(main_container, bg=BG_COLOR)
content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

nav_buttons = {}
current_page = None

def show_page(page_name):
    global current_page
    if current_page:
        current_page.pack_forget()
    page_frames[page_name].pack(fill=tk.BOTH, expand=True)
    current_page = page_frames[page_name]
    # Update nav button styles
    for name, btn in nav_buttons.items():
        if name == page_name:
            btn.configure(bg=ACCENT_COLOR, relief=tk.SUNKEN)
        else:
            btn.configure(bg=PRIMARY_COLOR, relief=tk.FLAT)
    
    # Create content for the page
    if page_name == "dashboard":
        create_dashboard()
    elif page_name == "tasks":
        create_tasks_page()
    elif page_name == "calendar":
        create_calendar_page()
    elif page_name == "settings":
        create_settings_page()

# Create navigation buttons in sidebar
nav_button_names = ["🏠 Dashboard", "📋 All Tasks", "📅 Calendar", "⚙️ Settings"]
nav_pages = ["dashboard", "tasks", "calendar", "settings"]

def on_hover_enter(btn):
    if btn != nav_buttons.get(current_page, None):
        btn.configure(bg="#5DADE2")  # Lighter blue on hover

def on_hover_leave(btn):
    if btn != nav_buttons.get(current_page, None):
        btn.configure(bg=PRIMARY_COLOR)

for i, (text, page) in enumerate(zip(nav_button_names, nav_pages)):
    btn = tk.Button(sidebar, text=text, command=lambda p=page: show_page(p),
                    bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
                    relief=tk.FLAT, padx=15, pady=12, anchor="w")
    btn.pack(fill=tk.X, padx=5, pady=2)
    btn.bind("<Enter>", lambda e, b=btn: on_hover_enter(b))
    btn.bind("<Leave>", lambda e, b=btn: on_hover_leave(b))
    nav_buttons[page] = btn

# Create page frames in content area
page_frames = {}

# Dashboard frame
dashboard_frame = tk.Frame(content_area, bg=BG_COLOR)
page_frames["dashboard"] = dashboard_frame

# Tasks frame
tasks_frame = tk.Frame(content_area, bg=BG_COLOR)
page_frames["tasks"] = tasks_frame

# Calendar frame
calendar_frame = tk.Frame(content_area, bg=BG_COLOR)
page_frames["calendar"] = calendar_frame

# Settings frame
settings_frame = tk.Frame(content_area, bg=BG_COLOR)
page_frames["settings"] = settings_frame

def create_tasks_page():
    global task_entry, due_date_entry, priority_var, search_entry, sort_var, status_label, task_canvases
    # Clear existing widgets
    for widget in tasks_frame.winfo_children():
        widget.destroy()
    
    # Create notebook for tabs
    notebook = ttk.Notebook(tasks_frame)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create tabs
    all_tab = tk.Frame(notebook, bg=BG_COLOR)
    pending_tab = tk.Frame(notebook, bg=BG_COLOR)
    completed_tab = tk.Frame(notebook, bg=BG_COLOR)
    
    notebook.add(all_tab, text="📋 All Tasks")
    notebook.add(pending_tab, text="⏳ Pending")
    notebook.add(completed_tab, text="✅ Completed")
    
    # Add input section to all_tab
    input_frame = tk.LabelFrame(all_tab, text="➕ Add New Task", font=("Segoe UI", 12, "bold"),
                               bg=BG_COLOR, fg=PRIMARY_COLOR, padx=15, pady=10)
    input_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Task input
    tk.Label(input_frame, text="Task Description:", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=5)
    task_entry = tk.Entry(input_frame, width=40, font=("Segoe UI", 10))
    task_entry.grid(row=0, column=1, padx=(10,0), pady=5)
    
    # Due date input
    tk.Label(input_frame, text="Due Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=1, column=0, sticky="w", pady=5)
    due_date_entry = tk.Entry(input_frame, width=40, font=("Segoe UI", 10))
    due_date_entry.grid(row=1, column=1, padx=(10,0), pady=5)
    
    # Priority selection
    tk.Label(input_frame, text="Priority:", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=5)
    priority_var = tk.StringVar(value="medium")
    priority_frame = tk.Frame(input_frame, bg=BG_COLOR)
    priority_frame.grid(row=2, column=1, sticky="w", padx=(10,0), pady=5)
    
    tk.Radiobutton(priority_frame, text="🔴 High", variable=priority_var, value="high",
                   bg=BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(priority_frame, text="🟡 Medium", variable=priority_var, value="medium",
                   bg=BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(priority_frame, text="🟢 Low", variable=priority_var, value="low",
                   bg=BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
    
    # Add button
    add_button = tk.Button(input_frame, text="✨ Add Task", command=add_task,
                          bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
                          padx=20, pady=5, relief=tk.RAISED, borderwidth=2)
    add_button.grid(row=3, column=0, columnspan=2, pady=15)
    
    # Search section
    search_frame = tk.LabelFrame(all_tab, text="🔍 Search & Sort", font=("Segoe UI", 12, "bold"),
                                bg=BG_COLOR, fg=PRIMARY_COLOR, padx=15, pady=10)
    search_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Search row
    tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=5)
    search_entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 10))
    search_entry.grid(row=0, column=1, padx=(10,0), pady=5)
    
    search_button = tk.Button(search_frame, text="🔍 Search", command=search_tasks,
                             bg=SECONDARY_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 10, "bold"),
                             padx=15, pady=3)
    search_button.grid(row=0, column=2, padx=(10,0), pady=5)
    
    # Sort row
    tk.Label(search_frame, text="Sort by:", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=1, column=0, sticky="w", pady=5)
    
    sort_frame = tk.Frame(search_frame, bg=BG_COLOR)
    sort_frame.grid(row=1, column=1, sticky="w", padx=(10,0), pady=5)
    
    tk.Radiobutton(sort_frame, text="None", variable=sort_var, value="none",
                   bg=BG_COLOR, font=("Segoe UI", 9), command=lambda: refresh_all_tabs()).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(sort_frame, text="📅 Due Date", variable=sort_var, value="due_date",
                   bg=BG_COLOR, font=("Segoe UI", 9), command=lambda: refresh_all_tabs()).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(sort_frame, text="🎯 Priority", variable=sort_var, value="priority",
                   bg=BG_COLOR, font=("Segoe UI", 9), command=lambda: refresh_all_tabs()).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(sort_frame, text="📊 Status", variable=sort_var, value="status",
                   bg=BG_COLOR, font=("Segoe UI", 9), command=lambda: refresh_all_tabs()).pack(side=tk.LEFT, padx=5)
    
    # Create scrollable canvas for cards
    def create_task_canvas(parent):
        canvas = tk.Canvas(parent, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return canvas, scrollable_frame
    
    # All tasks tab
    all_canvas, all_scrollable = create_task_canvas(all_tab)
    # Pending tasks tab
    pending_canvas, pending_scrollable = create_task_canvas(pending_tab)
    # Completed tasks tab
    completed_canvas, completed_scrollable = create_task_canvas(completed_tab)
    
    # Store references
    global task_canvases
    task_canvases = {
        "all": (all_canvas, all_scrollable),
        "pending": (pending_canvas, pending_scrollable),
        "completed": (completed_canvas, completed_scrollable)
    }
    
    # Refresh all tabs
    refresh_all_tabs()

def refresh_all_tabs():
    # Clear all canvases
    for canvas, scrollable in task_canvases.values():
        for widget in scrollable.winfo_children():
            widget.destroy()
    
    # Get sorted tasks
    sorted_tasks = get_current_filtered_tasks()
    
    # All tasks
    display_tasks_as_cards(sorted_tasks, task_canvases["all"][1])
    
    # Pending tasks
    pending_tasks = [t for t in sorted_tasks if not t["completed"]]
    display_tasks_as_cards(pending_tasks, task_canvases["pending"][1])
    
    # Completed tasks
    completed_tasks = [t for t in sorted_tasks if t["completed"]]
    display_tasks_as_cards(completed_tasks, task_canvases["completed"][1])

def display_tasks_as_cards(task_list, parent_frame):
    priority_colors = {
        "high": "#FF6B6B",
        "medium": "#FFD93D",
        "low": "#6BCF7F"
    }
    
    for i, task in enumerate(task_list):
        # Card frame
        card = tk.Frame(parent_frame, bg="white", relief="raised", borderwidth=2)
        card.pack(fill=tk.X, padx=10, pady=5)
        
        # Priority border
        priority = task.get("priority", "medium")
        card.configure(highlightbackground=priority_colors.get(priority, "#FFD93D"), highlightthickness=3)
        
        # Task name
        name_label = tk.Label(card, text=task["text"], font=("Segoe UI", 12, "bold"),
                             bg="white", fg=TEXT_COLOR, anchor="w")
        name_label.pack(fill=tk.X, padx=10, pady=(10,5))
        
        # Due date
        due_text = f"📅 {task['due_date']}" if task.get('due_date') else "📅 No due date"
        due_label = tk.Label(card, text=due_text, font=("Segoe UI", 10),
                            bg="white", fg=TEXT_COLOR, anchor="w")
        due_label.pack(fill=tk.X, padx=10, pady=(0,5))
        
        # Bottom row: priority icon and buttons
        bottom_frame = tk.Frame(card, bg="white")
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
        priority_label = tk.Label(bottom_frame, text=f"{priority_icon} {priority.capitalize()}",
                                 font=("Segoe UI", 10), bg="white", fg=TEXT_COLOR)
        priority_label.pack(side=tk.LEFT)
        
        # Buttons frame
        buttons_frame = tk.Frame(bottom_frame, bg="white")
        buttons_frame.pack(side=tk.RIGHT)
        
        # Edit button
        edit_btn = tk.Button(buttons_frame, text="✏️", bg=PRIMARY_COLOR, fg="white",
                            font=("Segoe UI", 9, "bold"), padx=5, pady=2,
                            command=lambda t=task: edit_task_from_card(t))
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Remove button
        remove_btn = tk.Button(buttons_frame, text="🗑️", bg=WARNING_COLOR, fg="white",
                              font=("Segoe UI", 9, "bold"), padx=5, pady=2,
                              command=lambda t=task: remove_task_from_card(t))
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        # Complete toggle button
        if task["completed"]:
            btn_text = "✅ Completed"
            btn_bg = ACCENT_COLOR
        else:
            btn_text = "⏳ Mark Complete"
            btn_bg = SECONDARY_COLOR
        
        complete_btn = tk.Button(buttons_frame, text=btn_text,
                                bg=btn_bg, fg="white" if task["completed"] else TEXT_COLOR,
                                font=("Segoe UI", 9, "bold"), padx=10, pady=2,
                                command=lambda t=task: toggle_complete(t))
        complete_btn.pack(side=tk.LEFT, padx=2)

def toggle_complete(task):
    task["completed"] = not task["completed"]
    save_tasks()
    refresh_all_tabs()
    status_label.config(text=f"{'✅' if task['completed'] else '⏳'} Task status updated", fg=ACCENT_COLOR)

def edit_task_from_card(task):
    # Reuse the existing edit_task function but pass the task directly
    original_index = tasks.index(task)
    
    # Create edit dialog
    edit_window = tk.Toplevel(root)
    edit_window.title("✏️ Edit Task")
    edit_window.geometry("400x300")
    edit_window.configure(bg=BG_COLOR)
    edit_window.resizable(False, False)
    
    # Center the window
    edit_window.transient(root)
    edit_window.grab_set()
    
    # Edit form
    tk.Label(edit_window, text="Edit Task", font=("Segoe UI", 14, "bold"),
             bg=PRIMARY_COLOR, fg="white").pack(fill=tk.X, pady=(0,10))
    
    form_frame = tk.Frame(edit_window, bg=BG_COLOR, padx=20, pady=10)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    # Task text
    tk.Label(form_frame, text="Task Description:", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=0, column=0, sticky="w", pady=5)
    edit_task_entry = tk.Entry(form_frame, width=30, font=("Segoe UI", 10))
    edit_task_entry.grid(row=0, column=1, padx=(10,0), pady=5)
    edit_task_entry.insert(0, task["text"])
    
    # Due date
    tk.Label(form_frame, text="Due Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=1, column=0, sticky="w", pady=5)
    edit_due_entry = tk.Entry(form_frame, width=30, font=("Segoe UI", 10))
    edit_due_entry.grid(row=1, column=1, padx=(10,0), pady=5)
    if task.get("due_date"):
        edit_due_entry.insert(0, task["due_date"])
    
    # Priority
    tk.Label(form_frame, text="Priority:", font=("Segoe UI", 10, "bold"),
             bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=5)
    edit_priority_var = tk.StringVar(value=task.get("priority", "medium"))
    priority_edit_frame = tk.Frame(form_frame, bg=BG_COLOR)
    priority_edit_frame.grid(row=2, column=1, sticky="w", padx=(10,0), pady=5)
    
    tk.Radiobutton(priority_edit_frame, text="🔴 High", variable=edit_priority_var, value="high",
                   bg=BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(priority_edit_frame, text="🟡 Medium", variable=edit_priority_var, value="medium",
                   bg=BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(priority_edit_frame, text="🟢 Low", variable=edit_priority_var, value="low",
                   bg=BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
    
    def save_edit():
        new_text = edit_task_entry.get().strip()
        new_due = edit_due_entry.get().strip()
        new_priority = edit_priority_var.get()
        
        if not new_text:
            messagebox.showwarning("Warning", "Task cannot be empty.")
            return
        
        # Validate due date if provided
        if new_due:
            try:
                datetime.strptime(new_due, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return
        
        # Update task
        tasks[original_index]["text"] = new_text
        tasks[original_index]["due_date"] = new_due if new_due else None
        tasks[original_index]["priority"] = new_priority
        
        save_tasks()
        refresh_all_tabs()
        status_label.config(text=f"✏️ Task updated: {new_text}", fg=PRIMARY_COLOR)
        edit_window.destroy()
    
    # Buttons
    button_frame = tk.Frame(edit_window, bg=BG_COLOR)
    button_frame.pack(fill=tk.X, pady=10)
    
    tk.Button(button_frame, text="💾 Save Changes", command=save_edit,
              bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5).pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="❌ Cancel", command=edit_window.destroy,
              bg=WARNING_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5).pack(side=tk.RIGHT, padx=10)

def remove_task_from_card(task):
    if messagebox.askyesno("Confirm", f"Are you sure you want to remove the task:\n\n{task['text']}"):
        tasks.remove(task)
        save_tasks()
        refresh_all_tabs()
        status_label.config(text=f"🗑️ Task removed: {task['text']}", fg=WARNING_COLOR)

# Show tasks on startup with saved settings
if sort_var:
    sort_var.set(settings.get("sort_by", "none"))
if filter_var:
    filter_var.set(settings.get("filter_by", "all"))

# Check for due dates on startup
root.after(1000, check_due_dates)  # Check after 1 second

# Bind Enter key to add task
root.bind('<Return>', lambda e: add_task())

# Initialize pages
show_page("dashboard")

# Start the app
root.mainloop()