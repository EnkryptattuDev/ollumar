import os
from rich.console import Console

console = Console()
BASE_DIR = os.path.join(os.path.expanduser("~"), "ollumar", "data")
HISTORY_DIR = os.path.join(BASE_DIR, "history")

def load_config():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)
    config_path = os.path.join(BASE_DIR, "config.conf")
    config = {
        "history": True,
        "search": False,
        "search_count": 2,
        "search_amount": 500,
        "search_mode": "auto",
        "context_size": 2048,
        "deep_research": False,
        "deep_research_amount": 4,
        "top_p": 0.9,
        "top_k": 40,
        "temperature": 0.7,
        "system_prompt": "You are a helpful assistant.",
        "api_url": "http://localhost:11434"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("history="):
                        value = line.split("=")[1].strip().lower()
                        config["history"] = (value == "true")
                    elif line.startswith("search="):
                        value = line.split("=")[1].strip().lower()
                        config["search"] = (value == "true")
                    elif line.startswith("search_count="):
                        value = line.split("=")[1].strip()
                        try:
                            config["search_count"] = int(value)
                        except ValueError:
                            config["search_count"] = 2
                    elif line.startswith("search_amount="):
                        value = line.split("=")[1].strip()
                        try:
                            config["search_amount"] = int(value)
                        except ValueError:
                            config["search_amount"] = 500
                    elif line.startswith("search_mode="):
                        value = line.split("=")[1].strip().lower()
                        if value in ["auto", "manual"]:
                            config["search_mode"] = value
                        else:
                            config["search_mode"] = "auto"
                    elif line.startswith("context_size="):
                        value = line.split("=")[1].strip()
                        try:
                            config["context_size"] = int(value)
                        except ValueError:
                            config["context_size"] = 2048
                    elif line.startswith("deep_research="):
                        value = line.split("=")[1].strip().lower()
                        config["deep_research"] = (value == "true")
                    elif line.startswith("deep_research_amount="):
                        value = line.split("=")[1].strip()
                        try:
                            config["deep_research_amount"] = int(value)
                        except ValueError:
                            config["deep_research_amount"] = 4
                    elif line.startswith("top_p="):
                        value = line.split("=")[1].strip()
                        try:
                            config["top_p"] = float(value)
                        except ValueError:
                            config["top_p"] = 0.9
                    elif line.startswith("top_k="):
                        value = line.split("=")[1].strip()
                        try:
                            config["top_k"] = int(value)
                        except ValueError:
                            config["top_k"] = 40
                    elif line.startswith("temperature="):
                        value = line.split("=")[1].strip()
                        try:
                            config["temperature"] = float(value)
                        except ValueError:
                            config["temperature"] = 0.7
                    elif line.startswith("system_prompt="):
                        config["system_prompt"] = line.split("=", 1)[1].strip()
                    elif line.startswith("api_url="):
                        config["api_url"] = line.split("=", 1)[1].strip()
        except Exception as e:
            console.print(f"[red]Error reading config:[/red] {e}")
    else:
        save_config(config)
    return config

def save_config(config):
    config_path = os.path.join(BASE_DIR, "config.conf")
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(f"history={'true' if config.get('history', True) else 'false'}\n")
            f.write(f"search={'true' if config.get('search', False) else 'false'}\n")
            f.write(f"search_count={config.get('search_count', 2)}\n")
            f.write(f"search_amount={config.get('search_amount', 500)}\n")
            f.write(f"search_mode={config.get('search_mode', 'auto')}\n")
            f.write(f"context_size={config.get('context_size', 2048)}\n")
            f.write(f"deep_research={'true' if config.get('deep_research', False) else 'false'}\n")
            f.write(f"deep_research_amount={config.get('deep_research_amount', 4)}\n")
            f.write(f"top_p={config.get('top_p', 0.9)}\n")
            f.write(f"top_k={config.get('top_k', 40)}\n")
            f.write(f"temperature={config.get('temperature', 0.7)}\n")
            f.write(f"system_prompt={config.get('system_prompt', 'You are a helpful assistant.')}\n")
            f.write(f"api_url={config.get('api_url', 'http://localhost:11434')}\n")
    except Exception as e:
        console.print(f"[red]Error saving config:[/red] {e}")

def reset_settings():
    config = {
        "history": True,
        "search": False,
        "search_count": 2,
        "search_amount": 500,
        "search_mode": "auto",
        "context_size": 2048,
        "deep_research": False,
        "deep_research_amount": 4,
        "top_p": 0.9,
        "top_k": 40,
        "temperature": 0.7,
        "system_prompt": "You are a helpful assistant.",
        "api_url": "http://localhost:11434"
    }
    save_config(config)
    return config
