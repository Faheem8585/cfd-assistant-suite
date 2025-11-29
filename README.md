# CFD Assistant Suite 🌊⚙️

## Overview

This is my personal project designed to bridge the gap between complex Computational Fluid Dynamics (CFD) theory and practical OpenFOAM implementation. As a CFD engineer, I often found myself switching between textbooks for theory and documentation for syntax. I built this unified assistant to have both at my fingertips.

The suite combines two specialized assistants into a single interface:
1.  **CFD GPT**: Focuses on the physics, mathematics, and fundamental theory of fluid dynamics.
2.  **OpenFOAM GPT**: Specializes in the practicalities of running simulations, configuring dictionaries, and troubleshooting OpenFOAM cases.

## 🛠️ How It Works (The Workflow)

I designed this application using a Retrieval-Augmented Generation (RAG) architecture to ensuring the AI's responses are grounded in verified technical documentation rather than just training data.

### 1. Data Ingestion Pipeline
The first step was building a robust knowledge base. I wrote custom ingestion scripts (`ingest.py`) that:
-   **Scrape & Parse**: Extract text from reliable online sources (like NASA's CFD guides and OpenFOAM documentation) and local PDF textbooks.
-   **Chunking**: The text is split into manageable chunks (approx. 1000 characters) to ensure precise retrieval.
-   **Embedding**: I used the `all-MiniLM-L6-v2` model from HuggingFace to convert these text chunks into vector embeddings.
-   **Storage**: These vectors are stored locally in a **ChromaDB** vector database, allowing for fast semantic search.

### 2. The RAG Engine
When you ask a question, the system doesn't just guess. Here is the logic I implemented in `rag.py`:
1.  **Retrieval**: The system searches the ChromaDB for the 5 most relevant chunks of text related to your query.
2.  **Context Construction**: It combines these chunks into a "context" block.
3.  **Prompt Engineering**: I designed a specialized system prompt that instructs the LLM to act as a senior researcher. It forces the model to answer *using* the retrieved context, ensuring accuracy.
4.  **Generation**: The context and your question are sent to the LLM (Google Gemini), which synthesizes the final answer.

### 3. The Unified Interface
I built the frontend using **Streamlit** to create a clean, modern web interface.
-   **Mode Switching**: I implemented a state-management system that lets you toggle between "CFD Mode" and "OpenFOAM Mode" instantly. This swaps the underlying vector database and system prompts on the fly.
-   **Document Upload**: I added a feature to upload your own PDFs or Word docs. The app processes them in real-time, OCRs images if needed, and adds them to the knowledge base immediately.

## ✨ Key Features

-   **Scientific Rigor**: The system is tuned to output proper LaTeX equations ($Re = \frac{\rho u L}{\mu}$) and structured technical data.
-   **Context Awareness**: It remembers the last few exchanges of our conversation, allowing for follow-up questions.
-   **Dual Knowledge Bases**: Keeps theoretical knowledge separate from software syntax to prevent hallucination.

## 🚀 Installation & Usage

### Prerequisites
-   Python 3.11+
-   Tesseract OCR (optional, for image processing)

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/cfd-assistant-suite.git
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your API key in a `.env` file:
    ```env
    GOOGLE_API_KEY=your_key_here
    ```

### Running the App
```bash
streamlit run unified_cfd_assistant.py
```

## 📁 Project Structure

-   `unified_cfd_assistant.py`: The main entry point and UI logic.
-   `cfd_gpt/`: Contains the logic for the general CFD assistant.
    -   `rag.py`: The RAG pipeline implementation.
    -   `ingest.py`: Scripts for building the knowledge base.
-   `openfoam_gpt/`: Contains the logic for the OpenFOAM assistant.

## 🤝 Future Improvements

I plan to add:
-   Automated case file generation (writing `controlDict` directly to disk).
-   Support for more CFD solvers (ANSYS Fluent, SU2).
-   Plotting capabilities for residual monitoring.

---
*Created by [Muhammad Faheem Arshad]*
