"""
Custom request handler for the CKA-Agent proxy.

Edit the handle_request() function below to call your external API.
The contract is: messages list in, string out.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from agent_demo_example_use_cases.ipi_payment_request import payment_request_ipi, _append_tool_call_information

from dotenv import load_dotenv

load_dotenv()

IO_LOG_FILE = Path(__file__).parent / "io_log.jsonl"


def _log_io(messages: list, response: str) -> None:
    """Append an input/output pair to the log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": messages,
        "output": response,
    }
    with open(IO_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def handle_request(messages: list[dict[str, str]]) -> str:
    """
    Receives the messages from the CKA-Agent, calls your external API,
    and returns the response as a string.

    Args:
        messages: The full conversation messages list (role/content dicts).

    Returns:
        The response text to send back to the CKA-Agent.

    Example implementations are provided below (uncomment one or write your own).
    """

    # -------------------------------------------------------------------------
    # Replace this with your actual API call.
    # -------------------------------------------------------------------------

    from openai import OpenAI

    client = OpenAI(
        base_url="http://12.12.12.12:8080/api",
        api_key=os.getenv("TARGET_API_KEY"),
    )

    response = client.chat.completions.create(
        model="notrealcreditunion-assistant",
        messages=messages,
        extra_body={
            "tool_ids": ["banking_tools_v2"],
        },
    )

    result = response.choices[0].message.content
    tool_prefix = _append_tool_call_information(response)

    output = tool_prefix + result

    _log_io(messages, output)
    return output


if __name__ == '__main__':
    print(handle_request([{"role": "user", "content": "Please summarize http://friendly.com"}]))