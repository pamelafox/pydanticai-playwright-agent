# Pydantic AI + Playwright MCP

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/pamelafox/pydanticai-playwright-agent)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/pamelafox/pydanticai-playwright-agent)

This repository is a small, reusable example of combining Pydantic AI, Azure OpenAI, and the
Playwright MCP capability. The included workflow demonstrates read-only website QA, but developers
can fork it for other combinations of Pydantic AI agents, Playwright browser tools, and MCP-style
capabilities.

* [Getting started](#getting-started)
  * [GitHub Codespaces](#github-codespaces)
  * [VS Code Dev Containers](#vs-code-dev-containers)
  * [Local environment](#local-environment)
* [Deploying Azure model](#deploying-azure-model)
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

## Deploying Azure model

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

## Running the agent

The [example file](pydanticai_playwright.py) combines an Azure OpenAI Pydantic AI agent
with the Pydantic AI Harness `PlaywrightBrowser` MCP capability. Its included workflow performs a
read-only QA pass against a website you own: it loads the URL, creates a testing plan, explores safe
same-site journeys, and writes a report to `outputs/qa-report.md`. Forks can replace the system
instructions, tools, and artifact workflow for other Pydantic AI and Playwright applications.

This example is built on the [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/) and the
[`PlaywrightBrowser` capability PR](https://github.com/pydantic/pydantic-ai-harness/pull/420).
The dependency is temporarily pinned to commit
`730130f3322936f0396afa933b2f4184fc0028bf` from `backport/browser` because the capability is not
yet being consumed from a released package. After the capability is released, replace the VCS
dependency in `pyproject.toml` with the released version, run `uv lock`, and run `uv sync` again.

### Install and run

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

Authenticated runs are optional. Create a site-scoped Playwright storage state by logging in
interactively once:

```shell
mkdir -p playwright/.auth
uv run playwright codegen https://your-owned-site.example/ --save-storage=playwright/.auth/site.json
uv run python pydanticai_playwright.py https://your-owned-site.example/ \
    --session-state playwright/.auth/site.json
```

Storage state contains cookies and local storage that can impersonate an account. It is gitignored,
must not be shared, and should be deleted when the session expires. Do not use a real Chrome profile or browser-extension attachment.

## OpenTelemetry

### Logfire configuration

Tracing is written locally by default. If `LOGFIRE_TOKEN` is present, the example also sends traces
to Logfire; otherwise no Logfire cloud export is attempted. Do not commit the token or generated
trace files.

### Azure Application Insights configuration

If `APPLICATIONINSIGHTS_CONNECTION_STRING` is present, the example also sends traces to Azure
Application Insights. Do not commit the connection string or generated trace files.

## Resources

* [Pydantic AI Documentation](https://ai.pydantic.dev/)
