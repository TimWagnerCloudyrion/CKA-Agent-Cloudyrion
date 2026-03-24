# CKA-Agent API Proxy

A local proxy server that lets the CKA-Agent talk to any external API. You write a single Python function that takes a prompt string and returns a response string.

## Quick Start

1. Edit `proxy/handler.py` — implement `handle_request(prompt: str) -> str` with your API call logic.

2. Start the proxy:
   ```bash
   python -m proxy.server --port 8080
   ```

3. Point the CKA-Agent at the proxy in `config/config.yml`:
   ```yaml
   blackbox:
     provider: "openai"
     name: "any-name"
     base_url: "http://localhost:8080/v1/"
     api_key: "not-needed"
   ```

4. Run your experiment as usual.

## How It Works

```
CKA-Agent  -->  POST /v1/chat/completions  -->  Proxy Server
                                                    |
                                                    v
                                             handle_request(prompt)
                                             (your code in handler.py)
                                                    |
                                                    v
                                             Your external API
                                                    |
                                                    v
CKA-Agent  <--  OpenAI-compatible response  <--  Proxy Server
```

The proxy exposes an OpenAI-compatible endpoint. The CKA-Agent sends requests as usual. The proxy extracts the prompt, passes it to your `handle_request()` function, and wraps whatever string you return back into an OpenAI-compatible response.

## Dependencies

```bash
pip install flask requests
```