import os
import sys
import streamlit as st
from dotenv import load_dotenv
import json
from datetime import datetime
import importlib.util

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CFD Assistant Suite - AI for Computational Fluid Dynamics",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e88e5 0%, #c8102e 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        margin: 0;
    }
    
    .mode-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .mode-cfd {
        background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
        color: white;
    }
    
    .mode-openfoam {
        background: linear-gradient(135deg, #c8102e 0%, #ff6b6b 100%);
        color: white;
    }
    
    .feature-list {
        list-style: none;
        padding: 0;
    }
    
    .feature-list li {
        padding: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
    }
    
    .feature-list li:before {
        content: "✓";
        position: absolute;
        left: 0;
        font-weight: bold;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stChatMessage {
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def export_chat_history():
    """Export chat history as JSON"""
    if "messages" in st.session_state and st.session_state.messages:
        export_data = {
            "mode": st.session_state.get("mode", "CFD"),
            "exported_at": datetime.now().isoformat(),
            "messages": st.session_state.messages
        }
        return json.dumps(export_data, indent=2)
    return None

def main():
    # Initialize session state
    if "mode" not in st.session_state:
        st.session_state.mode = "CFD"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌊 CFD Assistant Suite</h1>
        <p>Unified AI Assistant for Computational Fluid Dynamics & OpenFOAM</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Mode Selection")
        
        # Mode selector
        mode = st.radio(
            "Choose Assistant",
            ["CFD GPT", "OpenFOAM GPT"],
            index=0 if st.session_state.mode == "CFD" else 1,
            help="Switch between general CFD and OpenFOAM-specific assistance"
        )
        
        # Update mode and clear chat if changed
        new_mode = "CFD" if mode == "CFD GPT" else "OpenFOAM"
        if new_mode != st.session_state.mode:
            st.session_state.mode = new_mode
            st.session_state.messages = []
            st.rerun()
        
        # Display current mode badge
        badge_class = "mode-cfd" if st.session_state.mode == "CFD" else "mode-openfoam"
        icon = "🌊" if st.session_state.mode == "CFD" else "⚙️"
        st.markdown(f'<div class="mode-badge {badge_class}">{icon} {mode} Active</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Mode-specific capabilities
        st.markdown("### 🎯 Capabilities")
        
        if st.session_state.mode == "CFD":
            st.markdown("""
            <ul class="feature-list">
                <li>Fundamental CFD concepts</li>
                <li>Turbulence modeling (RANS, LES, DNS)</li>
                <li>Numerical methods & discretization</li>
                <li>Mesh generation strategies</li>
                <li>Solver algorithms</li>
                <li>Post-processing techniques</li>
                <li>Scientific equations & theory</li>
            </ul>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <ul class="feature-list">
                <li>Case setup & directory structure</li>
                <li>Solver selection & configuration</li>
                <li>Dictionary files (controlDict, fvSchemes)</li>
                <li>Mesh generation (blockMesh, snappyHexMesh)</li>
                <li>Boundary conditions</li>
                <li>Turbulence model setup</li>
                <li>Troubleshooting & debugging</li>
            </ul>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Knowledge base status
        st.markdown("### 📊 Status")
        
        db_path = "./cfd_gpt/chroma_db" if st.session_state.mode == "CFD" else "./openfoam_gpt/chroma_db"
        
        if os.path.exists(db_path):
            st.success(f"✓ {mode} Knowledge Loaded")
            try:
                import chromadb
                client = chromadb.PersistentClient(path=db_path)
                collections = client.list_collections()
                if collections:
                    count = collections[0].count()
                    st.info(f"📚 {count} chunks")
            except:
                pass
        else:
            st.warning(f"⚠ {mode} DB not found")
        
        st.markdown("---")
        
        # File upload
        st.markdown("### 📤 Upload Documents")
        st.caption("Expand knowledge base")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "tiff", "bmp"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            if st.button("🚀 Process Files", use_container_width=True):
                # Import the correct processor based on mode using importlib
                import importlib.util
                
                processor_path = f"./{st.session_state.mode.lower()}_gpt/document_processor.py"
                spec = importlib.util.spec_from_file_location("doc_processor", processor_path)
                doc_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(doc_module)
                
                processor = doc_module.DocumentProcessor(persist_directory=db_path)
                
                with st.spinner("Processing..."):
                    total_chunks = 0
                    progress_bar = st.progress(0)
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        st.caption(f"Processing {uploaded_file.name}...")
                        
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                        
                        try:
                            file_type = uploaded_file.name.split('.')[-1].lower()
                            chunks = processor.process_and_ingest(tmp_path, file_type)
                            total_chunks += chunks
                            st.success(f"✓ {uploaded_file.name}: {chunks} chunks")
                        except Exception as e:
                            st.error(f"✗ {uploaded_file.name}: {str(e)}")
                        finally:
                            os.unlink(tmp_path)
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    st.balloons()
                    st.success(f"🎉 Added {total_chunks} chunks!")
        
        st.markdown("---")
        
        # Chat controls
        st.markdown("### 🛠️ Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            chat_json = export_chat_history()
            if chat_json:
                st.download_button(
                    label="💾 Export",
                    data=chat_json,
                    file_name=f"cfd_suite_{st.session_state.mode.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        st.markdown("---")
        st.caption("CFD Assistant Suite v1.0")

    # Initialize appropriate RAG pipeline using importlib
    import importlib.util
    
    if st.session_state.mode == "CFD":
        # Load CFD RAG module
        spec = importlib.util.spec_from_file_location("cfd_rag", "./cfd_gpt/rag.py")
        cfd_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfd_module)
        rag = cfd_module.CFDRAG(persist_directory="./cfd_gpt/chroma_db")
        placeholder_text = "🤔 Ask me anything about CFD..."
    else:
        # Load OpenFOAM RAG module
        spec = importlib.util.spec_from_file_location("openfoam_rag", "./openfoam_gpt/rag.py")
        openfoam_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openfoam_module)
        rag = openfoam_module.OpenFOAMRAG(persist_directory="./openfoam_gpt/chroma_db")
        placeholder_text = "🤔 Ask about OpenFOAM setup, solvers, or configuration..."

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(placeholder_text):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                full_response = rag.query(prompt, chat_history=st.session_state.messages[:-1])
            st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
