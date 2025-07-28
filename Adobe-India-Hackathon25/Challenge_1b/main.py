#!/usr/bin/env python3
import os
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from persona_analyzer import PersonaAnalyzer
from chunk_embedder import ChunkEmbedder
from section_ranker import SectionRanker
from utils import PDFProcessor, load_json_input

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load input specification
    input_files = list(input_dir.glob("*.json"))
    if not input_files:
        print("No JSON input files found in /app/input")
        sys.exit(1)
    
    # Process each input file
    for input_file in input_files:
        try:
            print(f"Processing {input_file.name}")
            start_time = time.time()
            
            # Load input specification
            spec = load_json_input(input_file)
            
            # Initialize components
            persona_analyzer = PersonaAnalyzer()
            chunk_embedder = ChunkEmbedder()
            section_ranker = SectionRanker()
            pdf_processor = PDFProcessor()
            
            # Process documents
            all_sections = []
            document_texts = {}
            
            for doc in spec['input_documents']:
                doc_file = input_dir / doc
                if doc_file.exists():
                    # Extract text and structure from PDF
                    text, sections = pdf_processor.extract_structured_content(doc_file)
                    document_texts[doc] = text
                    
                    # Add document info to sections
                    for section in sections:
                        section['document'] = doc
                        all_sections.append(section)
            
            # Analyze persona and job requirements
            persona_vector = persona_analyzer.analyze_persona(
                spec['persona'], spec['job_to_be_done']
            )
            
            # Create embeddings for all sections
            section_embeddings = chunk_embedder.embed_sections(all_sections)
            
            # Rank sections based on relevance
            ranked_sections = section_ranker.rank_sections(
                all_sections, section_embeddings, persona_vector, spec
            )
            
            # Generate sub-section analysis
            subsections = section_ranker.extract_subsections(
                ranked_sections[:10], document_texts, persona_vector
            )
            
            # Create output
            output = {
                "metadata": {
                    "input_documents": spec['documents'],
                    "persona": spec['persona'],
                    "job_to_be_done": spec['job_to_be_done'],
                    "processing_timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": round(time.time() - start_time, 2)
                },
                "extracted_sections": [
                    {
                        "document": s["document"],
                        "section_title": s["section_title"],
                        "importance_rank": s["importance_rank"],
                        "page_number": s["page_number"]
                    } for s in ranked_sections[:10]
                ],
                "subsection_analysis": [
                    {
                        "document": ss["document"],
                        "refined_text": ss["refined_text"],
                        "page_number": ss["page_number"]
                    } for ss in subsections
                ]
            }
            
            # Save output
            output_file = output_dir / f"{input_file.stem}_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            print(f"Completed {input_file.name} in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            print(f"Error processing {input_file.name}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()