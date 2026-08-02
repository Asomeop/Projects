import os
import warnings
from dotenv import load_dotenv

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

CHROMA_PATH = "chroma_db"

def get_retriever():
    """
    Connects to the local ChromaDB and returns a retriever configured to fetch the top 3 most relevant text chunks for a query.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Connect to the saved vector store folder
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    return retriever

def query_rag(user_query: str):
    """
    Retrieves context chunks from ChromaDB and sends them to Gemini to generate a grounded answer with page citations.
    """
    retriever = get_retriever()
    
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise.\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Initialize Google Gemini 2.5 Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    response = rag_chain.invoke({"input": user_query})
    
    # Extract source citations from metadata
    citations = [
        {
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", 0) + 1  # 0-indexed to 1-indexed
        }
        for doc in response["context"]
    ]
    
    return {
        "answer": response["answer"],
        "citations": citations
    }




if __name__ == "__main__":
    if os.path.exists(CHROMA_PATH):
        # Feel free to change this question to test your PDF!
        question = "What is the main topic of this document?"
        
        print(f"🔍 Querying ChromaDB and asking Gemini: '{question}'...\n")
        result = query_rag(question)
        
        print("--- 🤖 Gemini's Answer ---")
        print(result["answer"])
        
        print("\n--- 📖 Citations ---")
        for citation in result["citations"]:
            print(f"- Source: {citation['source']} | Page: {citation['page']}")
    else:
        print(f"❌ '{CHROMA_PATH}' folder not found! Make sure to run chromaDB.py first.")