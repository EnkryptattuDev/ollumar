import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def display_logo():
    logo = r"""
                         ....:.:::..                        
                    .:-:..:===#*=:==--:                     
                  :=-::=#%=.                                
               ::..=+**-                                                                         
            =: :%%%*.                                       
           -+:+*%%+                                         
          .-..=:=*=                                         
          --:.=:-*:                                         
          -*: .=#*          OLLUMAR                                   
          ==:.#@@*                                          
          =-.:#%@%:                                         
          -*-..--**                                         
           +*: ..:#-.                                                                           
             -%%#=:.:==:                     .              
              =@%**:....::..              .:=               
               =%%%%===.:=-:::::.. ....:==-.                
               ::=*+%#==:.:. .:==:.::::::.                  
               ....  .:+*%%@#--..-**-.                      
               -:.         .:=*%::                          
                :=            +:.::                         
                 .          - :                             
                            .                               
                              :                             
                              #:                            
                              -.                            
    """
    console.print(f"[violet]{logo}[/violet]")

def display_settings(config):
    history_state = "[green]enabled[/green]" if config.get("history", True) else "[red]disabled[/red]"
    deep_research_state = "[green]enabled[/green]" if config.get("deep_research", False) else "[red]disabled[/red]"
    search_state = "[green]enabled[/green]" if config.get("search", True) else "[red]disabled[/red]"
    search_mode = f"[yellow]{config.get('search_mode', 'auto')}[/yellow]"
    
    settings_table = Table(show_header=False, box=None, padding=(0,1,0,1))
    settings_table.add_column("Setting", style="white")
    settings_table.add_column("Value", style="green")
    
    settings_table.add_row("History:", history_state)
    settings_table.add_row("Deep research:", deep_research_state)
    settings_table.add_row("Search:", search_state)
    settings_table.add_row("Deep research amount:", f"[yellow]{config.get('deep_research_amount', 4)}[/yellow]")
    settings_table.add_row("Search Mode:", search_mode)
    settings_table.add_row("Search Count:", f"[yellow]{config.get('search_count', 2)}[/yellow]")
    settings_table.add_row("Search Amount:", f"[yellow]{config.get('search_amount', 500)}[/yellow] words per result")
    settings_table.add_row("Context Size:", f"[yellow]{config.get('context_size', 2048)}[/yellow]")
    settings_table.add_row("Top P:", f"[yellow]{config.get('top_p', 0.9)}[/yellow]")
    settings_table.add_row("Top K:", f"[yellow]{config.get('top_k', 40)}[/yellow]")
    settings_table.add_row("Temperature:", f"[yellow]{config.get('temperature', 0.7)}[/yellow]")
    
    console.print(Panel(settings_table, title="[bold][violet]OLLUMAR[/violet] - Current Settings[/bold]", expand=False))

def clear_screen():
    os.system("clear")