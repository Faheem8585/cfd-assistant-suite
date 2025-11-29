# File Upload Feature Guide

## Overview
Both **CFD GPT** and **OpenFOAM GPT** now support uploading documents directly through the web interface!

## Supported File Types

### 📄 **PDF Files**
- Research papers
- Textbooks
- Technical documentation
- User manuals

### 📝 **Word Documents**
- `.docx` files
- `.doc` files (older format)
- Technical notes
- Reports

### 🖼️ **Images (with OCR)**
- `.png`, `.jpg`, `.jpeg`
- `.tiff`, `.bmp`
- **OCR extracts text from images**
- Perfect for:
  - Scanned documents
  - Screenshots
  - Diagrams with text
  - Handwritten notes (if clear)

## How to Use

### 1. **Navigate to Sidebar**
Look for the "📤 Upload Documents" section in the left sidebar

### 2. **Choose Files**
Click "Browse files" and select one or more documents

### 3. **Process Files**
Click "Process Uploaded Files" button

### 4. **Wait for Processing**
- Progress bar shows status
- Each file shows success ✓ or error ✗
- Total chunks added displayed

### 5. **Restart App** (Important!)
After uploading, you need to restart the Streamlit app to load the new knowledge:
- Press `Ctrl+C` in the terminal
- Run `streamlit run main.py` again
- Or just refresh the browser (Streamlit will auto-reload)

## Processing Details

### What Happens Behind the Scenes:
1. **File Upload**: Temporary file created
2. **Text Extraction**:
   - PDFs: Direct text extraction
   - DOCX: Document structure parsing
   - Images: OCR with Tesseract
3. **Chunking**: Split into 1000-character chunks with 200 overlap
4. **Embedding**: Convert to vectors using HuggingFace model
5. **Storage**: Add to ChromaDB vector database

### Chunk Size Examples:
- A typical PDF page: ~3-5 chunks
- A research paper (10 pages): ~30-50 chunks
- A textbook chapter (20 pages): ~60-100 chunks

## OCR Requirements

For image processing, Tesseract OCR must be installed:

### macOS:
```bash
brew install tesseract
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get install tesseract-ocr
```

### Windows:
Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Best Practices

### ✅ **Do:**
- Upload high-quality PDFs (not scanned)
- Use clear, high-resolution images for OCR
- Upload related documents together
- Check success messages

### ❌ **Avoid:**
- Very large files (>50MB) - may timeout
- Poor quality scans
- Password-protected PDFs
- Corrupted files

## Example Use Cases

### CFD GPT:
- Upload Anderson's "Computational Fluid Dynamics" textbook
- Add research papers on turbulence modeling
- Include conference proceedings
- Upload lecture notes with equations (as images)

### OpenFOAM GPT:
- Upload OpenFOAM User Guide PDF
- Add custom case setup documentation
- Include solver implementation papers
- Upload screenshots of dictionary configurations

## Troubleshooting

### "No text extracted"
- PDF might be scanned (use OCR software first)
- Image quality too low
- File corrupted

### "Processing failed"
- File too large
- Unsupported format variant
- Memory issue (try smaller batches)

### "Tesseract not found" (Images only)
- Install Tesseract OCR
- Add to system PATH
- Restart terminal/app

## Performance Notes

- **PDFs**: Fast (seconds per document)
- **DOCX**: Fast (seconds)
- **Images**: Slower (OCR takes 5-30s per image)
- **Batch uploads**: Process sequentially

## Privacy & Data

- Files processed locally
- Not sent to external servers
- Stored only in local ChromaDB
- Temporary files deleted after processing
