# Approach Explanation - Adobe India Hackathon 2025

## Overview
This document explains the comprehensive approach used for the "Connecting the Dots" challenge, covering both Round 1A (Document Structure Extraction) and Round 1B (Persona-Driven Document Intelligence).

## Challenge 1A:
Document Structure Extraction

### Methodology
The PDF outline extraction solution employs a heuristic-based approach that leverages typography analysis for structure identification. The core strategy focuses on font size ranking to distinguish hierarchical document elements.
**Key Components:**- **Title Detection**: Identifies the largest text on the first page as the document title, assuming standard document formatting conventions. **Heading Classification**: Maps the three largest font sizes throughout the document to H1, H2, and H3 levels respectively.
**Multi-factor Analysis**: Considers font size, style, and positional context for robust heading detectionThe approach uses PyMuPDF for precise font metadata extraction, enabling accurate typography-based classification without relying on semantic understanding.

## Challenge 1B: Persona-Driven Document Intelligence

### Architecture Design
The solution implements a sophisticated multi-component architecture that combines semantic understanding with persona-specific analysis:
**Core Components:**1. **PersonaAnalyzer**: Creates semantic vectors from persona descriptions and job requirements using sentence transformers2.
**ChunkEmbedder**: Processes documents through adaptive chunking with sentence-aware splitting3.
**SectionRanker**: Implements multi-factor scoring for relevance assessment4. **PDFProcessor**: Extracts structured content maintaining document hierarchy### Semantic Matching StrategyThe approach leverages the `all-MiniLM-L6-v2` sentence transformer model for creating 384-dimensional embeddings that capture semantic meaning. This enables understanding of conceptual relationships between persona requirements and document content, going beyond simple keyword matching.

### Multi-Factor Ranking Algorithm
The section ranking employs a weighted scoring system:-
**Semantic Similarity (70%)**: Cosine similarity between persona vectors and section embeddings.
**Keyword Matching (10%)**: Persona-specific keyword weighting.
**Positional Context (5%)**: Document structure awareness
**Content Length (5%)**: Section substance evaluation
**Title Relevance (10%)**: Heading-based relevance scoring### Adaptive ProcessingThe system implements intelligent chunking that respects sentence boundaries while maintaining optimal chunk sizes (500 characters with 100-character overlap). This ensures semantic coherence while enabling efficient processing of large documents.

### Technical Constraints Adherence
Both solutions strictly adhere to competition requirements:-
**Offline Operation**: No internet dependencies during processing
**Resource Efficiency**: CPU-only processing under 60 seconds 
**Model Size**: Total models under 1GB
**Containerization**: Docker-based deployment for consistent execution## Innovation HighlightsThe approach demonstrates several innovative aspects: typography-based structure extraction without ML overhead in Challenge 1A, semantic persona matching that understands context rather than just keywords, and adaptive content chunking that maintains semantic integrity while optimizing processing efficiency.This dual-challenge solution showcases the balance between simple heuristic approaches for structural tasks and sophisticated semantic analysis for intelligence-driven document understanding.
