"""
chains.py
---------
Everything related to talking to the LLM lives here:

- build_llm()               : creates the ChatOpenAI client. Accepts an
                               optional api_key so a user-typed key (from the
                               sidebar) can override the .env key.
- demo_message_roles()      : standalone demo of SystemMessage / HumanMessage
                               / AIMessage.
- build_analysis_chain()    : the reusable LLMChain that produces JSON.
- stream_recommendations()  : generator that streams the human-readable
                               recommendation text for st.write_stream.
"""

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src import config
from src.prompts import (
    ANALYSIS_PROMPT_TEMPLATE,
    NARRATIVE_CHAT_TEMPLATE,
    SYSTEM_PROMPT,
)


def build_llm(streaming: bool = False, api_key: str = None) -> ChatOpenAI:
    """Create a ChatOpenAI instance.

    `api_key`: if provided (e.g. typed by the user into the sidebar), it
    overrides the key loaded from .env. This lets someone run the app with
    their own OpenAI key without ever editing the .env file.
    """
    return ChatOpenAI(
        model=config.MODEL_NAME,
        temperature=config.MODEL_TEMPERATURE,
        api_key=api_key or config.OPENAI_API_KEY,
        streaming=streaming,
    )


def demo_message_roles(user_question: str, api_key: str = None) -> list:
    """A tiny standalone demo of SystemMessage / HumanMessage / AIMessage.

    Mirrors a real chat turn: system sets the rules, human asks a question,
    and the reply is wrapped in an AIMessage so it could be appended back
    into a longer conversation.
    """
    llm = build_llm(streaming=False, api_key=api_key)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_question),
    ]

    response = llm.invoke(messages)
    ai_turn = AIMessage(content=response.content)
    messages.append(ai_turn)

    return messages  # [SystemMessage, HumanMessage, AIMessage]


def build_analysis_chain(api_key: str = None) -> LLMChain:
    """Build the reusable LLMChain that turns financial inputs into raw JSON text."""
    llm = build_llm(streaming=False, api_key=api_key)
    return LLMChain(llm=llm, prompt=ANALYSIS_PROMPT_TEMPLATE)


def stream_recommendations(inputs: dict, api_key: str = None):
    """Generator: yields recommendation text chunks as they arrive from the model.

    Intended for st.write_stream(stream_recommendations(...)) so the user
    sees a live typing effect instead of waiting for the full response.
    """
    llm = build_llm(streaming=True, api_key=api_key)
    messages = NARRATIVE_CHAT_TEMPLATE.format_messages(**inputs)

    for chunk in llm.stream(messages):
        if chunk.content:
            yield chunk.content
