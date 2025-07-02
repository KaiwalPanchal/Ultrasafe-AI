# build_rag_index.py
from rag_knowledge_base import RAGKnowledgeBase
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

def main():
    embeddings = OpenAIEmbeddings()  # Placeholder; actual embedding via USF API in RAGKnowledgeBase
    rag = RAGKnowledgeBase(embeddings)
    index_path = "rag_faiss_index"

    while True:
        print("\nRAG Index Builder")
        print("1. Full rebuild (from all style guides and examples)")
        print("2. Incremental update (add new/changed files)")
        print("3. Save index to disk")
        print("4. Load index from disk")
        print("5. Exit")
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            rag.build_knowledge_base()
            rag.save_index(index_path)
        elif choice == "2":
            rag.incremental_update(index_path)
        elif choice == "3":
            rag.save_index(index_path)
        elif choice == "4":
            rag.load_index(index_path)
        elif choice == "5":
            print("Exiting.")
            break
        else:
            print("Invalid selection. Please choose 1-5.")

if __name__ == "__main__":
    main()