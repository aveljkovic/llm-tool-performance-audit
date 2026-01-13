from typing import List, Dict, Any

def generate_dummy_tools(count: int = 50) -> List[Dict[str, Any]]:
    """
    Generates a list of dummy tool definitions to simulate context load.
    
    Args:
        count: Number of tools to generate.
    
    Returns:
        List of tool definitions matching Anthropic's schema.
    """
    tools = []
    for i in range(count):
        tool = {
            "name": f"get_customer_metric_{i:03d}",
            "description": (
                f"Retrieves granular customer metric #{i} for a specific user ID. "
                f"Use this tool when the user asks about data point {i}."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The customer UUID"},
                    "period": {"type": "string", "enum": ["day", "week", "month"]}
                },
                "required": ["user_id"]
            }
        }
        tools.append(tool)
    return tools