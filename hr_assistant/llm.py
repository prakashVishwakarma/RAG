"""Step 5: create the Groq chat LLM."""

from langchain_groq import ChatGroq

from hr_assistant import config


def get_llm():
    """Return a ChatGroq model using the configured name and temperature."""
    return ChatGroq(
        model=config.LLM_MODEL_NAME,
        temperature=config.LLM_TEMPERATURE,
    )
