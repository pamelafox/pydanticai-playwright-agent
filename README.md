# Pydantic AI + Playwright MCP

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/pamelafox/pydanticai-playwright-agent)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/pamelafox/pydanticai-playwright-agent)

This project shows you how to build a [Pydantic AI agent](https://pydantic.dev/docs/ai/) using a [Microsoft Foundry model](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure) and the [Playwright MCP server](https://playwright.dev/docs/getting-started-mcp). The example workflow is a website QA analysis agent, but you can customize the code for any browser-using agent scenario.

* [Getting started](#getting-started)
  * [GitHub Codespaces](#github-codespaces)
  * [VS Code Dev Containers](#vs-code-dev-containers)
  * [Local environment](#local-environment)
* [Deploying Azure OpenAI model](#deploying-azure-openai-model)
* [Running the agent](#running-the-agent)
  * [Install and run](#install-and-run)
  * [Allowed domains](#allowed-domains)
  * [Outputs](#outputs)
  * [Authentication](#authentication)
* [OpenTelemetry](#opentelemetry)
  * [Logfire configuration](#logfire-configuration)
  * [Azure Application Insights configuration](#azure-application-insights-configuration)
* [Resources](#resources)

## Getting started

You have a few options for getting started with this repository.
The quickest way to get started is GitHub Codespaces, since it will setup everything for you, but you can also [set it up locally](#local-environment).

### GitHub Codespaces

You can run this repository virtually by using GitHub Codespaces. Click one of the buttons below to open a web-based VS Code instance in your browser:

**Default (Azure OpenAI):**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/pamelafox/pydanticai-playwright-agent)

Once the Codespace is open, open a terminal window and continue with the steps to run the examples.

### VS Code Dev Containers

A related option is VS Code Dev Containers, which will open the project in your local VS Code using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed)
2. Open the project:

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/pamelafox/pydanticai-playwright-agent)

3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a terminal window.
4. Continue with the steps to run the examples

### Local environment

1. Make sure the following tools are installed:

    * [Python 3.10+](https://www.python.org/downloads/)
    * Git

2. Clone the repository:

    ```shell
    git clone https://github.com/pamelafox/pydanticai-playwright-agent
    cd pydanticai-playwright-agent
    ```

3. Create a virtual environment and install dependencies:

    ```shell
    uv sync
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

## Deploying the model

Pydantic AI agents can run with models from many providers, but the code in this project is currently configured to use an Azure OpenAI model from Microsoft Foundry.

This project includes infrastructure as code (IaC) to provision an Azure OpenAI deployment of "gpt-5.4". The IaC is defined in the `infra` directory and uses the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/) to provision the resource. Once you have an Azure account, run these steps:

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

## Running the agent

The [pydanticai_playwright.py](pydanticai_playwright.py) file combines a Pydantic AI `Agent`
with the `PlaywrightBrowser` MCP capability from the Pydantic AI harness.

1. Install the Python packages:

    ```shell
    uv sync
    ```

2. Download the Chromium browser used by Playwright:

    ```shell
    uv run playwright install chromium
    ```

3. Run the agent:

    ```shell
    uv run python pydanticai_playwright.py https://www.pamelafox.org
    ```

    By default, the agent uses Playwright to do a manual QA of the provided website URL
    and look for usability issues and potential bugs. The output is stored in `outputs/qa-report.md`. Change the URL to test on your website, or change the system prompt entirely for a different scenario.

### Allowed domains

The starting URL controls which site the browser can visit. In `pydanticai_playwright.py`,
`urlparse()` extracts its hostname and passes it to `PlaywrightBrowser(allowed_domains=[...])`.
The browser also uses `block_private_addresses=True` to reject private network addresses. The
allowlist is set by the code before the agent runs; the model and the webpage cannot add domains.

### Outputs

All generated files are confined to `outputs/`, including the report and local trace file
`outputs/traces.jsonl`. Absolute paths and path traversal outside that directory are rejected by the
Harness `FileSystem` capability. The trace can include model prompts, results, tool output, and page
content, so treat it as sensitive local data.

### Authentication

If your website requires authentication, you will first need to save a Playwright storage state JSON with the cookies for that website.

Create the storage state for the target website:

```shell
mkdir -p playwright/.auth
uv run playwright codegen https://your-owned-site.example/ --save-storage=playwright/.auth/site.json
```

Run the agent with the storage state:

```shell
uv run python pydanticai_playwright.py https://your-owned-site.example/ \
    --session-state playwright/.auth/site.json
```

⚠️ Storage state contains cookies and local storage that can impersonate an account. It is gitignored, must not be shared, and should be deleted when the session expires.

## OpenTelemetry

OpenTelemetry tracing is written locally by default.

### Logfire configuration

If `LOGFIRE_TOKEN` is present, the example also sends traces to Logfire; otherwise no Logfire cloud export is attempted.

### Azure Application Insights configuration

If `APPLICATIONINSIGHTS_CONNECTION_STRING` is present, the example also sends traces to Azure
Application Insights. Do not commit the connection string or generated trace files.

## Resources

* [Pydantic AI Documentation](https://ai.pydantic.dev/)
