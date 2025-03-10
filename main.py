import os
import sys
import threading
import time
import re
import datetime
import json
from config.settings import load_config, save_config, reset_settings
from ui.display import display_logo, display_settings, clear_screen
from api.models import select_model
from chat.messaging import send_message
from chat.history import save_chat_session, load_chat_session, view_history_sessions
from tools.search import search_duckduckgo, generate_search_query
from tools.research import perform_deep_research_step, start_deep_research, compile_research_results
from utils.commands import setup_command_completer, print_help, format_history_line
from utils.spinners import FancySpinner, Spinner
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console

console = Console()
current_history_file = None
CONFIG = {}
DEEP_RESEARCH_ENABLED = False
DEEP_RESEARCH_AMOUNT = 4
OLLAMA_API_BASE = "http://localhost:11434"
BASE_DIR = os.path.join(os.path.expanduser("~"), "ollumar", "data")
HISTORY_DIR = os.path.join(BASE_DIR, "history")

def check_dependencies():
    return

def main():
    global current_history_file, CONFIG, DEEP_RESEARCH_ENABLED, DEEP_RESEARCH_AMOUNT, OLLAMA_API_BASE
    config = load_config()
    CONFIG = config
    OLLAMA_API_BASE = config.get("api_url", "http://localhost:11434")
    DEEP_RESEARCH_ENABLED = config.get("deep_research", False)
    DEEP_RESEARCH_AMOUNT = config.get("deep_research_amount", 4)
    model = select_model()
    session_history = []
    context = []
    
    command_completer = setup_command_completer()
    
    style = Style.from_dict({
        'completion-menu': 'bg:#333333 #AAAAAA',
        'completion-menu.completion': 'bg:#333333 #FFFFFF',
        'completion-menu.completion.current': 'bg:#555555 #FFFFFF',
        'scrollbar.background': 'bg:#333333',
        'scrollbar.button': 'bg:#555555',
    })
    
    session = PromptSession(completer=command_completer, style=style)
    clear_screen()
    
    display_settings(config)
    
    console.print("[green]Type [yellow]/help[/yellow] to see available commands.[/green]")
    
    while True:
        try:
            text = session.prompt("> ")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        if not text.strip():
            continue
            
        if text.startswith("/"):
            cmd = text.strip().split(maxsplit=1)
            base_cmd = cmd[0]
            
            if base_cmd == "/help":
                print_help()
                continue
                
            elif base_cmd == "/settings":
                display_settings(config)
                continue
                
            elif base_cmd == "/reset":
                config = reset_settings()
                console.print("[green]All settings have been reset to default values.[/green]")
                display_settings(config)
                continue
                
            elif base_cmd == "/context_size":
                if len(cmd) != 2:
                    console.print("[green]Usage: /context_size <number>[/green]")
                    continue
                try:
                    new_size = int(cmd[1])
                    config["context_size"] = new_size
                    save_config(config)
                    console.print(f"[green]Context size set to {new_size}.[/green]")
                except ValueError:
                    console.print("[green]Invalid context size number.[/green]")
                continue
                
            elif base_cmd == "/set_system_prompt":
                if len(cmd) != 2:
                    console.print("[green]Usage: /set_system_prompt <text>[/green]")
                    continue
                new_prompt = cmd[1].strip()
                config["system_prompt"] = new_prompt
                save_config(config)
                console.print(f"[green]System prompt set to: {new_prompt}[/green]")
                
                if context and context[0].get("role") == "system":
                    context[0]["content"] = new_prompt
                else:
                    context.insert(0, {"role": "system", "content": new_prompt})
                continue
                
            elif base_cmd == "/set_top_p":
                if len(cmd) != 2:
                    console.print("[green]Usage: /set_top_p <number>[/green]")
                    continue
                try:
                    new_value = float(cmd[1])
                    if new_value <= 0 or new_value > 1:
                        console.print("[green]top_p must be between 0 and 1[/green]")
                        continue
                    config["top_p"] = new_value
                    save_config(config)
                    console.print(f"[green]top_p set to {new_value}.[/green]")
                except ValueError:
                    console.print("[green]Invalid number.[/green]")
                continue
                
            elif base_cmd == "/set_top_k":
                if len(cmd) != 2:
                    console.print("[green]Usage: /set_top_k <number>[/green]")
                    continue
                try:
                    new_value = int(cmd[1])
                    if new_value <= 0:
                        console.print("[green]top_k must be greater than 0[/green]")
                        continue
                    config["top_k"] = new_value
                    save_config(config)
                    console.print(f"[green]top_k set to {new_value}.[/green]")
                except ValueError:
                    console.print("[green]Invalid number.[/green]")
                continue
                
            elif base_cmd == "/set_temperature":
                if len(cmd) != 2:
                    console.print("[green]Usage: /set_temperature <number>[/green]")
                    continue
                try:
                    new_value = float(cmd[1])
                    if new_value < 0:
                        console.print("[green]temperature must be non-negative[/green]")
                        continue
                    config["temperature"] = new_value
                    save_config(config)
                    console.print(f"[green]temperature set to {new_value}.[/green]")
                except ValueError:
                    console.print("[green]Invalid number.[/green]")
                continue
                
            elif base_cmd == "/history":
                loaded_history, loaded_context, filename = view_history_sessions()
                if loaded_history is not None and loaded_context is not None:
                    current_history_file = filename
                    session_history = loaded_history
                    context = loaded_context
                    clear_screen()
                    console.print("[green]Session loaded. You can continue the conversation.[/green]\n")
                    for role, msg in session_history:
                        console.print(format_history_line(role, msg))
                    console.print("")
                continue
                
            elif base_cmd == "/clear":
                session_history = []
                context = []
                clear_screen()
                display_settings(config)
                console.print("[green]Type [yellow]/help[/yellow] to see available commands.[/green]")
                console.print("[green]Chat cleared.[/green]")
                continue
                
            elif base_cmd == "/exit":
                break
                
            elif base_cmd == "/toggle_history":
                config["history"] = not config.get("history", True)
                save_config(config)
                state = "enabled" if config["history"] else "disabled"
                console.print(f"[green]History has been {state}.[/green]")
                continue
                
            elif base_cmd == "/toggle_search":
                config["search"] = not config.get("search", True)
                save_config(config)
                state = "enabled" if config["search"] else "disabled"
                console.print(f"[green]Internet search has been {state}.[/green]")
                continue
                
            elif base_cmd == "/toggle_search_mode":
                current_mode = config.get("search_mode", "auto")
                new_mode = "manual" if current_mode == "auto" else "auto"
                config["search_mode"] = new_mode
                save_config(config)
                console.print(f"[green]Search mode has been changed to: {new_mode}.[/green]")
                continue
                
            elif base_cmd == "/search_count":
                if len(cmd) < 2:
                    console.print("[green]Usage: /search_count <number>[/green]")
                else:
                    try:
                        count = int(cmd[1])
                        if count <= 0:
                            raise ValueError
                        config["search_count"] = count
                        save_config(config)
                        console.print(f"[green]Search result count set to {count}.[/green]")
                    except ValueError:
                        console.print("[green]Invalid number provided.[/green]")
                continue
                
            elif base_cmd == "/search_amount":
                if len(cmd) < 2:
                    console.print("[green]Usage: /search_amount <number>[/green]")
                else:
                    try:
                        amount = int(cmd[1])
                        if amount <= 0:
                            raise ValueError
                        config["search_amount"] = amount
                        save_config(config)
                        console.print(f"[green]Search result word amount set to {amount} words per result.[/green]")
                    except ValueError:
                        console.print("[green]Invalid number provided.[/green]")
                continue
                
            elif base_cmd == "/change_model":
                model = select_model()
                clear_screen()
                display_settings(config)
                console.print(f"[green]Model changed to: {model}[/green]")
                continue
                
            elif base_cmd == "/toggle_deep_research":
                DEEP_RESEARCH_ENABLED = not DEEP_RESEARCH_ENABLED
                config["deep_research"] = DEEP_RESEARCH_ENABLED
                save_config(config)
                state = "enabled" if DEEP_RESEARCH_ENABLED else "disabled"
                console.print(f"[green]Deep research mode has been {state}.[/green]")
                continue
                
            elif base_cmd == "/deep_research_amount":
                if len(cmd) < 2:
                    console.print("[green]Usage: /deep_research_amount <number>[/green]")
                else:
                    try:
                        amt = int(cmd[1])
                        if amt < 1:
                            raise ValueError
                        DEEP_RESEARCH_AMOUNT = amt
                        config["deep_research_amount"] = amt
                        save_config(config)
                        console.print(f"[green]Deep research iterations set to {amt}.[/green]")
                    except ValueError:
                        console.print("[green]Invalid number provided for deep research amount.[/green]")
                continue
                
            else:
                console.print("[green]Unknown command.[/green] Type [yellow]/help[/yellow] to see available commands.")
                continue
                
        if DEEP_RESEARCH_ENABLED:
            original_request = text.strip()
            console.print("[green]Deep Research Mode is active[/green]")
            
            additional_details = start_deep_research(model, original_request, config)
            
            full_research_task = f"{original_request}"
            if additional_details:
                full_research_task += f" {additional_details}"
                
            combined_summary = ""
            step_summaries = []
            previous_queries = []
            
            # Perform research steps
            for i in range(DEEP_RESEARCH_AMOUNT):
                new_summary, query = perform_deep_research_step(
                    model, 
                    original_request, 
                    additional_details, 
                    combined_summary,
                    previous_queries,
                    i+1, 
                    DEEP_RESEARCH_AMOUNT, 
                    config
                )
                
                previous_queries.append(query)
                step_summaries.append(f"--- Step {i+1} Research ---\n{new_summary}")
                
                if combined_summary:
                    combined_summary += "\n\n" + new_summary
                else:
                    combined_summary = new_summary
                    
            all_research = "\n\n".join(step_summaries)
            
            # Compile and display final answer
            final_answer = compile_research_results(model, original_request, additional_details, all_research, config)
            
            # Add to conversation history
            session_history.append(("User", original_request))
            if additional_details:
                session_history.append(("User Focus", additional_details))
            session_history.append(("Research Summary", combined_summary))
            session_history.append(("Assistant", final_answer))
            
            context.append({"role": "user", "content": original_request})
            context.append({"role": "assistant", "content": final_answer})
            
        else:
            session_history.append(("User", text))
            context.append({"role": "user", "content": text})
            
            if config.get("search", True):
                if config.get("search_mode", "auto") == "auto":
                    if "</think>" in text:
                        text = text.split("</think>")[-1].strip()
                    if text.lower().startswith("search online"):
                        text = text[len("search online"):].strip()
                        
                    generated_search_query = generate_search_query(text, model, config)
                    generated_search_query = generated_search_query.splitlines()[0].strip()
                    generated_search_query = generated_search_query.replace("<think>", "").strip()
                    
                    if not generated_search_query:
                        generated_search_query = text
                        
                    console.print(f"[green]Generated search query:[/green] {generated_search_query}")
                    
                    search_result = search_duckduckgo(
                        generated_search_query,
                        max_results=config.get("search_count", 2),
                        search_amount=config.get("search_amount", 500)
                    )
                    
                    urls = []
                    for line in search_result.splitlines():
                        if "Link:" in line:
                            url = line.split("Link:")[-1].strip()
                            urls.append(url)
                            
                    if urls:
                        urls_str = "\n" + "\n".join(f"- {url}" for url in urls)
                        console.print(f"[green]Online Search URLs:[/green]\n{urls_str}\n")
                    
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    refined_prompt = (
                        f"Current Date: {current_date}. Search Query: {generated_search_query}. "
                        f"IMPORTANT: Answer using only the information provided in the search results below. Do not include any extraneous commentary or speculation. "
                        f"Online search results for '{generated_search_query}': {search_result} "
                        f"Based on these findings, please address the following inquiry: {text}"
                    )
                    
                    refined_prompt = " ".join(refined_prompt.split())
                    text = refined_prompt
                    context[-1] = {"role": "user", "content": text}
                    
                elif config.get("search_mode", "auto") == "manual":
                    match = re.search(r'search\s*"([^"]+)"', text)
                    if match:
                        query = match.group(1)
                        search_result = search_duckduckgo(
                            query,
                            max_results=config.get("search_count", 2),
                            search_amount=config.get("search_amount", 500)
                        )
                        
                        text = re.sub(r'search\s*"[^"]+"', "", text).strip()
                        if not text:
                            refined_prompt = f"A web search was performed; results: {search_result}. No additional query provided."
                        else:
                            refined_prompt = f"A web search was performed; results: {search_result}. Please answer the user's query using these results: {text}"
                            
                        urls = []
                        for line in search_result.splitlines():
                            if "Link:" in line:
                                parts = line.split("Link:")
                                if len(parts) > 1:
                                    url = parts[1].strip()
                                    urls.append(url)
                                    
                        if urls:
                            urls_str = "\n" + "\n".join(f"- {url}" for url in urls)
                            console.print(f"[green]Online Search URLs:[/green]\n{urls_str}\n")
                        
                        text = " ".join(refined_prompt.split())
                        context[-1] = {"role": "user", "content": text}
                        
            response_text = send_message(model, context, text, config=config)
            response_text = transform_stars(response_text)
            session_history.append(("Assistant", response_text))
            context.append({"role": "assistant", "content": response_text})
            
    save_chat_session(session_history, CONFIG)

def transform_stars(text):
    return text.replace("*", "★")

if __name__ == "__main__":
    check_dependencies()
    main()