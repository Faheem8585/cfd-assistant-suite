import os
import glob
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Comprehensive OpenFOAM documentation URLs
URLS = [
    # User Guide
    "https://www.openfoam.com/documentation/user-guide",
    "https://www.openfoam.com/documentation/user-guide/1-introduction",
    "https://www.openfoam.com/documentation/user-guide/2-openfoam-cases",
    "https://www.openfoam.com/documentation/user-guide/2-running-applications/2.1-running-openfoam",
    "https://www.openfoam.com/documentation/user-guide/3-running-applications",
    "https://www.openfoam.com/documentation/user-guide/4-mesh-generation-and-conversion",
    "https://www.openfoam.com/documentation/user-guide/5-pre-processing",
    "https://www.openfoam.com/documentation/user-guide/6-solving",
    "https://www.openfoam.com/documentation/user-guide/7-post-processing",
    "https://www.openfoam.com/documentation/user-guide/8-basic-file-format",
    
    # Tutorials
    "https://www.openfoam.com/documentation/tutorial-guide",
    "https://www.openfoam.com/documentation/tutorial-guide/2-incompressible-flow",
    "https://www.openfoam.com/documentation/tutorial-guide/3-compressible-flow",
    "https://www.openfoam.com/documentation/tutorial-guide/4-multiphase-flow",
    
    # Programming Guide (if accessible)
    "https://www.openfoam.com/documentation/cpp-guide",
]

def ingest_docs():
    print("Loading documentation...")
    docs = []
    
    # Load from Web with error handling
    print(f"Loading web documentation from {len(URLS)} URLs...")
    for i, url in enumerate(URLS, 1):
        try:
            print(f"  [{i}/{len(URLS)}] Loading {url}...")
            loader = WebBaseLoader([url])
            loaded_docs = loader.load()
            docs.extend(loaded_docs)
            print(f"    ✓ Loaded {len(loaded_docs)} page(s)")
        except Exception as e:
            print(f"    ✗ Failed to load {url}: {e}")
    
    # Load PDFs from current directory
    pdf_files = glob.glob("*.pdf")
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF file(s): {', '.join(pdf_files)}")
        for pdf_file in pdf_files:
            print(f"Loading {pdf_file}...")
            pdf_loader = PyPDFLoader(pdf_file)
            docs.extend(pdf_loader.load())
    else:
        print("No PDF files found in current directory.")
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    print(f"Split into {len(splits)} chunks.")

    # Create Vector Store
    print("Creating vector store...")
    # Use a standard, small, efficient model for embeddings
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )
    print("Ingestion complete. Vector store saved to ./chroma_db")

if __name__ == "__main__":
    ingest_docs()
