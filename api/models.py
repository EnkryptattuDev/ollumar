import json
import time
import requests
import sys
from rich.console import Console
from ui.display import display_logo, clear_screen
from utils.spinners import FancySpinner

console = Console()
OLLAMA_API_BASE = "http://localhost:11434"

def select_model():
    global OLLAMA_API_BASE
    try:
        r = requests.get(f"{OLLAMA_API_BASE}/api/tags")
        if not r.ok:
            raise Exception("Non-OK response")
        models = r.json().get("models", [])
    except Exception:
        models = None
    while True:
        clear_screen()
        display_logo()
        instructions = ('''
- '<model_number>' or '<model_name>' to load
- 'p <model_name>' to pull
- 'r <number>' or 'r <model_name>' to remove
- [green]/change_api[/green] to change API URL
- [green]/exit[/green] to quit.
        ''')
        console.print(instructions)
        console.print("Available models:")
        if models is None:
            console.print("  [red]Error connecting to ollama. Is it running?[/red]")
        elif not models:
            console.print("  [green]No models found. Please pull a model.[/green]")
        else:
            for idx, m in enumerate(models):
                console.print(f"  {idx+1}. {m.get('name')}")
        choice = input("Your choice: ").strip()
        if choice.lower() == "/exit":
            sys.exit(0)
        if choice.lower() == "/change_api":
            console.print("Enter new Ollama API base URL (default: http://localhost:11434):")
            new_api = input().strip()
            if new_api:
                OLLAMA_API_BASE = new_api
                from main import CONFIG
                CONFIG["api_url"] = new_api
                from config.settings import save_config
                save_config(CONFIG)
                console.print(f"[green]API URL changed to {new_api}[/green]")
            else:
                console.print("[green]API URL unchanged.[/green]")
            try:
                r = requests.get(f"{OLLAMA_API_BASE}/api/tags")
                if r.ok:
                    models = r.json().get("models", [])
                else:
                    models = None
            except Exception:
                models = None
            continue
        if not choice:
            choice = "1"
        if choice.lower().startswith("p"):
            model_name = choice[1:].strip()
            if not model_name:
                console.print("[green]Please specify a model name to pull. For example: p llama3.2[/green]")
                continue
            pull_model(model_name)
            try:
                r = requests.get(f"{OLLAMA_API_BASE}/api/tags")
                if r.ok:
                    models = r.json().get("models", [])
                else:
                    models = None
            except Exception:
                models = None
            continue
        elif choice.lower().startswith("r"):
            model_identifier = choice[1:].strip()
            if not model_identifier:
                console.print("[green]Please specify a model name or number to remove. For example: r llama3.2 or r 1[/green]")
                continue
            
            try:
                model_number = int(model_identifier)
                if models is None or model_number < 1 or model_number > len(models):
                    console.print("[green]Invalid model number.[/green]")
                    continue
                model_name = models[model_number-1].get("name")
                remove_model(model_name)
            except ValueError:
                remove_model(model_identifier)
                
            try:
                r = requests.get(f"{OLLAMA_API_BASE}/api/tags")
                if r.ok:
                    models = r.json().get("models", [])
                else:
                    models = None
            except Exception:
                models = None
            continue
        else:
            try:
                idx = int(choice) - 1
                if models is None or idx < 0 or idx >= len(models):
                    console.print("[green]Invalid model number.[/green]")
                    continue
                selected = models[idx].get("name")
            except ValueError:
                if models is None:
                    console.print("[green]Invalid model name. Please try again.[/green]")
                    continue
                valid_models = [m.get("name").lower() for m in models]
                if choice.lower() not in valid_models:
                    console.print("[green]Model not found. Please enter a valid model name or number.[/green]")
                    continue
                selected = choice
            console.print(f"[white]Selected model:[/white] [green]{selected}[/green]")
            clear_screen()
            try:
                requests.post(f"{OLLAMA_API_BASE}/api/chat", json={"model": selected, "messages": []})
            except Exception:
                pass
            return selected

def pull_model(model_name):
    try:
        response = requests.post(f"{OLLAMA_API_BASE}/api/pull", json={"model": model_name}, stream=True)
    except Exception as e:
        console.print(f"[green]Error pulling model {model_name}:[/green] {e}")
        return
    
    spinner = FancySpinner(f"Pulling model {model_name}")
    spinner.start()
    
    i = 0
    try:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            status = data.get("status", "")
            total = data.get("total")
            completed = data.get("completed")
            if total and completed:
                progress_status = f"[{completed/(1024**3):.1f}GB/{total/(1024**3):.1f}GB]"
                spinner.update(f"Pulling model {model_name} {progress_status} {status}")
            else:
                spinner.update(f"Pulling model {model_name} {status}")
            i += 1
        spinner.stop()
        time.sleep(0.5)
        clear_screen()
        display_logo()
        console.print(f"[white]Successfully pulled model:[/white] [green]{model_name}[/green]")
        input("Press Enter to continue...")
    except KeyboardInterrupt:
        spinner.stop()
        console.print(f"\n[green]Pulling model {model_name} interrupted.[/green]")
        return

def remove_model(model_name):
    try:
        response = requests.delete(f"{OLLAMA_API_BASE}/api/delete", json={"name": model_name})
    except Exception as e:
        console.print(f"[green]Error removing model {model_name}:[/green] {e}")
        return
    time.sleep(0.5)
    clear_screen()
    display_logo()
    if response.ok:
        console.print(f"[white]Successfully removed model:[/white] [green]{model_name}[/green]")
    else:
        console.print(f"[green]Failed to remove model {model_name}. Response: {response.text}[/green]")
    input("Press Enter to continue...")