"""Step 5: create the Groq chat LLM."""

from langchain_groq import ChatGroq

from hr_assistant import config
from hr_assistant.logger import get_logger

logger = get_logger(__name__)


def get_llm():
    """Return a ChatGroq model using the configured name and temperature."""
    logger.info(
        "Initializing LLM '%s' via Groq (temperature=%s)",
        config.LLM_MODEL_NAME,
        config.LLM_TEMPERATURE,
    )
    return ChatGroq(
        model=config.LLM_MODEL_NAME,
        temperature=config.LLM_TEMPERATURE,
    )
