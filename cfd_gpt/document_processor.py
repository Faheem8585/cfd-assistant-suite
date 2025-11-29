import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PIL import Image
import pytesseract

class DocumentProcessor:
    """Process and ingest various document types into the vector database"""
    
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF files"""
        loader = PyPDFLoader(file_path)
        return loader.load()
    
    def process_docx(self, file_path: str) -> List[Document]:
        """Process Word documents"""
        loader = Docx2txtLoader(file_path)
        return loader.load()
    
    def process_image(self, file_path: str) -> List[Document]:
        """Process images using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            # Create a Document object
            doc = Document(
                page_content=text,
                metadata={"source": file_path, "type": "image_ocr"}
            )
            return [doc]
        except Exception as e:
            print(f"Error processing image {file_path}: {e}")
            return []
    
    def process_file(self, file_path: str, file_type: str) -> List[Document]:
        """Process a file based on its type"""
        if file_type == "pdf":
            return self.process_pdf(file_path)
        elif file_type in ["docx", "doc"]:
            return self.process_docx(file_path)
        elif file_type in ["png", "jpg", "jpeg", "tiff", "bmp"]:
            return self.process_image(file_path)
        else:
            return []
    
    def add_documents_to_db(self, documents: List[Document]):
        """Add processed documents to the vector database"""
        if not documents:
            return 0
        
        # Split documents into chunks
        splits = self.text_splitter.split_documents(documents)
        
        # Load existing vectorstore or create new one
        if os.path.exists(self.persist_directory):
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function
            )
            vectorstore.add_documents(splits)
        else:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory
            )
        
        return len(splits)
    
    def process_and_ingest(self, file_path: str, file_type: str) -> int:
        """Process a file and add it to the database"""
        docs = self.process_file(file_path, file_type)
        return self.add_documents_to_db(docs)
