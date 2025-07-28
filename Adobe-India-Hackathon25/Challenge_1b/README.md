# Challenge 1B - Persona-Driven Document Intelligence

## Overview
This solution implements a persona-driven document analysis system that extracts and ranks relevant sections from PDF collections based on user persona and job requirements.

## Architecture
- *PersonaAnalyzer*: Analyzes persona and job descriptions to create semantic vectors
- *ChunkEmbedder*: Creates embeddings for document sections using sentence transformers
- *SectionRanker*: Ranks sections and extracts subsections based on relevance
- *PDFProcessor*: Extracts structured content from PDFs

## Key Features
- Semantic similarity matching using MiniLM embeddings
- Multi-factor ranking (semantic, keyword, position, length, title relevance)
- Adaptive chunking with sentence-aware splitting
- Persona-specific keyword weighting
- Subsection extraction and refinement

## Dependencies
- *PyTorch*: Deep learning framework for transformers
- *sentence-transformers*: For creating document embeddings
- *spaCy*: Natural language processing
- *NLTK*: Text processing and tokenization
- *PyPDF2/pdfplumber*: PDF text extraction
- *scikit-learn*: Machine learning utilities

## Usage

### Build the Docker Image
bash
docker build -t challenge1b .


### Run the Solution
bash
# Option 1: Using volume mounts (recommended)
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output challenge1b

# Option 2: Test the Docker environment
docker run --rm -v $(pwd)/input:/app/input challenge1b python test_docker.py


### Input Format
Place your JSON input files in the input/ directory. Each JSON file should contain:
- documents: List of PDF files to process
- persona: User persona description
- job_to_be_done: Task description

### Output
The solution generates JSON output files in the output/ directory with:
- Extracted and ranked sections
- Subsection analysis
- Processing metadata

## File Structure

Challenge_1b/
├── main.py              # Main processing script
├── persona_analyzer.py  # Persona analysis module
├── chunk_embedder.py    # Document embedding module
├── section_ranker.py    # Section ranking module
├── utils.py            # Utility functions
├── test_docker.py      # Docker environment test
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── input/             # Input JSON and PDF files
└── output/            # Output JSON files
