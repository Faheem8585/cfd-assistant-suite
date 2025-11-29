import os
import glob
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, WikipediaLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Comprehensive CFD knowledge sources
URLS = [
    # NASA CFD Resources
    "https://www.grc.nasa.gov/www/k-12/airplane/cfd.html",
    "https://www.grc.nasa.gov/www/k-12/airplane/turbulence.html",
    "https://www.grc.nasa.gov/www/k-12/airplane/bga.html",
    "https://www.grc.nasa.gov/www/k-12/VirtualAero/BottleRocket/airplane/nseqs.html",
    
    # CFD Online Wiki
    "https://www.cfd-online.com/Wiki/Introduction_to_CFD",
    "https://www.cfd-online.com/Wiki/Turbulence_modeling",
    "https://www.cfd-online.com/Wiki/Discretization",
    "https://www.cfd-online.com/Wiki/Numerical_methods",
    "https://www.cfd-online.com/Wiki/Mesh_generation",
    "https://www.cfd-online.com/Wiki/Post-processing",
]

# Comprehensive Wikipedia topics covering ALL aspects of CFD
WIKIPEDIA_TOPICS = [
    # Fundamental Equations & Theory
    "Computational fluid dynamics",
    "Navier-Stokes equations",
    "Reynolds-averaged Navier-Stokes equations",
    "Euler equations (fluid dynamics)",
    "Continuity equation",
    "Momentum equation",
    "Energy equation",
    "Bernoulli's principle",
    "Conservation law",
    
    # Turbulence Modeling
    "Turbulence modeling",
    "K-epsilon turbulence model",
    "K-omega turbulence model",
    "Large eddy simulation",
    "Direct numerical simulation",
    "Detached eddy simulation",
    "Spalart-Allmaras turbulence model",
    "Reynolds stress equation model",
    "Turbulence",
    "Turbulent flow",
    "Laminar flow",
    
    # Numerical Methods
    "Finite volume method",
    "Finite element method",
    "Finite difference method",
    "Spectral method",
    "Lattice Boltzmann methods",
    "Smoothed-particle hydrodynamics",
    "Vortex method",
    "Boundary element method",
    
    # Discretization & Schemes
    "Discretization",
    "Upwind scheme",
    "Central differencing scheme",
    "QUICK scheme",
    "TVD scheme",
    "MUSCL scheme",
    "Numerical diffusion",
    
    # Solver Algorithms
    "SIMPLE algorithm",
    "PISO algorithm",
    "Pressure-correction method",
    "Fractional step method",
    "Projection method",
    "Multigrid method",
    "Conjugate gradient method",
    
    # Mesh & Geometry
    "Mesh generation",
    "Structured grid",
    "Unstructured grid",
    "Adaptive mesh refinement",
    "Delaunay triangulation",
    "Computational geometry",
    
    # Boundary Conditions
    "Boundary layer",
    "No-slip condition",
    "Dirichlet boundary condition",
    "Neumann boundary condition",
    "Periodic boundary condition",
    "Wall function",
    
    # Flow Phenomena
    "Compressible flow",
    "Incompressible flow",
    "Multiphase flow",
    "Free surface",
    "Shock wave",
    "Vortex",
    "Flow separation",
    "Cavitation",
    "Heat transfer",
    "Mass transfer",
    
    # Stability & Convergence
    "Courant-Friedrichs-Lewy condition",
    "Numerical stability",
    "Convergence (numerical analysis)",
    "Iterative method",
    
    # Applications & Software
    "Wind tunnel",
    "Aerodynamics",
    "Hydrodynamics",
    "Fluid mechanics",
    "Reynolds number",
    "Mach number",
    "Dimensionless quantity",
    
    # Advanced Topics
    "Combustion",
    "Reacting flow",
    "Non-Newtonian fluid",
    "Viscoelastic fluid",
    "Magnetohydrodynamics",
    "Rarefied gas dynamics",
]

def ingest_docs():
    print("="*60)
    print("CFD GPT Knowledge Base Ingestion")
    print("="*60)
    docs = []
    
    # Load from Web with error handling
    print(f"\n📄 Loading web documentation from {len(URLS)} URLs...")
    for i, url in enumerate(URLS, 1):
        try:
            print(f"  [{i}/{len(URLS)}] Loading {url}...")
            loader = WebBaseLoader([url])
            loaded_docs = loader.load()
            docs.extend(loaded_docs)
            print(f"    ✓ Loaded {len(loaded_docs)} page(s)")
        except Exception as e:
            print(f"    ✗ Failed to load {url}: {e}")
    
    # Load Wikipedia articles
    print(f"\n📚 Loading Wikipedia articles ({len(WIKIPEDIA_TOPICS)} topics)...")
    for i, topic in enumerate(WIKIPEDIA_TOPICS, 1):
        try:
            print(f"  [{i}/{len(WIKIPEDIA_TOPICS)}] Loading '{topic}'...")
            loader = WikipediaLoader(query=topic, load_max_docs=1)
            loaded_docs = loader.load()
            docs.extend(loaded_docs)
            print(f"    ✓ Loaded {len(loaded_docs)} article(s)")
        except Exception as e:
            print(f"    ✗ Failed to load '{topic}': {e}")
    
    # Load PDFs from current directory
    print(f"\n📑 Checking for PDF files...")
    pdf_files = glob.glob("*.pdf")
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF file(s): {', '.join(pdf_files)}")
        for pdf_file in pdf_files:
            print(f"  Loading {pdf_file}...")
            try:
                pdf_loader = PyPDFLoader(pdf_file)
                loaded_docs = pdf_loader.load()
                docs.extend(loaded_docs)
                print(f"    ✓ Loaded {len(loaded_docs)} page(s)")
            except Exception as e:
                print(f"    ✗ Failed to load {pdf_file}: {e}")
    else:
        print("  No PDF files found in current directory.")
    
    print(f"\n📊 Total documents loaded: {len(docs)}")
    
    # Split documents
    print(f"\n✂️  Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    print(f"   Split into {len(splits)} chunks.")

    # Create Vector Store
    print(f"\n🗄️  Creating vector store...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )
    print("="*60)
    print("✅ Ingestion complete! Vector store saved to ./chroma_db")
    print(f"   Total chunks in database: {len(splits)}")
    print("="*60)

if __name__ == "__main__":
    ingest_docs()
