from langchain_chroma import Chroma
from langchain_community.embeddings import JinaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import config

embeddings = JinaEmbeddings(model_name=config.EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=config.CHROMA_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})

prompt = ChatPromptTemplate.from_template("""
You are a company policy assistant.

Answer the question using only the provided context.

If the answer is not present in the context,
say: "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:
""")

llm = ChatGroq(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)


def ask_question(question):
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    messages = prompt.invoke({"context": context, "question": question})
    return llm.invoke(messages).content


if __name__ == "__main__":
    print(ask_question("How many casual leaves can an employee take?"))