from prompt_toolkit.completion import Completer, Completion
from rich.console import Console

console = Console()

def setup_command_completer():
    command_list = [
        "/help", 
        "/settings",
        "/reset",
        "/change_model", 
        "/history", 
        "/clear", 
        "/exit", 
        "/toggle_history",
        "/toggle_search", 
        "/toggle_search_mode", 
        "/toggle_deep_research",
        "/search_count", 
        "/search_amount",
        "/context_size", 
        "/deep_research_amount",
        "/set_system_prompt", 
        "/set_top_p", 
        "/set_top_k", 
        "/set_temperature"
    ]
    
    class CommandCompleter(Completer):
        def __init__(self, commands):
            self.commands = commands
            
        def get_completions(self, document, complete_event):
            word = document.get_word_before_cursor()
            if word.startswith('/'):
                prefix = word[1:]
                for command in self.commands:
                    cmd = command[1:]
                    if cmd.startswith(prefix):
                        yield Completion(
                            cmd,
                            start_position=-len(prefix),
                            display=command
                        )
            elif document.text.startswith('/'):
                prefix = document.text[1:]
                for command in self.commands:
                    cmd = command[1:]
                    if cmd.startswith(prefix):
                        yield Completion(
                            cmd,
                            start_position=-len(prefix),
                            display=command
                        )
    
    return CommandCompleter(command_list)

def format_history_line(role, msg):
    role_colors = {
        "User": "[yellow]",
        "Assistant": "[green]",
        "system": "[yellow]",
        "Clarification Prompt": "[magenta]",
        "AI Clarification": "[yellow]",
        "User Clarification": "[yellow]",
        "Research Summary": "[yellow]",
        "Additional Details": "[magenta]"
    }
    
    role_color = role_colors.get(role, "[white]")
    reset = "[/]"
    return f"{role_color}{role}: {msg}{reset}"

def print_help():
    console.print("[green]Commands:[/green]")
    console.print("  [green]/help[/green]                           → display this help message")
    console.print("  [green]/settings[/green]                       → display current settings")
    console.print("  [green]/reset[/green]                          → reset all settings to default values")
    console.print("  [green]/change_model[/green]                   → go back to model selection")
    console.print("  [green]/history[/green]                        → view saved chat sessions (and load or delete them)")
    console.print("  [green]/clear[/green]                          → clear the current chat")
    console.print("  [green]/exit[/green]                           → exit the chat (session is saved automatically)")
    console.print("  [green]/toggle_history[/green]                 → enable/disable history saving")
    console.print("  [green]/toggle_search[/green]                  → enable/disable internet search in prompts")
    console.print("  [green]/toggle_search_mode[/green]             → toggle between auto and manual search modes")
    console.print("  [green]/search_count <number>[/green]          → set number of search results to display (default: 2)")
    console.print("  [green]/search_amount <number>[/green]         → set number of words to fetch per search result (default: 500)")
    console.print("  [green]/context_size <number>[/green]          → set the model context length (num_ctx) to use in requests (default: 2048)")
    console.print("  [green]/toggle_deep_research[/green]           → enable/disable deep research mode")
    console.print("  [green]/deep_research_amount <number>[/green]  → set the number of deep research iterations (default: 4)")
    console.print("  [green]/set_system_prompt <text>[/green]       → set the system prompt for the conversation (default: 'You are a helpful assistant.')")
    console.print("  [green]/set_top_p <number>[/green]             → set the top_p sampling parameter (0.0-1.0) (default: 0.9)")
    console.print("  [green]/set_top_k <number>[/green]             → set the top_k sampling parameter (default: 40)")
    console.print("  [green]/set_temperature <number>[/green]       → set the temperature parameter (0.0-2.0) (default: 0.7)")
