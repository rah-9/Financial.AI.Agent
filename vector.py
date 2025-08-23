from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "vector_store"

def get_vector_store(persist_directory=CHROMA_DIR):
    """
    Initializes and returns a Chroma vector store with HuggingFace embeddings.
    This function will create the directory and model if they don't exist,
    or load them if they do.
    """
    # Using a popular and efficient model for sentence embeddings.
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectorstore

def store_research_response(response):
    """
    Stores the summary of a research response in the vector store.
    The metadata helps in understanding the context of the stored document later.
    """
    try:
        vectorstore = get_vector_store()
        doc = Document(
            page_content=response.summary,
            metadata={
                "topic": response.topic,
                "accuracy": response.accuracy,
                "tools_used": ", ".join(response.tools_used),
                "sources": ", ".join(response.sources)
            }
        )
        vectorstore.add_documents([doc])
        print(f"[INFO] Stored research on '{response.topic}' in vector store.")
    except Exception as e:
        print(f"[ERROR] Failed to store research in vector store: {e}")


def retrieve_similar_docs(query, k=2):
    """
    Retrieves the top 'k' most similar documents from the vector store for a given query.
    """
    try:
        vectorstore = get_vector_store()
        return vectorstore.similarity_search(query, k=k)
    except Exception as e:
        print(f"[ERROR] Failed to retrieve similar documents: {e}")
        return []
