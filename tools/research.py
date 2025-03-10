import datetime
import re
from rich.console import Console
from tools.search import search_duckduckgo
from chat.messaging import send_message
from utils.spinners import FancySpinner

console = Console()

def start_deep_research(model, original_request, config):
    spinner = FancySpinner("Generating research focus questions")
    spinner.start()
    
    specific_questions_prompt = (
        f"Generate 5 specific questions that will help tailor research for: '{original_request}'\n\n"
        f"Make each question clear and standalone. Format each as a bullet point."
    )
    
    questions_context = [{"role": "user", "content": specific_questions_prompt}]
    questions_response = send_message(model, questions_context, specific_questions_prompt, suppress_output=True, config=config)
    spinner.stop()
    
    prompts = []
    for line in questions_response.strip().split('\n'):
        line = line.strip()
        clean_prompt = re.sub(r'^\d+\.?\s+', '', line)
        clean_prompt = re.sub(r'^[•\-\*]\s+', '', clean_prompt)
        if clean_prompt and len(clean_prompt) > 10:
            prompts.append(clean_prompt)
    
    console.print("\n[green]To better focus the research on your request, please clarify:[/green]")
    for prompt in prompts[:5]:
        console.print(f"• {prompt}")
    
    console.print("[green]Enter your response:[/green] ", end="")
    additional_details = input().strip()
    return additional_details

def perform_deep_research_step(model, original_request, additional_details, current_summary, previous_queries, step, total_steps, config):
    console.print(f"\n[green]Research Step {step} of {total_steps}[/green]\n")
    
    if not hasattr(perform_deep_research_step, 'aspects'):
        spinner = FancySpinner("Generating research aspects\n")
        spinner.start()
        
        aspects_prompt = (
            f"For the topic: '{original_request}'\n"
            f"Additional details: '{additional_details}'\n\n"
            f"Generate {total_steps} distinct research aspects to explore sequentially.\n"
            f"Each aspect should cover ONE specific dimension of the topic.\n"
            f"Number each aspect and make them progressively more specific, starting with fundamental concepts.\n"
            f"Return only the numbered list without explanations."
        )
        
        aspects_context = [{"role": "user", "content": aspects_prompt}]
        aspects_response = send_message(model, aspects_context, aspects_prompt, suppress_output=True, config=config)
        
        perform_deep_research_step.aspects = []
        for line in aspects_response.strip().split('\n'):
            line = line.strip()
            clean_aspect = re.sub(r'^\d+\.?\s+', '', line)
            if clean_aspect and len(clean_aspect) > 3:
                perform_deep_research_step.aspects.append(clean_aspect)
        
        spinner.stop()
    
    if len(perform_deep_research_step.aspects) < step:
        current_aspect = f"Additional details and specific information about {original_request}"
    else:
        current_aspect = perform_deep_research_step.aspects[step-1]
    
    spinner = FancySpinner("Generating targeted search query")
    spinner.start()
    
    research_prompt_template = (
        "Based on this information:\n"
        "Task: {original_task}\n"
        "Details: {additional_details}\n"
        "{current_summary_text}"
        "{previous_queries_text}\n"
        "RESEARCH STAGE: You are at step {step} of {total_steps}.\n"
        "CURRENT ASPECT: {current_aspect}\n\n"
        "Generate a single focused search query specifically about: {current_aspect}\n"
        "Your query should be 1-5 words targeting ONLY the current aspect, not the general topic.\n"
        "Make sure your query is different from previous searches.\n"
        "Return only the search query without additional text."
    )
    
    current_summary_text = ""
    if current_summary:
        current_summary_text = f"3. Current research summary: {current_summary}\n"
    
    previous_queries_text = ""
    if previous_queries:
        previous_queries_text = f"4. Previous search queries (DO NOT REPEAT THESE):\n" + "\n".join([f"- {q}" for q in previous_queries])
    
    search_prompt = research_prompt_template.format(
        original_task=original_request,
        additional_details=additional_details,
        current_summary_text=current_summary_text,
        previous_queries_text=previous_queries_text,
        step=step,
        total_steps=total_steps,
        current_aspect=current_aspect
    )
    
    search_context = [{"role": "user", "content": search_prompt}]
    gen_query_response = send_message(model, search_context, search_prompt, suppress_output=True, config=config)
    gen_query = gen_query_response.strip().splitlines()[0].strip()
    spinner.stop()
    
    console.print(f"[green]Researching aspect:[/green] {current_aspect}")
    console.print(f"[green]Generated search query:[/green] {gen_query}")
    
    search_result = search_duckduckgo(
        gen_query,
        max_results=config.get("search_count", 2),
        search_amount=config.get("search_amount", 500)
    )
    
    urls = []
    for line in search_result.splitlines():
        if "Link:" in line:
            url = line.split("Link:")[-1].strip()
            urls.append(url)
    
    if urls:
        urls_str = "\n" + "\n".join(f"- {url.strip()}" for url in urls)
        console.print(f"[green]Online Search URLs:[/green]\n{urls_str}\n")
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    summary_instruction = f"Focus on providing information specifically about: {current_aspect}. Integrate with previous research but emphasize new findings."
    
    summary_prompt = (
        f"Today is {current_date}. You are researching: '{original_request}'.\n\n"
        f"You are at step {step} of {total_steps}, focusing on: {current_aspect}\n"
        f"{summary_instruction}\n\n"
        f"Search Results:\n{search_result}\n\n"
        f"Previous Summary: {current_summary}\n\n"
        f"Summarize NEW information about {current_aspect} that contributes to understanding the topic. Be concise but thorough."
    )
    
    spinner = FancySpinner("Analyzing")
    spinner.start()
    summary_context = [{"role": "user", "content": summary_prompt}]
    summary_response = send_message(model, summary_context, summary_prompt, suppress_output=True, config=config)
    spinner.stop()
    
    return summary_response.strip(), gen_query

def compile_research_results(model, original_request, additional_details, all_research, config):
    model_max_context = config.get("context_size", 2048)
    
    instructions_length = len(
        "Create a comprehensive response about: ''\n\n"
        "Additional details provided: ''\n\n"
        "Research information:\n\n\n\n"
        "Instructions:\n"
        "Synthesize this information into a well-structured response\n"
        "Organize logically with clear sections and headings\n"
        "Maintain a consistent tone and flow throughout\n"
        "Ensure all key aspects are covered thoroughly\n"
        "Create a cohesive narrative that addresses the original request\n\n"
        "Format your response as a polished, publication-ready document."
    )
    prompt_overhead = len(original_request) + len(additional_details) + instructions_length
    
    available_research_space = model_max_context - prompt_overhead
    
    research_text = all_research
    if len(all_research) > available_research_space and available_research_space > 0:
        console.print(f"[yellow]Note: Optimizing research data to fit within context window ({available_research_space} of {len(all_research)} chars).[/yellow]")
        research_text = all_research[:available_research_space] + "..."
    elif available_research_space <= 0:
        console.print(f"[red]Warning: Very limited context space available. Using abbreviated research.[/red]")
        minimal_research = min(int(model_max_context * 0.7), len(all_research))
        research_text = all_research[:minimal_research] + "..."
    
    final_prompt = (
        f"Create a comprehensive response about: '{original_request}'\n\n"
        f"Additional details provided: '{additional_details}'\n\n"
        f"Research information:\n\n{research_text}\n\n"
        f"Instructions:\n"
        f"Synthesize this research information AND use your own knowledge to create a complete response\n"
        f"Fill in gaps in the research with your own understanding when appropriate\n"
        f"Organize logically with clear sections and headings\n"
        f"Maintain a consistent tone and flow throughout\n"
        f"Ensure all key aspects are covered thoroughly\n"
        f"Create a cohesive narrative that addresses the original request\n\n"
        f"Format your response as a polished, publication-ready document."
    )
    
    console.print("\n[green]Compiling final answer...[/green]\n")
    
    final_context = [{"role": "user", "content": final_prompt}]
    final_answer = send_message(model, final_context, final_prompt, suppress_output=False, config=config)
    
    return final_answer