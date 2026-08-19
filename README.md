# Pydantic AI + Playwright

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/pamelafox/pydanticai-playwright-agent)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/pamelafox/pydanticai-playwright-agent)

This project shows you how to build a [Pydantic AI agent](https://pydantic.dev/docs/ai/) using a [Microsoft Foundry model](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure) and the [Playwright](https://playwright.dev/python/) capability from Pydantic AI Harness. The example workflow is a website QA analysis agent, but you can customize the code for any browser-using agent scenario.

![Diagram showing a Pydantic AI agent using a Microsoft Foundry model and Playwright tools to inspect a website and write a QA report](readme_diagram.png)

* [Getting started](#getting-started)
  * [GitHub Codespaces](#github-codespaces)
  * [VS Code Dev Containers](#vs-code-dev-containers)
  * [Local environment](#local-environment)
* [Deploying the model](#deploying-the-model)
* [Running the agent](#running-the-agent)
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
with the `PlaywrightBrowser` capability from the Pydantic AI Harness.

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
`urlparse()` extracts its hostname into `website_hostname` and passes it to
`PlaywrightBrowser(allowed_domains=[website_hostname])`. Each allowlist entry matches its exact
host and its subdomains. The browser also uses `block_private_addresses=True` to refuse navigation
to private, loopback, link-local, and other reserved IP literals, including the cloud metadata
endpoint, RFC 1918 ranges, and `localhost` names. The two policies are independent: an allowlisted
private address is still refused unless private-address blocking is disabled.

The allowlist governs top-level navigation, while private-address blocking applies to every frame.
Neither policy is a general security boundary: private-address blocking matches IP literals and
`localhost` names but does not resolve hostnames, and neither policy controls requests initiated by
in-page JavaScript (`fetch`/XHR) or WebSockets. For untrusted-input scenarios, run the browser in
a container or VM with an egress firewall, or front it with a proxy. Treat these controls as
defense in depth, not a guarantee.

### Outputs

All generated files are confined to `outputs/`, including the report and local trace file
`outputs/traces.jsonl`. Absolute paths and path traversal outside that directory are rejected by the
Harness `FileSystem` capability. The trace can include model prompts, results, tool output, and page
content, so treat it as sensitive local data.

### Authentication

If your website requires authentication, you will first need to save a Playwright storage state JSON with the cookies for that website. The script reads that file and passes the parsed state to `PlaywrightBrowser(storage_state=...)`, which takes the state itself rather than a path, so the browser never has to read your filesystem.

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

Expect some browser tool results to arrive as `[Scrubbed due to 'cookie']`. Logfire redacts
attribute values matching its [default patterns](https://github.com/pydantic/logfire/blob/main/logfire/_internal/scrubbing.py#L38),
and page text hits them often: a conference agenda is full of "session", a pricing page of
"credit card". Treat the traces as page content either way, since they hold whatever the browsed
site returned.

![Logfire trace view showing the Pydantic AI agent run and Playwright browser calls](readme_logfire.png)

### Azure Application Insights configuration

If `APPLICATIONINSIGHTS_CONNECTION_STRING` is present, the example also sends traces to Azure
Application Insights. Do not commit the connection string or generated trace files.

## Resources

* [Pydantic AI Documentation](https://ai.pydantic.dev/)
* [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/)
* [Playwright for Python](https://playwright.dev/python/)
* [Microsoft Foundry models](https://learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)