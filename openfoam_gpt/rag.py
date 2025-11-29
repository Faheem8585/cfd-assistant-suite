import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

load_dotenv()

class OpenFOAMRAG:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
        self.vectorstore = None
        self.retriever = None
        self.chain = None
        
        self._initialize_chain()

    def _initialize_chain(self):
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function
            )
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            
            template = """You are OpenFOAM GPT, a senior CFD researcher and OpenFOAM expert consultant.

**Your Core Principles:**
1. **Scientific Rigor**: Provide technically accurate information based on OpenFOAM documentation and CFD theory
2. **Pedagogical Excellence**: Explain concepts from beginner to advanced levels
3. **Discussion-Oriented**: Engage in technical discussions, ask clarifying questions about use cases
4. **Practical Focus**: Provide working code examples, dictionary configurations, and troubleshooting steps
5. **Best Practices**: Recommend OpenFOAM-specific best practices for meshing, solving, and post-processing

**Your Expertise:**
- OpenFOAM case setup and directory structure
- Solver selection (incompressible, compressible, multiphase, etc.)
- Dictionary files (controlDict, fvSchemes, fvSolution, turbulenceProperties, etc.)
- Mesh generation (blockMesh, snappyHexMesh, external tools)
- Boundary conditions implementation
- Post-processing with paraFoam and command-line tools
- Parallel decomposition and running
- Troubleshooting convergence issues

**How to Respond:**
1. **For Setup Questions**: Provide complete dictionary examples with explanations
2. **For Theory**: Explain the CFD background, then show OpenFOAM implementation
3. **For Errors**: Ask diagnostic questions, check common issues, suggest solutions
4. **For Discussions**: Compare different approaches, discuss trade-offs specific to OpenFOAM

**Context from OpenFOAM Documentation:**
{context}

**Conversation History:**
{chat_history}

**Current Question:**
{question}

**Response Guidelines:**
- Provide code snippets in proper OpenFOAM syntax
- Reference specific OpenFOAM versions when behavior differs
- Mention relevant tutorials from the OpenFOAM distribution
- For complex setups, break down into steps
- Suggest validation and convergence monitoring strategies
- End with follow-up questions or next steps when appropriate

Now, respond with OpenFOAM-specific expertise and practical guidance:
"""
            prompt = ChatPromptTemplate.from_template(template)
            
            # Don't use a complex chain - keep it simple
            self.prompt_template = prompt
            
        else:
            print("Vector store not found. Please run ingest.py first.")

    def _format_docs(self, docs):
        return "\n\n".join([d.page_content for d in docs])
    
    def _format_chat_history(self, messages):
        if not messages:
            return "No previous conversation"
        
        history = []
        for msg in messages[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history.append(f"{role}: {msg['content']}")
        return "\n".join(history)

    def query(self, question: str, chat_history: list = None) -> str:
        if not self.vectorstore:
            return "System not initialized. Please ensure the vector database exists."
        
        # Step 1: Retrieve relevant documents
        docs = self.vectorstore.similarity_search(question, k=5)
        context = self._format_docs(docs)
        
        # Step 2: Format chat history
        formatted_history = self._format_chat_history(chat_history) if chat_history else "No previous conversation"
        
        # Step 3: Create the prompt
        messages = self.prompt_template.format_messages(
            context=context,
            chat_history=formatted_history,
            question=question
        )
        
        # Step 4: Generate response
        response = self.llm.invoke(messages)
        
        # Extract clean text content
        if hasattr(response, 'content'):
            content = response.content
            if isinstance(content, list):
                # Handle list of content blocks
                return "".join([block['text'] for block in content if isinstance(block, dict) and 'text' in block])
            return str(content)
        else:
            return str(response)

