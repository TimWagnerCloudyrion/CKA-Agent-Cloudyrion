"""
Custom request handler for the CKA-Agent proxy.

Edit the handle_request() function below to call your external API.
The only contract is: string in, string out.
"""

import json
from datetime import datetime
from pathlib import Path

IO_LOG_FILE = Path(__file__).parent / "io_log.jsonl"


def _log_io(prompt: str, response: str) -> None:
    """Append an input/output pair to the log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": prompt,
        "output": response,
    }
    with open(IO_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def handle_request(prompt: str) -> str:
    """
    Receives the prompt from the CKA-Agent, calls your external API,
    and returns the response as a string.

    Args:
        prompt: The text prompt sent by the CKA-Agent.

    Returns:
        The response text to send back to the CKA-Agent.

    Example implementations are provided below (uncomment one or write your own).
    """

    # -------------------------------------------------------------------------
    # Replace this with your actual API call.
    # -------------------------------------------------------------------------

    from openai import OpenAI

    client = OpenAI(
        base_url="http://16.16.162.190:8080/api",
        api_key="..."
    )

    response = client.chat.completions.create(
        model="notrealcreditunion-assistant",
        messages=[{"role": "user", "content": prompt}],
        extra_body={
            "tool_ids": ["banking_tools"],
        },
    )

    result = response.choices[0].message.content
    _log_io(prompt, result)
    return result

    raise NotImplementedError(
        "Edit proxy/handler.py and implement handle_request()"
    )

    # -------------------------------------------------------------------------
    # Example 1: Simple REST API
    # -------------------------------------------------------------------------
    # resp = requests.post(
    #     "https://api.example.com/generate",
    #     headers={
    #         "Authorization": "Bearer YOUR_API_KEY",
    #         "Content-Type": "application/json",
    #     },
    #     json={
    #         "prompt": prompt,
    #         "max_tokens": 512,
    #     },
    #     timeout=120,
    # )
    # resp.raise_for_status()
    # return resp.json()["output"]["text"]

    # -------------------------------------------------------------------------
    # Example 2: Anthropic API (without their SDK)
    # -------------------------------------------------------------------------
    # resp = requests.post(
    #     "https://api.anthropic.com/v1/messages",
    #     headers={
    #         "x-api-key": "YOUR_API_KEY",
    #         "anthropic-version": "2023-06-01",
    #         "Content-Type": "application/json",
    #     },
    #     json={
    #         "model": "claude-sonnet-4-20250514",
    #         "max_tokens": 512,
    #         "messages": [{"role": "user", "content": prompt}],
    #     },
    #     timeout=120,
    # )
    # resp.raise_for_status()
    # return resp.json()["content"][0]["text"]

    # -------------------------------------------------------------------------
    # Example 3: Local Ollama
    # -------------------------------------------------------------------------
    # resp = requests.post(
    #     "http://localhost:11434/api/generate",
    #     json={
    #         "model": "llama3",
    #         "prompt": prompt,
    #         "stream": False,
    #     },
    #     timeout=300,
    # )
    # resp.raise_for_status()
    # return resp.json()["response"]