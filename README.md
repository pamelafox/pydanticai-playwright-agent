<!--
---
name: PydanticAI Python Demos
description: Collection of PydanticAI examples using Azure OpenAI.
languages:
- python
products:
- azure-openai
- azure
page_type: sample
urlFragment: python-ai-agent-frameworks-demos
---
-->
# PydanticAI Python Demos

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/Azure-Samples/python-ai-agent-frameworks-demos)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Azure-Samples/python-ai-agent-frameworks-demos)

This repository provides examples of Python AI agents built with PydanticAI.

* [Getting started](#getting-started)
  * [GitHub Codespaces](#github-codespaces)
  * [VS Code Dev Containers](#vs-code-dev-containers)
  * [Local environment](#local-environment)
* [Configuring model providers](#configuring-model-providers)
  * [Using Azure OpenAI models](#using-azure-openai-models)
  * [Using OpenAI.com models](#using-openaicom-models)
  * [Using Ollama models](#using-ollama-models)
* [Running the Python examples](#running-the-python-examples)
* [Resources](#resources)

## Getting started

You have a few options for getting started with this repository.
The quickest way to get started is GitHub Codespaces, since it will setup everything for you, but you can also [set it up locally](#local-environment).

### GitHub Codespaces

You can run this repository virtually by using GitHub Codespaces. Click one of the buttons below to open a web-based VS Code instance in your browser:

**Default (Azure OpenAI):**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/python-ai-agent-frameworks-demos)

**Ollama (local models, requires 64GB+ memory):**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure-Samples/python-ai-agent-frameworks-demos?devcontainer_path=.devcontainer/ollama/devcontainer.json)

The Ollama Codespace pre-installs Ollama and pulls the `gemma4:e4b` model, and copies `.env.sample.ollama` as your `.env` file. Note that the 64GB memory requirement will consume your Codespace quota faster.

Once the Codespace is open, open a terminal window and continue with the steps to run the examples.

### VS Code Dev Containers

A related option is VS Code Dev Containers, which will open the project in your local VS Code using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed)
2. Open the project:

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Azure-Samples/python-ai-agent-frameworks-demos)

3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a terminal window.
4. Continue with the steps to run the examples

### Local environment

1. Make sure the following tools are installed:

    * [Python 3.10+](https://www.python.org/downloads/)
    * Git

2. Clone the repository:

    ```shell
    git clone https://github.com/Azure-Samples/python-ai-agent-frameworks-demos
    cd python-ai-agent-frameworks-demos
    ```

3. Set up a virtual environment:

    ```shell
3. Create a virtual environment and install dependencies:

    ```shell
    uv sync
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

## Configuring model providers

These examples can be run with Azure OpenAI account, OpenAI.com, or local Ollama server, depending on the environment variables you set. All the scripts reference the environment variables from a `.env` file, and an example `.env.sample` file is provided. Host-specific instructions are below.

## Using Azure OpenAI models

To run the examples using models from Azure OpenAI, you need to provision the Azure AI resources, which will incur costs.

This project includes infrastructure as code (IaC) to provision an Azure OpenAI deployment of "gpt-5.4". The IaC is defined in the `infra` directory and uses the Azure Developer CLI to provision the resource.

1. Make sure the [Azure Developer CLI (azd)](https://aka.ms/install-azd) is installed.

2. Login to Azure:

    ```shell
    azd auth login
    ```

    For GitHub Codespaces users, if the previous command fails, try:

   ```shell
    azd auth login --use-device-code
    ```

3. Provision the OpenAI account:

    ```shell
    azd provision
    ```

    It will prompt you to provide an `azd` environment name (like "agents-demos"), select a subscription from your Azure account, and select a location. Then it will provision the resources in your account.

4. Once the resources are provisioned, you should now see a local `.env` file with all the environment variables needed to run the scripts.
5. To delete the resources, run:

    ```shell
    azd down
    ```

## Running the Playwright manual QA example

The Playwright example uses Azure OpenAI, the pinned Pydantic AI Harness browser capability, and a
filesystem rooted at `outputs/`. It is a read-only manual QA agent for websites you own: it loads the
URL you provide, makes a test plan, explores safe user journeys, and writes usability and bug findings
to `outputs/qa-report.md`. The host allowlist is derived from the supplied URL, and the agent does not
follow links to other domains.

After Azure authentication and configuration, install the Python and browser dependencies:

```shell
uv sync
uv run playwright install chromium
```

Set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_CHAT_DEPLOYMENT` in `.env`, then run:

```shell
uv run python examples/pydanticai_playwright.py https://www.pamelafox.org
```

Authenticated QA is optional. To create a site-scoped Playwright storage state, log in interactively
once with:

```shell
mkdir -p playwright/.auth
uv run playwright codegen https://your-owned-site.example/ --save-storage=playwright/.auth/site.json
```

Close the browser after logging in, then pass the state file explicitly:

```shell
uv run python examples/pydanticai_playwright.py https://your-owned-site.example/ \
    --session-state playwright/.auth/site.json
```

The auth file contains cookies and local storage that can impersonate the account, so it is
gitignored, must not be shared, and should be deleted when the session expires. Do not use a real
Chrome profile or browser-extension attachment. The agent will not submit forms, send messages,
change settings, or perform other consequential actions.

Reports and traces are written below `outputs/`; absolute paths and paths outside that directory are
blocked by the Harness `FileSystem` capability. The browser dependency is pinned to Harness commit
`730130f3322936f0396afa933b2f4184fc0028bf` (PR #420 / `backport/browser`) until a release is available.

The example also writes local OpenTelemetry JSON spans to `outputs/traces.jsonl`. Cloud Logfire
export is disabled. The trace file includes model prompts/results and tool output to help diagnose
slow browsing, so treat it as sensitive local data and do not share it. Inspect it with a JSONL
viewer or commands such as `jq` after a run.

For accessibility-tree debugging, enable opt-in snapshot logging before a run:

```shell
DEBUG_BROWSER_SNAPSHOTS=1 uv run python examples/pydanticai_playwright.py https://www.pamelafox.org
```

Snapshots are saved as JSONL in `outputs/debug/snapshots.jsonl`. They can contain page text,
links, and other sensitive content, so inspect and delete them locally when finished.

## Using OpenAI.com models

1. Create a `.env` file by copying the `.env.sample` file and updating it with your OpenAI API key and desired model name.

    ```bash
    cp .env.sample .env
    ```

2. Update the `.env` file with your OpenAI API key and desired model name:

    ```bash
    API_HOST=openai
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_MODEL=gpt-4o-mini
    ```

## Using Ollama models

1. Install [Ollama](https://ollama.com/) and follow the instructions to set it up on your local machine.
2. Pull a model, for example:

    ```shell
    ollama pull qwen3:30b
    ```

    Note that most models do not support tool calling to the extent required by agents frameworks, so choose a model accordingly.

3. Create a `.env` file by copying the `.env.sample` file and updating it with your Ollama endpoint and model name.

    ```bash
    cp .env.sample .env
    ```

4. Update the `.env` file with your Ollama endpoint and model name (any model you've pulled):

    ```bash
    API_HOST=ollama
    OLLAMA_ENDPOINT=http://localhost:11434/v1
    OLLAMA_MODEL=gemma4:e4b
    ```

## Running the Python examples

### PydanticAI

| Example | Description |
| ------- | ----------- |
| [pydanticai_basic.py](examples/pydanticai_basic.py) | Uses PydanticAI to build a basic single agent. |
| [pydanticai_multiagent.py](examples/pydanticai_multiagent.py) | Uses PydanticAI to build a two-agent sequential workflow (flight + seat selection). |
| [pydanticai_supervisor.py](examples/pydanticai_supervisor.py) | Uses PydanticAI with a supervisor orchestrating multiple agents. |
| [pydanticai_graph.py](examples/pydanticai_graph.py) | Uses PydanticAI with pydantic-graph to build a small question/answer evaluation graph. |
| [pydanticai_tools.py](examples/pydanticai_tools.py) | Uses PydanticAI with multiple Python tools for weekend activity planning. |
| [pydanticai_playwright.py](examples/pydanticai_playwright.py) | Uses Azure OpenAI, Playwright, and scoped files for prompt-driven read-only research. |
| [pydanticai_mcp_http.py](examples/pydanticai_mcp_http.py) | Uses PydanticAI with an MCP HTTP server toolset for travel planning (hotel search). |
| [pydanticai_mcp_github.py](examples/pydanticai_mcp_github.py) | Uses PydanticAI with an MCP GitHub server toolset to triage repository issues. |

## Resources

* [Pydantic AI Documentation](https://ai.pydantic.dev/multi-agent-applications/)
