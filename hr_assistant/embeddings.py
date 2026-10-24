"""Step 3: create the Jina embeddings model."""

from langchain_community.embeddings import JinaEmbeddings

from hr_assistant import config


def get_embeddings_model():
    """Return a Jina embeddings model using the configured model name."""
    return JinaEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
