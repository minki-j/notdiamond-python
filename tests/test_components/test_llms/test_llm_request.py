import pytest
from langchain_core.messages import AIMessage

from notdiamond import Metric, NotDiamond
from notdiamond.llms.config import LLMConfig
from notdiamond.llms.providers import NDLLMProviders


def test_llm_invoke_with_latency_tracking_success():
    metric = Metric("accuracy")
    openai = NDLLMProviders.GPT_3_5_TURBO
    llm_configs = [openai]

    llm = NotDiamond(llm_configs=llm_configs, latency_tracking=True)

    llm_result, session_id, _ = llm.invoke(
        messages=[{"role": "user", "content": "Prompt: Tell me a joke."}],
        metric=metric,
    )

    assert session_id
    assert llm_result


def test_custom_model_attributes():
    metric = Metric("accuracy")
    llm_configs = [
        LLMConfig(
            provider="openai",
            model="gpt-4",
            latency=10,
            input_price=0.0,
            output_price=0.0,
        ),
        LLMConfig(
            provider="togetherai",
            model="Meta-Llama-3.1-8B-Instruct-Turbo",
            latency=0,
            input_price=10.0,
            output_price=10.0,
        ),
    ]

    client = NotDiamond(llm_configs=llm_configs)

    llm_result, session_id, _ = client.invoke(
        messages=[{"role": "user", "content": "hello"}],
        metric=metric,
        tradeoff="cost",
    )

    assert session_id
    assert llm_result.provider == "openai"
    assert llm_result.model == "gpt-4"

    llm_result, session_id, _ = client.invoke(
        messages=[{"role": "user", "content": "hello"}],
        metric=metric,
        tradeoff="latency",
    )

    assert session_id
    assert llm_result.provider == "togetherai"
    assert llm_result.model == "Meta-Llama-3.1-8B-Instruct-Turbo"


def test_session_linking():
    metric = Metric("accuracy")
    llm_configs = [
        LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
        ),
    ]

    client = NotDiamond(llm_configs=llm_configs)

    llm_result, session_id, _ = client.invoke(
        messages=[{"role": "user", "content": "hello"}],
        metric=metric,
    )

    assert session_id
    assert llm_result

    llm_result, new_session_id, _ = client.invoke(
        messages=[{"role": "user", "content": "hello"}],
        metric=metric,
        previous_session=session_id,
    )

    assert new_session_id
    assert llm_result


@pytest.mark.asyncio
async def test_async_llm_invoke_with_latency_tracking_success():
    metric = Metric("accuracy")
    openai = NDLLMProviders.GPT_3_5_TURBO
    llm_configs = [openai]

    llm = NotDiamond(llm_configs=llm_configs, latency_tracking=True)

    llm_result, session_id, _ = await llm.ainvoke(
        messages=[{"role": "user", "content": "Prompt: Tell me a joke."}],
        metric=metric,
    )

    assert session_id
    assert llm_result


def test_llm_invoke_with_latency_tracking_nd_chat_prompt_success():
    metric = Metric("accuracy")
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI bot. Your name is Bob.",
        },
        {"role": "user", "content": "Hello, how are you doing?"},
        {"role": "assistant", "content": "I'm doing well, thanks!"},
        {"role": "user", "content": "What is your name?"},
    ]

    nd_llm = NotDiamond(
        llm_configs=["openai/gpt-3.5-turbo"], hash_content=True
    )
    result, session_id, _ = nd_llm.invoke(
        messages=messages,
        metric=metric,
    )

    print(session_id)
    assert len(session_id) == 36
    assert len(session_id.split("-")) == 5
    assert type(result) is AIMessage
    assert "Bob" in result.content
