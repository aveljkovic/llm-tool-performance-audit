import time
from typing import Dict, Any, List
from anthropic import Anthropic

class StandardProfiler:
    def __init__(self, client: Anthropic, model: str):
        self.client = client
        self.model = model

    def run(self, system_prompt: str, user_message: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs a standard inference pass with all tools loaded immediately."""
        
        start_time = time.time()
        
        # Standard API call - all tools sent in 'tools'
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=tools
        )
        
        duration = time.time() - start_time
        
        return {
            "mode": "Standard (Eager Loading)",
            "latency_seconds": round(duration, 3),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "tool_use_count": len(response.content) if response.content else 0
        }