# Description: This script connects to the ChromaDB database and prints out all the episodic and semantic memories.
# Usage: python verify_memory.py

import chromadb
from pprint import pprint

def verify_memory():
    """Connects to ChromaDB and prints the contents of the memory collections."""
    
    db_path = "./data/chroma_db"
    
    print(f"Connecting to ChromaDB at: {db_path}\n")
    
    try:
        client = chromadb.PersistentClient(path=db_path)
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        return

    # --- Verify Episodic Memory ---
    print("="*25)
    print("  Episodic Memory (Conversations)")
    print("="*25 + "\n")
    
    try:
        episodic_collection = client.get_collection("episodic_memory")
        episodic_data = episodic_collection.get(include=["metadatas", "documents"])
        
        if not episodic_data or not episodic_data['ids']:
            print("No episodic memories found.")
        else:
            for i, doc in enumerate(episodic_data['documents']):
                cleaned_doc = doc.replace('\n', ' \\n ')
                print(f"- Memory ID: {episodic_data['ids'][i]}")
                print(f"  Content: {cleaned_doc}")
                print("  Metadata:")
                pprint(episodic_data['metadatas'][i], indent=4)
                print("---")
            print(f"\nTotal episodic memories: {len(episodic_data['ids'])}")
            
    except Exception as e:
        print(f"Could not retrieve episodic memory. It might be empty. Error: {e}")

    # --- Verify Semantic Memory ---
    print("\n" + "="*25)
    print("  Semantic Memory (Facts)")
    print("="*25 + "\n")
    
    try:
        semantic_collection = client.get_collection("semantic_memory")
        semantic_data = semantic_collection.get(include=["metadatas", "documents"])
        
        if not semantic_data or not semantic_data['ids']:
            print("No semantic memories found.")
        else:
            for i, doc in enumerate(semantic_data['documents']):
                print(f"- Memory ID: {semantic_data['ids'][i]}")
                print(f"  Content: {doc}")
                print("  Metadata:")
                pprint(semantic_data['metadatas'][i], indent=4)
                print("---")
            print(f"\nTotal semantic memories: {len(semantic_data['ids'])}")
            
    except Exception as e:
        print(f"Could not retrieve semantic memory. It might be empty. Error: {e}")

if __name__ == "__main__":
    verify_memory()
