# Adobe India Hackathon 2025 - Connecting the Dots

## Project Overview
This repository contains solutions for both Round 1A (Document Structure Extraction) and Round 1B (Persona-Driven Document Intelligence) of the "Connecting the Dots" challenge.

## Structure
- `Challenge_1a/`: PDF outline extraction solution
- `Challenge_1b/`: Persona-driven document intelligence solution
- `approach_explanation.md`: Detailed methodology for Round 1B

## Round 1B Solution
Our Round 1B implementation provides intelligent document analysis that:
- Extracts and ranks relevant sections based on persona and job requirements
- Uses semantic embeddings for content understanding
- Implements multi-factor relevance scoring
- Provides granular subsection analysis

### Key Features
- Offline operation with no internet dependencies
- CPU-only processing under 60 seconds
- Model size under 1GB total

### Teammates
- Bhumi Garg
- Anvitha Gowda
- Kashish Rai

## Quick Start
```bash
# Build Challenge 1B
cd Challenge_1b
docker build --platform linux/amd64 -t challenge1b:latest .

# Run with input/output volumes
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1b:latest
