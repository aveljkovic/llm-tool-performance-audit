import time
from typing import Dict, Any, List
from anthropic import Anthropic

class DeferredProfiler:
    def __init__(self, client: Anthropic, model: str):
        self.client = client
        self.model = model

    def run(self, system_prompt: str, user_message: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs inference using the 'tool_search' beta feature."""
        
        # 1. Modify tools to be deferred
        # We assume the user wants to defer ALL tools for this test
        deferred_tools = []
        for tool in tools:
            t = tool.copy()
            t["defer_loading"] = True 
            deferred_tools.append(t)

        # 2. Define the search tool 
        # Using the BM25 (Natural Language) variant
        tool_search = {
            "name": "tool_search",
            "type": "tool_search_tool_bm25_20251119" 
        }

        start_time = time.time()

        # 3. Execute with beta headers
        response = self.client.beta.messages.create(
            model=self.model,
            betas=["advanced-tool-use-2025-11-20"], 
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            # We pass the search tool + the deferred definitions
            tools=[tool_search] + deferred_tools
        )

        duration = time.time() - start_time
        
        # Note: In beta, server_tool_use stats might be in different fields,
        # but usage.input_tokens reliably captures the total cost.
        return {
            "mode": "Deferred (Tool Search)",
            "latency_seconds": round(duration, 3),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "tool_use_count": len(response.content) if response.content else 0
        }