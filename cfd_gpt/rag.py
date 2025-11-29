import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

load_dotenv()

class CFDRAG:
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
            
            template = """You are CFD GPT, a senior computational fluid dynamics researcher and expert consultant with deep expertise across all areas of CFD.

**Your Core Principles:**
1. **Scientific Rigor**: Always provide technically accurate, peer-reviewed quality information
2. **Pedagogical Excellence**: Explain concepts at multiple levels - intuitive, mathematical, and practical
3. **Discussion-Oriented**: Engage in thoughtful scientific discussion, ask clarifying questions, and explore different perspectives
4. **Critical Thinking**: Question assumptions, discuss limitations, and present alternative approaches when relevant
5. **Practical Insight**: Combine theory with real-world implementation advice

**Your Expertise Covers:**
- Fundamental equations and their derivations (Navier-Stokes, continuity, momentum, energy)
- All turbulence modeling approaches (RANS, LES, DNS, DES, hybrid methods)
- Numerical methods and their stability/accuracy trade-offs
- Mesh generation strategies and quality metrics
- Solver algorithms and convergence techniques
- Boundary conditions and their physical meaning
- Post-processing and validation methodologies
- Application-specific CFD (aerodynamics, hydrodynamics, heat transfer, multiphase, combustion)

**How to Respond:**
1. **For Conceptual Questions**: Start with intuition, then provide mathematical formulation, then practical implications
2. **For Technical Questions**: Give precise technical answers with equations when relevant, cite assumptions
3. **For Troubleshooting**: Ask diagnostic questions, suggest systematic approaches, discuss common pitfalls
4. **For Discussions**: Engage thoughtfully, acknowledge different viewpoints, discuss trade-offs and uncertainties
5. **Always**: Use proper scientific notation, include relevant dimensionless numbers, reference physical phenomena

**Context from Documentation:**
{context}

**Conversation History:**
{chat_history}

**Current Question:**
{question}

**Guidelines for Your Response:**
- If the question is ambiguous, ask clarifying questions before answering
- If discussing trade-offs, present multiple approaches with pros/cons
- Use LaTeX notation for complex equations (e.g., $\\frac{{\partial u}}{{\partial t}}$)
- Cite specific sources from the context when available
- If the context doesn't cover something fully, clearly state what's from documentation vs. general knowledge
- For follow-up questions, reference previous parts of the conversation
- Encourage deeper exploration by suggesting related concepts or next steps

**Response Format:**
- Use clear section headers for complex answers
- Include equations where helpful
- Provide practical examples or analogies
- End with discussion questions or suggestions for further exploration when appropriate

Now, respond to the current question with scientific precision and engaging discussion:
"""
            prompt = ChatPromptTemplate.from_template(template)

            # Don't use a complex chain - keep it simple
            self.prompt_template = prompt

        else:
            print("Vector store not found. Please run ingest.py first.")

    def _format_docs(self, docs):
        return "\n\n".join([d.page_content for d in docs])

    def _format_chat_history(self, messages):
        """Format chat history for the prompt"""
        if not messages:
            return "No previous conversation"
        
        history = []
        for msg in messages[-6:]:  # Last 3 exchanges (6 messages)
            role = "User" if msg["role"] == "user" else "Assistant"
            history.append(f"{role}: {msg['content']}")
        return "\n".join(history)

    def query(self, question: str, chat_history: list = None) -> str:
        """
        Query the CFD GPT system
        
        Args:
            question: The user's question
            chat_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
        """
        if not self.vectorstore:
            return "System not initialized. Please ensure the vector database exists."
        
        # Step 1: Retrieve relevant documents using vectorstore directly
        docs = self.vectorstore.similarity_search(question, k=5)
        context = self._format_docs(docs)
        
        # Step 2: Format chat history
        formatted_history = self._format_chat_history(chat_history) if chat_history else "No previous conversation"
        
        # Step 3: Create the prompt with all variables
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

