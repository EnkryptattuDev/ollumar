import requests
import json
import sys
import time
from rich.console import Console
from utils.spinners import FancySpinner

console = Console()
OLLAMA_API_BASE = "http://localhost:11434"

def send_message(model, context, text, suppress_output=False, config=None):
    if config is None:
        from main import CONFIG
        config = CONFIG
        
    system_msg = config.get("system_prompt")
    if system_msg and context and context[0].get("role") != "system":
        context.insert(0, {"role": "system", "content": system_msg})
        
    payload = {
        "model": model,
        "messages": context,
        "stream": True,
        "options": {
            "num_ctx": config.get("context_size", 2048),
            "top_p": config.get("top_p", 0.9),
            "top_k": config.get("top_k", 40),
            "temperature": config.get("temperature", 0.7)
        }
    }
    
    try:
        response = requests.post(f"{OLLAMA_API_BASE}/api/chat", json=payload, stream=True)
    except Exception as e:
        console.print(f"[red]Error connecting to API:[/red] {e}")
        return ""
        
    spinner = None
    in_think = False
    start_think_time = None
    full_response = ""
    
    try:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
                
            chunk = data.get("message", {}).get("content", "")
            while chunk:
                if not in_think:
                    if "<think>" in chunk:
                        before, after = chunk.split("<think>", 1)
                        if not suppress_output:
                            sys.stdout.write(before)
                            sys.stdout.flush()
                        full_response += before
                        if not full_response.endswith("\n"):
                            if not suppress_output:
                                sys.stdout.write("\n")
                                sys.stdout.flush()
                            full_response += "\n"
                        in_think = True
                        start_think_time = time.time()
                        if spinner is None:
                            spinner = FancySpinner("Thinking")
                            spinner.start()
                        chunk = after
                    else:
                        if not suppress_output:
                            sys.stdout.write(chunk)
                            sys.stdout.flush()
                        full_response += chunk
                        chunk = ""
                else:
                    if "</think>" in chunk:
                        part, after = chunk.split("</think>", 1)
                        if spinner:
                            spinner.stop()
                            spinner = None
                        elapsed = time.time() - start_think_time
                        elapsed_formatted = f"{elapsed:.1f}s"
                        if not suppress_output:
                            console.print(f"[green]Done thinking[/green] - thought for [{elapsed_formatted}]")
                        full_response += f"Done thinking - thought for [{elapsed_formatted}]\n"
                        in_think = False
                        chunk = after
                    else:
                        chunk = ""
    except KeyboardInterrupt:
        if spinner:
            spinner.stop()
        console.print("\n[green]Interrupted while waiting for response.[/green]")
        return full_response
        
    if in_think and spinner:
        spinner.stop()
        
    if not full_response.endswith("\n"):
        if not suppress_output:
            sys.stdout.write("\n")
        full_response += "\n"
        
    return full_response
