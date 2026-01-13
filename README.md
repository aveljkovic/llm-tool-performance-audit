# LLM Tool Performance Audit

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Anthropic](https://img.shields.io/badge/Anthropic-Beta-purple)
![License](https://img.shields.io/badge/License-MIT-green)

A precise profiling tool to benchmark **Standard Tool Loading** vs. **Anthropic's Deferred Tool Search** (Beta).

Building agents with 50+ tools introduces a critical trade-off: **Context Bloat** vs. **Latency**. This repo reverse-engineers the "Double Pass" behavior of server-side tool search to help engineers make data-driven architecture decisions.

---

## The Findings

Through empirical testing, this profiler confirms that **Deferred Loading** triggers a server-side loop:

1.  **Pass 1:** Model receives user prompt + `tool_search` tool only.
2.  **Server Action:** Anthropic executes search against your deferred tool definitions.
3.  **Pass 2:** Model receives the original prompt + **only the relevant tools** found.

**The Trade-off:**
* **Standard:** Higher Cost (Input Tokens), Lower Latency.
* **Deferred:** Lower Cost (Tokens), Higher Latency (~1.5x - 2x).

---

## Installation & Usage

1.  **Clone and Install**
    ```bash
    git clone [https://github.com/yourusername/llm-tool-performance-audit.git](https://github.com/yourusername/llm-tool-performance-audit.git)
    cd llm-tool-performance-audit
    make install
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```bash
    ANTHROPIC_API_KEY=sk-ant-api03-...
    ```

3.  **Run the Audit**
    ```bash
    make run
    ```
    *Optional: Simulate a heavier load with 100 tools:*
    ```bash
    make run-heavy
    ```

---

## The "Secret Sauce"

This project leverages the undocumented behavior of the `advanced-tool-use` beta. Here is how we implement the **Deferred Profiler**:

### 1. The Beta Configuration
We must specifically opt-in to the `2025-11-20` beta and use the `tool_search_tool_bm25` type.

```python
# src/profilers/deferred.py

response = client.beta.messages.create(
    model="claude-3-5-sonnet-20241022",
    # ⚠️ CRITICAL: The beta flag enables server-side loops
    betas=["advanced-tool-use-2025-11-20"], 
    max_tokens=1024,
    messages=[{"role": "user", "content": user_message}],
    tools=[
        {
            "type": "tool_search_tool_bm25_20251119", # The searcher
            "name": "tool_search"
        }
    ] + deferred_tools # Tools marked with defer_loading=True
)
```
### 2. Simulating Production Load
To get realistic metrics, we generate "heavy" tool definitions that mimic complex enterprise schemas.

```python
# src/utils.py

def generate_dummy_tools(count=50):
    return [{
        "name": f"get_metric_{i}",
        "description": "Complex retrieval tool for specific user segments...",
        "defer_loading": True  # <--- This triggers the search behavior
    } for i in range(count)]
```

### 📊 Sample Output
The CLI uses `rich` to visualize the delta between architectures.

```text
Performance Comparison
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Metric           ┃ Standard           ┃ Deferred (Search)   ┃ Delta        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Latency (s)      │ 2.105s             │ 3.850s              │ +1.745s      │
│ Input Tokens     │ 18,450             │ 1,240               │ -17,210      │
└──────────────────┴────────────────────┴─────────────────────┴──────────────┘
Analysis: Deferred loading reduced token consumption by 93%, but increased latency by 82% due to the sequential inference passes.
```

## Contributing
PRs are welcome! Specifically looking for:

- [ ] Profiling for the Regex search tool variant.
- [ ] Cost estimation calculator based on current token prices.

## 📄 License
MIT © Alex
