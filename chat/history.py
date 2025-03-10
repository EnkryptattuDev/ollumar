import os
import datetime
import re
from rich.console import Console
from rich.panel import Panel
from utils.commands import format_history_line

console = Console()
BASE_DIR = os.path.join(os.path.expanduser("~"), "ollumar", "data")
HISTORY_DIR = os.path.join(BASE_DIR, "history")

def save_chat_session(history, config):
    if not config.get("history", True):
        console.print("[green]History is disabled. Session not saved. Exiting...[/green]")
        return
    if not history:
        console.print("[green]No chat history to save.[/green]")
        return
    os.makedirs(HISTORY_DIR, exist_ok=True)
    global current_history_file
    if 'current_history_file' in globals() and current_history_file:
        filename = current_history_file
    else:
        first_msg = history[0][1] if history and history[0][1] else "chat"
        title = re.sub(r'\W+', '_', first_msg)[:20]
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(HISTORY_DIR, f"{title}_{now}.txt")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for role, msg in history:
                f.write(f"{role}: {msg}\n")
        console.print(f"[green]Chat session saved to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving session:[/red] {e}")

def load_chat_session(num):
    if not os.path.exists(HISTORY_DIR):
        console.print("[green]No history available.[/green]")
        return None, None, None
    files = sorted(os.listdir(HISTORY_DIR))
    if not files:
        console.print("[green]No history available.[/green]")
        return None, None, None
    if num < 1 or num > len(files):
        console.print("[green]Invalid session number.[/green]")
        return None, None, None
    filename = os.path.join(HISTORY_DIR, files[num-1])
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        session_history = []
        context = []
        for line in lines:
            if ": " in line:
                role, msg = line.split(": ", 1)
                session_history.append((role, msg.strip()))
                context.append({"role": role.lower(), "content": msg.strip()})
        return session_history, context, filename
    except Exception as e:
        console.print(f"[red]Error loading session:[/red] {e}")
        return None, None, None

def view_history_sessions():
    if not os.path.exists(HISTORY_DIR):
        console.print("[green]No history available.[/green]")
        return None, None, None
    files = sorted(os.listdir(HISTORY_DIR))
    if not files:
        console.print("[green]No history available.[/green]")
        return None, None, None
    console.print("[green]Saved Chat Sessions:[/green]")
    for idx, fname in enumerate(files):
        console.print(f"  {idx+1}. {fname}")
    console.print("[green]Enter session number to view, 'l <number>' to load, 'd <number>' to delete, 'd all' to delete all, or press Enter to return:[/green]", end=" ")
    command = input().strip()
    command = command.encode("ascii", errors="ignore").decode("ascii").strip()
    if command == "":
        return None, None, None
    parts = command.split()
    if parts[0].lower() == "d":
        if len(parts) == 2 and parts[1].lower() == "all":
            for fname in files:
                try:
                    os.remove(os.path.join(HISTORY_DIR, fname))
                except Exception as e:
                    console.print(f"[red]Error deleting {fname}:[/red] {e}")
            console.print("[green]All chat sessions deleted.[/green]")
        elif len(parts) == 2:
            try:
                num = int(parts[1])
                if num < 1 or num > len(files):
                    console.print("[green]Invalid session number.[/green]")
                    return None, None, None
                filename = os.path.join(HISTORY_DIR, files[num-1])
                os.remove(filename)
                console.print(f"[green]Deleted {files[num-1]}[/green]")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
        else:
            console.print("[green]Usage: d <number> OR d all[/green]")
        return None, None, None
    elif parts[0].lower() == "l":
        if len(parts) != 2:
            console.print("[green]Usage: l <number>[/green]")
            return None, None, None
        try:
            num = int(parts[1])
            loaded = load_chat_session(num)
            return loaded
        except ValueError:
            console.print("[green]Invalid session number.[/green]")
            return None, None, None
    else:
        try:
            num = int(command)
            if num < 1 or num > len(files):
                console.print("[green]Invalid session number.[/green]")
                return None, None, None
            filename = os.path.join(HISTORY_DIR, files[num-1])
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            console.print(Panel(content, title="Chat Session"))
            input("Press Enter to return...")
        except Exception as e:
            console.print(f"[red]Invalid input:[/red] {e}")
        return None, None, None