import os
import argparse
from dotenv import load_dotenv
from anthropic import Anthropic
from src.utils import generate_dummy_tools
from src.profilers.standard import StandardProfiler
from src.profilers.deferred import DeferredProfiler
from src.visualizers.terminal import ResultVisualizer

# Load .env file
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Audit LLM Tool Use Performance")
    parser.add_argument("--tools", type=int, default=50, help="Number of dummy tools to generate")
    # Note: Tool Search beta usually requires Sonnet 3.5 or newer
    parser.add_argument("--model", type=str, default="claude-3-5-sonnet-20241022", help="Anthropic model ID")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        return

    client = Anthropic(api_key=api_key)
    visualizer = ResultVisualizer()
    
    # Configuration
    tools = generate_dummy_tools(args.tools)
    system_prompt = "You are a helpful assistant. Use the provided tools to answer user questions."
    
    # We ask for a metric in the middle of the list to ensure search has to work
    target_id = int(args.tools/2)
    user_msg = f"I need to know the value of metric #{target_id} for user_123."

    visualizer.print_welcome(len(tools))

    # Run Standard
    std_profiler = StandardProfiler(client, args.model)
    print("Running Standard Profiler...")
    std_result = std_profiler.run(system_prompt, user_msg, tools)

    # Run Deferred
    def_profiler = DeferredProfiler(client, args.model)
    print("Running Deferred Profiler...")
    def_result = def_profiler.run(system_prompt, user_msg, tools)

    # Show Results
    visualizer.print_comparison(std_result, def_result)

if __name__ == "__main__":
    main()