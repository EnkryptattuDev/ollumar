import requests
import datetime
import random
import time
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from rich.console import Console
from utils.spinners import FancySpinner

console = Console()
OLLAMA_API_BASE = "http://localhost:11434"

def search_duckduckgo(query, max_results=2, search_amount=500):
    delay = random.uniform(0.5, 1.5)
    time.sleep(delay)
    
    search_result = ""
    spinner = FancySpinner(f"Searching for '{query}'")
    spinner.start()
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    ]
    
    user_agent = random.choice(user_agents)
    
    try:
        headers = {"User-Agent": user_agent}
        ddgs = DDGS(headers=headers)
        results = ddgs.text(query, max_results=max_results)
        if results and len(results) > 0:
            formatted_results = []
            for i, result in enumerate(results, start=1):
                title = result.get("title", "No title")
                original_snippet = result.get("body", "No snippet available")
                link = result.get("href", "")
                
                spinner.update(f"Fetching content from {title}")
                snippet_text = ""
                try:
                    page_headers = {"User-Agent": random.choice(user_agents)}
                    page = requests.get(link, timeout=5, headers=page_headers)
                    if page.ok:
                        soup = BeautifulSoup(page.text, "html.parser")
                        for script in soup(["script", "style"]):
                            script.decompose()
                        text_content = soup.get_text(separator=" ")
                        words = text_content.split()
                        snippet_text = " ".join(words[:search_amount])
                    else:
                        snippet_text = original_snippet
                except Exception as ex:
                    snippet_text = original_snippet

                formatted_results.append(
                    f"Result {i}: Title: {title} Snippet: {snippet_text} Link: {link}"
                )
            search_result = "\n".join(formatted_results)
        else:
            search_result = "No results found."
    except Exception as e:
        search_result = f"Error during search: {str(e)}"
    finally:
        spinner.stop()
    return search_result

def generate_search_query(user_prompt, model, config):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    search_prompt = (
        f"Today is {current_date}. From the user's inquiry below, create a short search query.\n"
        f"Make it different from the original inquiry.\n"
        f"Do not use any symbols or punctuation.\n"
        f"User inquiry: {user_prompt} Search Query:"
    )
    search_prompt = " ".join(search_prompt.split())
    
    spinner = FancySpinner("Generating search query")
    spinner.start()
    
    try:
        response = requests.post(
            f"{OLLAMA_API_BASE}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": search_prompt}],
                "stream": False,
                "options": {
                    "num_ctx": config.get("context_size", 2048),
                    "top_p": config.get("top_p", 0.9),
                    "top_k": config.get("top_k", 40),
                    "temperature": config.get("temperature", 0.7)
                }
            }
        )
        if response.ok:
            data = response.json()
            search_query = data.get("message", {}).get("content", "").strip().splitlines()[0]
            return search_query
        else:
            console.print("[green]Error: Received non-OK response from API while generating search query.[/green]")
            return user_prompt
    except Exception as e:
        console.print(f"[green]Error generating search query: {e}[/green]")
        return user_prompt
    finally:
        spinner.stop()