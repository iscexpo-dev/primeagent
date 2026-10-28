# WFX - Primeagent Executor

The Primeagent Executor (WFX) is a command-line tool that serves and runs flows statelessly from flow JSON files with minimal dependencies.

Running a flow with WFX is similar to running flows with the `--backend-only` environment variable enabled, but even more lightweight because the Primeagent package and all of its dependencies don't need to be installed.

WFX uses a no-op database interface called [`NoopSession`](https://github.com/khulnasoft-bot/primeagent/blob/main/src/wfx/src/wfx/services/session.py) for all operations that require persistent state.
There is no `primeagent.db` database file when using WFX.
You can run flows with the API, but any stateful operations that depend on the Primeagent database, like saving flows, storing messages, or managing users **will not** persist data.
Operations that depend on `primeagent.db` will not work as they do in the full Primeagent application.

Memory operations are dispatched at call time, not at import time.
If the `primeagent` package is installed in the same Python environment as `wfx` and a real database service is registered, memory operations are routed to the full `primeagent.memory` implementation instead. This applies when `wfx` is used as a Python library inside a running Primeagent server, not when running `wfx run` or `wfx serve` from the command line.

## Commands

**Runtime commands** — documented in this README:

| Command | Description |
|---------|-------------|
| [`wfx serve`](#serve-the-simple-agent-starter-flow-with-wfx-serve) | Serve one or more flows as FastAPI endpoints at `/flows/{flow_id}/run` |
| [`wfx run`](#run-the-simple-agent-flow-with-wfx-run) | Execute a flow locally and stream results to `stdout` |
| [`wfx-mcp`](#wfx-mcp) | Start an MCP server that connects to a running Primeagent instance |

**Flow DevOps SDK commands** — documented in the [Flow DevOps Toolkit](https://docs.prime.khulnasoft.com/flow-devops-sdk):

| Command | Description |
|---------|-------------|
| `wfx init` | Scaffold a versioned flow project with CI templates |
| `wfx login` | Validate credentials against a remote Primeagent instance |
| `wfx create` | Create a new flow JSON from a built-in or custom template |
| `wfx validate` | Validate flow JSON before pushing |
| `wfx requirements` | Generate `requirements.txt` from a flow's component dependencies |
| `wfx status` | Compare local flow files against a remote Primeagent instance |
| `wfx push` | Push flows to a remote instance by stable ID |
| `wfx pull` | Pull flows from a remote instance to local files |
| `wfx export` | Normalize flow JSON for clean git diffs |

## Prerequisites

- Install [Python](https://www.python.org/downloads/release/python-3100/).
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Create or download a flow JSON file. For example, download the Simple Agent flow from the repository:

  ```bash
  curl -o simple-agent-flow.json "https://raw.githubusercontent.com/khulnasoft-bot/primeagent/main/src/backend/base/primeagent/initial_setup/starter_projects/Simple%20Agent.json"
  ```

- Create an [OpenAI API key](https://platform.openai.com/api-keys).
- Create a Primeagent API key. For WFX, you can generate a secure token locally (see [Serve the simple agent starter flow with `wfx serve`](#serve-the-simple-agent-starter-flow-with-wfx-serve)), or create one through the Primeagent server UI or CLI.

## Install WFX

WFX can be installed in multiple ways. If you have installed Primeagent OSS version >=1.6, `wfx` is already included.

### Clone repository

1. Clone the Primeagent repository:

   ```bash
   git clone https://github.com/khulnasoft-bot/primeagent
   ```

2. Change directory to `primeagent/src/wfx`:

   ```bash
   cd primeagent/src/wfx
   ```

   From this directory, you can run `wfx` commands using `uv run wfx` as shown in [wfx serve](#serve-the-simple-agent-starter-flow-with-wfx-serve) or [wfx run](#run-the-simple-agent-flow-with-wfx-run).

### Install from PyPI

1. Create and activate a virtual environment:

   ```bash
   uv venv wfx-venv
   source wfx-venv/bin/activate
   ```

2. Install the WFX package from PyPI:

   ```bash
   uv pip install wfx
   ```

   To install the latest nightly (pre-release) version of WFX:

   ```bash
   uv pip install --pre wfx
   ```

   To run `wfx` commands, continue to [wfx serve](#serve-the-simple-agent-starter-flow-with-wfx-serve) or [wfx run](#run-the-simple-agent-flow-with-wfx-run).

### Run without installing

Run WFX without installing it locally using `uvx`.

1. Create a Primeagent API key (see [Serve](#serve-the-simple-agent-starter-flow-with-wfx-serve)), and set `PRIMEAGENT_API_KEY` in the same terminal session as `wfx`:

   ```bash
   export PRIMEAGENT_API_KEY="sk..."
   ```

2. Run `wfx serve` using `uvx`:

   ```bash
   uvx wfx serve simple-agent-flow.json
   ```

   This command downloads and runs WFX in a temporary environment without permanent installation. From the same environment, you can also run flows directly with [wfx run](#run-the-simple-agent-flow-with-wfx-run).

## Serve the simple agent starter flow with `wfx serve`

`wfx serve` starts a FastAPI server that hosts one or more flows. You can load flows at startup from files or a directory, or start with an empty registry and upload flows via the API. Once running, flows are available at `POST /flows/{flow_id}/run`.

`wfx serve` accepts a `.json` flow file or a `.py` Python script (same as `wfx run`), as well as inline JSON via `--flow-json` or piped input via `--stdin`.

`wfx serve` accepts a `.json` flow file or a `.py` Python script (same as `wfx run`), as well as inline JSON via `--flow-json` or piped input via `--stdin`.

The API key is required for security because `wfx serve` can create a publicly accessible FastAPI server.

This example uses the **Agent** component's built-in OpenAI model, which requires an OpenAI API key. If you want to use a different provider, edit the model provider, model name, and credentials accordingly.

1. Generate a Primeagent API key.

   For WFX, you can generate a secure token locally to use as your `PRIMEAGENT_API_KEY`:

   ```bash
   uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   This is different from creating a Primeagent API key through the Primeagent server UI or CLI, which stores the key in the Primeagent database. For WFX, you only need a secure token string to authenticate requests to your WFX server.

2. Set up your environment variables using one of the following options.

   **Option: .env file**

   Create a `.env` file and populate it with your flow's variables. The `PRIMEAGENT_API_KEY` is required. This example assumes the flow requires an OpenAI API key.

   ```bash
   PRIMEAGENT_API_KEY="sk..."
   OPENAI_API_KEY="sk-..."
   ```

   **Option: Export variables**

   Export your variables in the same terminal session where you'll start the server. You must declare your variables before the server starts for the server to pick them up.

   ```bash
   export PRIMEAGENT_API_KEY="sk..."
   export OPENAI_API_KEY="sk-..."
   ```

3. Install dependencies.

   If you already have Primeagent installed, or if you're running from source at `src/wfx`, WFX is included with Primeagent and all dependencies are already available. You don't need to install additional dependencies.

   If you install the standalone `wfx` package from [PyPI](https://pypi.org/project/wfx/) or run WFX with `uvx`, you need to manually install the dependencies required by the components in your flow.

   To find which dependencies your flow requires:

   1. Run your flow with [wfx run](#run-the-simple-agent-flow-with-wfx-run):

      ```bash
      uv run wfx run simple-agent-flow.json "test input"
      ```

      WFX reports any missing dependencies in the subsequent error message.
   2. Install the missing dependencies that WFX reports.

   For example, to run the simple agent template flow, install these dependencies in your environment before running the simple agent flow:

   ```bash
   uv pip install "langchain~=0.3.23" "langchain-core<1.0.0" "langchain-community" "langchain-openai" "langchain-text-splitters" beautifulsoup4 lxml requests
   ```

4. Start the server with your variable values using one of the following options.

   **Option: .env file**

   This example assumes your flow file and `.env` file are in the current directory:

   ```bash
   uv run wfx serve simple-agent-flow.json --env-file .env
   ```

   If your `.env` file is in a different location, provide the full or relative path:

   ```bash
   uv run wfx serve simple-agent-flow.json --env-file /path/to/.env
   ```

   **Option: Export variables**

   If you exported your variables, the command to start the server automatically picks up the values when it starts:

   ```bash
   uv run wfx serve simple-agent-flow.json
   ```

   To export new values, stop the server, export the variables, and then start the server again.

5. The startup process displays a `flow_id` value in the output. Copy the `flow_id` to use in the test API call in the next step. In this example, the `flow_id` is `c1dab29d-3364-58ef-8fef-99311d32ee42`:

   ```
    WFX Server
    Flow loaded: simple-agent-flow.json (c1dab29d-3364-58ef-8fef-99311d32ee42)
    Server:      http://127.0.0.1:8000
    Run flows at: POST /flows/{flow_id}/run
    API key:     x-api-key header or ?x-api-key= query parameter
   ```

6. To send a test request to the server, open a new terminal and export your `flow_id` and Primeagent API key values as variables:

   ```bash
   export PRIMEAGENT_API_KEY="sk..."
   export FLOW_ID="c1dab29d-3364-58ef-8fef-99311d32ee42"
   ```

7. Test the server with an API call to the `/flows/flow_id/run` endpoint:

   ```bash
   curl -X POST http://localhost:8000/flows/$FLOW_ID/run \
     -H "Content-Type: application/json" \
     -H "x-api-key: $PRIMEAGENT_API_KEY" \
     -d '{"input_value": "Hello, world!"}'
   ```

   Successful response example:

   ```json
   {
     "result": "Hello world! 👋\n\nHow can I help you today? If you have any questions or need assistance, just let me know!",
     "success": true,
     "logs": "\n\n\u001b[1m> Entering new None chain...\u001b[0m\n\u001b[32;1m\u001b[1;3mHello world! 👋\n\nHow can I help you today?...\u001b[0m\n\n\u001b[1m> Finished chain.\u001b[0m\n",
     "type": "message",
     "component": "Chat Output"
   }
   ```

Your flow is now running as a lightweight API endpoint, with only the flow's required dependencies and no visual builder installed. Users who call your endpoint don't need to install Primeagent or configure their own LLM provider keys.

To make your server publicly accessible, use a tunneling service like ngrok or deploy to a public cloud provider.

### HTTP endpoints

The WFX server exposes the following endpoints. All `/flows/{flow_id}` routes require the `x-api-key` header or `?x-api-key=` query parameter.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/flows` | GET | List all served flows and their metadata |
| `/flows/upload/` | POST | Upload a flow JSON to the registry (accepts full Primeagent export format) |
| `/flows/{flow_id}/run` | POST | Run the flow and return a single response |
| `/flows/{flow_id}/stream` | POST | Run the flow and stream output as server-sent events |
| `/flows/{flow_id}/info` | GET | Return flow metadata (title, description, input/output types) |
| `/health` | GET | Global health check — returns `{"status": "ok"}` |
| `/docs` | GET | Auto-generated OpenAPI/Swagger UI |

### Request body schema

**`POST /flows/{flow_id}/run`**

```json
{
  "input_value": "Your message here",
  "session_id": "optional-conversation-id"
}
```

`session_id` is optional. When set, Agent and Memory components use it to maintain conversation history across multiple calls. If omitted, a new session ID is generated for each request.

**`POST /flows/{flow_id}/stream`**

```json
{
  "input_value": "Your message here",
  "input_type": "chat",
  "output_type": "chat",
  "output_component": null,
  "session_id": "optional-conversation-id",
  "tweaks": {"ComponentName": {"param": "value"}}
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `input_value` | — | Required. Input passed to the flow. |
| `input_type` | `"chat"` | Input type: `chat` or `text`. |
| `output_type` | `"chat"` | Output type: `chat`, `text`, `debug`, or `any`. |
| `output_component` | `null` | Pin output to a specific component by name. |
| `session_id` | `null` | Conversation ID for memory continuity across requests. |
| `tweaks` | `null` | Per-request parameter overrides. Keys are component names; values are dicts of parameter overrides. Use this to parameterize a flow without modifying the JSON. |

### Response schema

The WFX server's response schema is different from the Primeagent API `/run` endpoint's schema. Requests to the WFX server's `/flows/{flow_id}/run` endpoint return the following fields:

```json
{
  "result": "string",      // Output result from the flow execution
  "success": true,         // Whether execution was successful
  "logs": "string",        // Captured logs from execution
  "type": "message",       // Type of result
  "component": "string"    // The component that generated the result (e.g. "Chat Output")
}
```

The `/stream` endpoint returns the same fields as server-sent events, with one event per component output.

### Serve multiple flows at startup

You can pass a directory, multiple file paths, or a mix of both to load several flows at startup. Each flow is registered under its own ID.

```bash
# Serve every .json file in a directory (top-level only, not recursive)
uv run wfx serve flows/

# Serve specific files
uv run wfx serve flow-a.json flow-b.json

# Mix directory and individual files
uv run wfx serve flows/ extra-flow.json
```

Python `.py` script flows are also supported when using a single worker:

```bash
uv run wfx serve my_flow.py
```

### Start with no flows

`wfx serve` starts with an empty registry when no flow path is provided. Flows can then be uploaded via the API:

```bash
uv run wfx serve --env-file .env
```

### Upload flows dynamically

While the server is running, upload flows with `POST /flows/upload/`.

The endpoint accepts the full Primeagent export JSON directly, the same format you get from the Primeagent UI's **Export** button:

```bash
# Upload a flow JSON file
curl -X POST http://localhost:8000/flows/upload/ \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d @my-flow.json

# Upload and replace an existing flow with the same ID
curl -X POST "http://localhost:8000/flows/upload/?replace=true" \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d @my-flow.json
```

The server returns a `409 Conflict` error if you upload a flow whose ID is already registered and `replace=true` is not set.

### Multi-worker deployment

Use `--workers N` to start multiple uvicorn worker processes, and `--flow-dir` to point all workers at a shared directory so they serve the same flows.

```bash
# 4 workers, flows shared via a local temp directory
uv run wfx serve flows/ --workers 4 --flow-dir /tmp/wfx-flows

# Cross-pod sharing (Kubernetes PVC or similar network volume)
uv run wfx serve flows/ --workers 4 --flow-dir /mnt/shared-flows
```

How it works:

- Each startup flow file is persisted to `--flow-dir` as `{flow_id}.json` when the server starts.
- Uploads via `POST /flows/upload/` are also written to `--flow-dir`, making them visible to every worker on the next request.
- Deletes propagate across workers: each worker detects a missing file on the next request to that flow and returns `404`.
- Without `--flow-dir`, each worker maintains an isolated in-memory registry. Uploads reach only the worker that received the request.

> **Note:** `--workers > 1` with `--flow-dir` does not support `.py` script flows — Python graphs cannot be serialized to the filesystem store.

A warning is printed when `--workers > 1` is used without `--flow-dir`, because in that case each worker has its own isolated in-memory registry.

### Isolate credentials with `--no-env-fallback` _(experimental)_

By default, `wfx serve` resolves component credentials from the process environment (`os.environ`). In multi-tenant deployments, this means every request shares the same credentials.

Use `--no-env-fallback` to disable process-environment fallback. With this flag set, credentials must be supplied per-request in the `global_vars` field of the request body:

```bash
uv run wfx serve my-flow.json --no-env-fallback --env-file .env
```

Pass per-request credentials in the `global_vars` map under `PRIMEAGENT_REQUEST_VARIABLES`:

```bash
curl -X POST http://localhost:8000/flows/$FLOW_ID/run \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PRIMEAGENT_API_KEY" \
  -d '{
    "input_value": "Hello world",
    "global_vars": {
      "PRIMEAGENT_REQUEST_VARIABLES": {
        "OPENAI_API_KEY": "sk-per-request-key"
      }
    }
  }'
```

Credentials supplied in `PRIMEAGENT_REQUEST_VARIABLES` are scoped to the current request using Python `contextvars`. Primeagent's built-in components do not write them to `os.environ`, so they do not bleed into other concurrent requests on the same worker. Custom components that explicitly write to `os.environ` are outside this guarantee.

### Check or upgrade flow compatibility at startup

Use `--upgrade-flow` to check compatibility between a flow and the current WFX version before serving it. See [WFX and Primeagent version compatibility](https://docs.prime.khulnasoft.com/wfx-compatibility) for details on the version model.

```bash
# Fail at startup if any component is incompatible
uv run wfx serve my-flow.json --upgrade-flow=check

# Apply safe upgrades in memory, then start serving
uv run wfx serve my-flow.json --upgrade-flow=safe
```

### WFX serve options

| Option | Description |
|--------|--------------|
| `--check-variables` / `--no-check-variables` | Check global variables for environment compatibility. Default: `--check-variables`. |
| `--env-file` | Path to the `.env` file containing environment variables. |
| `--flow-dir` | Directory for the filesystem-backed flow store shared across workers. When set, startup flows and uploads are persisted here. |
| `--flow-json` | Read inline flow JSON content as a string. Example: `uv run wfx serve --flow-json '{...}'`. |
| `--host`, `-h` | Host to bind the server to. Default: `127.0.0.1`. |
| `--log-level` | Logging level. One of: `debug`, `info`, `warning`, `error`, `critical`. Default: `warning`. |
| `--no-env-fallback` / `--env-fallback` | Disable process-environment fallback for credential resolution. Use with per-request `PRIMEAGENT_REQUEST_VARIABLES`. Default: `--env-fallback`. |
| `--port`, `-p` | Port to bind the server to. Default: `8000`. |
| `--stdin` | Read JSON flow content from `stdin`. Example: `cat flow.json | uv run wfx serve --stdin`. |
| `--max-requests` | Recycle each worker after N requests to bound memory (gunicorn, Unix, `--workers > 1`). Default: every ~1000 (10% jitter); `0` disables; `1` = every request. Worker hygiene, **not** per-request isolation. Not applied on Windows. |
| `--reset-environ` / `--no-reset-environ` | Snapshot/restore `os.environ` around each flow run so one request's env mutations or request-scoped credentials can't leak into the next on a warm worker. **A strict per-request isolation mechanism** (any worker, any platform). Default: `--no-reset-environ` (off). |
| `--use-sync-workers` / `--use-async-workers` | Multi-worker only (`--workers > 1`, Unix). gunicorn's blocking `sync` worker serves one request at a time per worker, so the kernel routes each to an idle worker. With `--max-requests 1` it is **the other strict per-request isolation mechanism** (each request gets a fresh process). Uses the `a2wsgi` bridge, which ships with wfx on Unix. Default: `--use-async-workers`. |
| `--timeout` | Worker timeout in seconds (gunicorn, Unix, `--workers > 1`): a worker that doesn't finish a request in this many seconds is killed and restarted. Raise it for long flows, especially with `--use-sync-workers`. Default: `120`. No effect on Windows. |
| `--upgrade-flow` | Compatibility mode: `check` reports issues and fails, `safe` applies safe upgrades in memory. |
| `--verbose`, `-v` | Show diagnostic output and execution details. |
| `--workers`, `-w` | Number of worker processes. Use with `--flow-dir` for multi-worker flow sharing. Default: `1`. |

## Run the simple agent flow with `wfx run`

The `wfx run` command runs a flow from a JSON file without serving it, and the output is sent to `stdout`. Input to `wfx run` can be a path to the JSON file, inline JSON passed with `--input-value`, or read from `stdin`. No Primeagent API key is required.

This example uses the **Agent** component's built-in OpenAI model, which requires an OpenAI API key. If you want to use a different provider, edit the model provider, model name, and credentials accordingly.

1. Export your variables in the same terminal session where you'll run the flow:

   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. Install dependencies.

   If you already have Primeagent installed, or if you're running from source at `src/wfx`, WFX is included with Primeagent and all dependencies are already available. You don't need to install additional dependencies.

   If you install the standalone `wfx` package from [PyPI](https://pypi.org/project/wfx/) or run WFX with `uvx`, you need to manually install the dependencies required by the components in your flow.

   To find which dependencies your flow requires:

   1. Run your flow with [wfx run](#run-the-simple-agent-flow-with-wfx-run):

      ```bash
      uv run wfx run simple-agent-flow.json "test input"
      ```

      WFX reports any missing dependencies in the subsequent error message.
   2. Install the missing dependencies that WFX reports.

   For example, to run the simple agent template flow, install these dependencies in your environment before running the simple agent flow:

   ```bash
   uv pip install "langchain~=0.3.23" "langchain-core<1.0.0" "langchain-community" "langchain-openai" "langchain-text-splitters" beautifulsoup4 lxml requests
   ```

3. Run the flow from a flow JSON file:

   ```bash
   uv run wfx run simple-agent-flow.json "Hello world"
   ```

   This flow expects a `Message` input, which is a simple text string.

   You can also use the `--input-value` flag instead of a positional argument:

   ```bash
   uv run wfx run simple-agent-flow.json --input-value "Hello world"
   ```

   The `--input-value` flag is required when using `--stdin` or `--flow-json` options, since those options use the positional argument for the flow definition instead of the input value.

In addition to running flows from JSON files, `wfx run` supports other input methods, described below.

### Run flows from stdin

The `--stdin` option lets you run flows from dynamic sources (APIs, databases) or after modifying a flow before execution. The command reads the flow's JSON definition from `stdin`, validates the JSON structure, and runs the flow. The `--input-value` flag is required when using `--stdin`.

Read a flow JSON from stdin:

```bash
cat simple-agent-flow.json | uv run wfx run --stdin \
  --input-value "Hello world" \
  --format json | jq '.result'
```

Fetch a flow JSON from a remote API and run it:

```bash
curl https://api.example.com/flows/my-agent-flow | uv run wfx run --stdin \
  --input-value "Hello world"
```

Modify a flow created in the visual builder before execution (e.g. change the OpenAI model to `gpt-4o`):

```bash
cat simple-agent-flow.json | jq '(.data.nodes[] | select(.data.node.template.model_name.value) | .data.node.template.model_name.value) = "gpt-4o"' | \
  uv run wfx run --stdin \
  --input-value "Hello world" \
  --format json | jq '.result'
```

### Run flows with inline JSON

Instead of piping from `stdin` or reading from a JSON file, you can pass the flow JSON directly as a string argument. The `--input-value` flag is required when using `--flow-json`.

```bash
uv run wfx run --flow-json '{"data": {"nodes": [...], "edges": [...]}}' \
  --input-value "Hello world"
```

### WFX run options

| Option | Description |
|--------|--------------|
| `--check-variables` / `--no-check-variables` | Validate the flow's global variables. Default: check. |
| `--flow-json` | Load inline JSON flow content as a string. |
| `--format`, `-f` | Output format. One of: `json`, `text`, `message`, `result`. Default: `json`. |
| `--input-value` | Input value to pass to the graph. |
| `--session-id` | Session ID for conversation tracking. Agent and Memory components use this to maintain history across runs. Auto-generated if not set. |
| `--stdin` | Read JSON flow content from `stdin`. |
| `--timing` | Include detailed timing information in output. |
| `--upgrade-flow` | Compatibility mode: `check` reports issues and fails, `safe` applies safe upgrades in memory before running. |
| `--verbose`, `-v` | Show basic progress and diagnostic output. |
| `-vv` | Show detailed progress and debug information. |
| `-vvv` | Show full debugging output including component logs. |

In addition to running flows from JSON files, you can use `wfx run` with Python scripts that define flows programmatically. This approach allows you to create flows directly in Python code without the visual builder.

For a complete example of creating an agent flow programmatically using WFX components, see the [Complete Agent Example on PyPI](https://pypi.org/project/wfx) or the **Complete Agent Example** below.

#### Complete agent example

Create a file called `simple_agent.py`:

```python
"""A simple agent flow example for Primeagent.

Usage:
    uv run wfx run simple_agent.py "How are you?"
"""

import os
from pathlib import Path

from wfx import components as cp
from wfx.graph import Graph
from wfx.log.logger import LogConfig


async def get_graph() -> Graph:
    """Create and return the graph with async component initialization."""
    log_config = LogConfig(
        log_level="INFO",
        log_file=Path("primeagent.log"),
    )

    chat_input = cp.ChatInput()
    agent = cp.AgentComponent()
    url_component = cp.URLComponent()
    tools = await url_component.to_toolkit()

    agent.set(
        model_name="gpt-4.1-mini",
        agent_llm="OpenAI",
        api_key=os.getenv("OPENAI_API_KEY"),
        input_value=chat_input.message_response,
        tools=tools,
    )
    chat_output = cp.ChatOutput().set(input_value=agent.message_response)

    return Graph(chat_input, chat_output, log_config=log_config)
```

Install dependencies and set your OpenAI API key, then run:

```bash
uv run wfx run simple_agent.py "How are you?" --verbose
```

### Human-in-the-loop with `wfx run`

When a flow contains a pausing node (such as **Human Input**) and the terminal is interactive, `wfx run` automatically pauses at each decision point and prompts on the terminal; the run then continues down the chosen branch. Use `--human-input` / `--no-human-input` to force the behavior either way.

CLI HITL is **interactive-session only**:

- Checkpoints are held **in memory** — if the process exits while paused, the run is lost.
- There is **no durable resume**: a paused run cannot be resumed later, from another terminal, or after a restart (no `--resume <id>`).
- A **non-interactive** run (piped stdin, CI, or `--no-human-input`) does **not** pause: the pausing node is passed through and the run continues; the CLI prints a warning so this is never silent.

For durable pause/resume that survives restarts, run the flow through the Primeagent server's v2 workflows API instead.

## wfx-mcp

`wfx-mcp` is a separate binary installed with `wfx`. It starts an MCP server that gives any MCP-compatible client programmatic control over a Primeagent instance for building flows, managing components, and running executions.

For more information, see [WFX_MCP.md](./WFX_MCP.md).

## Development

```bash
# Install development dependencies
make dev

# Run tests
make test

# Format code
make format
```

## Pluggable services

WFX supports a pluggable service architecture that lets you customize and extend its behavior. You can replace built-in services (storage, telemetry, tracing, etc.) with your own implementations or use Primeagent's full-featured services.

For more information, see [PLUGGABLE_SERVICES.md](./PLUGGABLE_SERVICES.md).

## Flattened component access

WFX supports simplified component imports for a better developer experience when building flows in Python.
You get simpler imports, easier discovery via `cp.ComponentName`, and full backward compatibility with the traditional import method.

**Before (old import style):**

```python
from wfx.components.agents.agent import AgentComponent
from wfx.components.data.url import URLComponent
from wfx.components.input_output import ChatInput, ChatOutput
```

**Now (flattened style):**

```python
from wfx import components as cp

chat_input = cp.ChatInput()
agent = cp.AgentComponent()
url_component = cp.URLComponent()
chat_output = cp.ChatOutput()
```

## Component category allowlist and blocklist

You can restrict which component categories are available when loading flows by using an allowlist or a blocklist.

### Environment variables

Both settings are optional. When unset or empty, all categories from the component index are loaded.

| Variable | Description |
|----------|-------------|
| `PRIMEAGENT_COMPONENT_CATEGORY_ALLOWLIST` | Comma-separated list of component category names to **include**. If empty (default), all categories are included. If set, only the listed categories are available. |
| `PRIMEAGENT_COMPONENT_CATEGORY_BLOCKLIST` | Comma-separated list of component category names to **exclude**. If empty (default), no categories are excluded. Applied after the allowlist. |

Category names are case-insensitive.

### Component categories

Category names in the allowlist and blocklist match the component index (e.g. top-level folders under `wfx.components`). The virtual keyword **`core`** in the allowlist or blocklist expands to the following core categories (aligned with the frontend sidebar):

- `input_output`, `data_source`, `models_and_agents`, `llm_operations`, `files_and_knowledge`, `processing`, `flow_controls`, `utilities`, `prototypes`, `tools`, `agents`, `data`, `logic`, `helpers`, `models`, `vectorstores`, `inputs`, `outputs`, `prompts`, `chains`, `documentloaders`, `link_extractors`, `output_parsers`, `retrievers`, `textsplitters`, `toolkits`

Provider-specific and other categories (e.g. `openai`, `anthropic`, `google`, `langchain_utilities`) are also valid; the full set depends on your WFX version and index.

### How to use in WFX

1. Set one or both environment variables before running `wfx serve` or `wfx run`. The filter is applied when the component index is loaded.

Allowlist only — restrict to specific categories:

   ```bash
   export PRIMEAGENT_COMPONENT_CATEGORY_ALLOWLIST="openai,anthropic,google,processing,input_output"
   uv run wfx serve my_flow.json
   ```

Blocklist only — load all categories except the ones you exclude:

   ```bash
   export PRIMEAGENT_COMPONENT_CATEGORY_BLOCKLIST="prototypes,langchain_utilities"
   uv run wfx run my_flow.json "Hello"
   ```

Virtual `core` keyword — use `core` in the allowlist or blocklist to refer to all core categories at once (e.g. allow only core categories, or exclude all core from a broader set):

   ```bash
   export PRIMEAGENT_COMPONENT_CATEGORY_ALLOWLIST="core"
   uv run wfx serve my_flow.json
   ```

## License

MIT License. See [LICENSE](../../LICENSE) for details.
