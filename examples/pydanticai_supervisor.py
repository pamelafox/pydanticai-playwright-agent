import asyncio
import os
import random

from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

"""Multi-agent example: triage hand-off to a weather agent.

This demonstrates Pydantic AI programmatic hand-off: a triage agent determines whether the
request needs weather information, then we invoke a weather agent that can call a weather tool.
"""

# Setup the OpenAI client to use Azure OpenAI or Ollama
load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "azure")

async_credential = None
if API_HOST == "azure":
    async_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(async_credential, "https://cognitiveservices.azure.com/.default")
    client = AsyncOpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"] + "/openai/v1",
        api_key=token_provider,
    )
    model = OpenAIChatModel(os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"], provider=OpenAIProvider(openai_client=client))
elif API_HOST == "ollama":
    client = AsyncOpenAI(base_url=os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434/v1"), api_key="none")
    model = OpenAIChatModel(os.environ["OLLAMA_MODEL"], provider=OpenAIProvider(openai_client=client))
else:
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = OpenAIChatModel(os.environ.get("OPENAI_MODEL", "gpt-4o"), provider=OpenAIProvider(openai_client=client))


class Weather(BaseModel):
    city: str
    temperature: int
    wind_speed: int
    rain_chance: int


class TriageResult(BaseModel):
    reason: str


async def get_weather(ctx: RunContext[None], city: str) -> Weather:
    """Returns weather data for the given city."""
    temp = random.randint(50, 90)
    wind_speed = random.randint(5, 20)
    rain_chance = random.randint(0, 100)
    return Weather(city=city, temperature=temp, wind_speed=wind_speed, rain_chance=rain_chance)


english_weather_agent = Agent(
    model,
    tools=[get_weather],
    system_prompt=(
        "You are a weather agent. You only respond in English with weather info for the requested city. "
        "Use the 'get_weather' tool to fetch data. Keep responses concise."
    ),
)


# Triage agent decides whether the weather agent should handle the request
triage_agent = Agent(
    model,
    output_type=TriageResult,
    system_prompt=(
        "You are a triage agent. Determine whether the user's request needs weather information. "
        "Return a brief reason for your decision."
    ),
)


async def main():
    user_input = "What is the weather in San Francisco CA?"
    triage = await triage_agent.run(user_input)
    triage_output = triage.output
    print("Triage output:", triage_output)
    weather_result = await english_weather_agent.run(user_input)
    print(weather_result.output)

    if async_credential:
        await async_credential.close()


if __name__ == "__main__":
    asyncio.run(main())
