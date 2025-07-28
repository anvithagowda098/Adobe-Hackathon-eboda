import os
import json
from pathlib import Path
from persona_analyzer import PersonaAnalyzer
from chunk_embedder import ChunkEmbedder
from section_ranker import SectionRanker
from utils import PDFProcessor
from datetime import datetime
import time
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def process_collection(collection_dir):
    collection_path = Path(collection_dir)
    pdfs_path = collection_path / "PDFs"
    pdf_files = list(pdfs_path.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdfs_path}")
        return

    # Try to read persona and job from *_input.json if present
    input_jsons = list(collection_path.glob("*_input.json"))
    persona = f"Persona for {collection_path.name}"
    job = f"Job to be done for {collection_path.name}"
    if input_jsons:
        with open(input_jsons[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Extract string values if persona/job_to_be_done are dicts
            p = data.get('persona')
            if isinstance(p, dict):
                persona = next(iter(p.values()))
            elif isinstance(p, str):
                persona = p
            j = data.get('job_to_be_done')
            if isinstance(j, dict):
                job = next(iter(j.values()))
            elif isinstance(j, str):
                job = j

    all_sections = []
    document_texts = {}
    start_time = time.time()

    for pdf_file in pdf_files:
        pdf_processor = PDFProcessor()
        text, sections = pdf_processor.extract_structured_content(pdf_file)
        print(f"First 500 chars of extracted text from {pdf_file}:\n{text[:500]}")
        print(f"Section titles extracted from {pdf_file}: {[s['title'] for s in sections]}")
        if not sections:
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
            for i, para in enumerate(paragraphs):
                sections.append({
                    'title': f'Paragraph {i+1}',
                    'text': para,
                    'page': 1
                })
        document_texts[pdf_file.name] = text
        for section in sections:
            section['document'] = pdf_file.name
            all_sections.append(section)

    print(f"Number of sections to rank: {len(all_sections)}")
    for s in all_sections[:3]:
        print(f"Section: {s['title'][:50]}... Text: {s['text'][:100]}...")

    persona_analyzer = PersonaAnalyzer()
    chunk_embedder = ChunkEmbedder()
    section_ranker = SectionRanker()
    persona_vector = persona_analyzer.analyze_persona(persona, job)
    section_embeddings = chunk_embedder.embed_sections(all_sections)
    ranked_sections = section_ranker.rank_sections(
        all_sections, section_embeddings, persona_vector, {'job_to_be_done': job, 'persona': persona}
    )
    print(f"Ranked section titles: {[s['section_title'] for s in ranked_sections]}")
    print(f"Ranked {len(ranked_sections)} sections for {collection_path.name}")

    # Generate sub-section analysis (improved: use job keywords, compact output)
    subsections = []
    job_keywords = [w.lower() for w in job.split() if len(w) > 3]
    for section in ranked_sections[:10]:
        doc_name = section['document']
        if doc_name in document_texts:
            # Split into sentences for more compact extraction
            from nltk.tokenize import sent_tokenize
            sentences = sent_tokenize(document_texts[doc_name])
            relevant_sents = [s for s in sentences if any(kw in s.lower() for kw in job_keywords)]
            # Take up to 3 most relevant sentences for each section
            if relevant_sents:
                refined = ' '.join(relevant_sents[:3])
                subsections.append({
                    'document': doc_name,
                    'refined_text': refined,
                    'page_number': section['page_number']
                })
            if len(subsections) >= 10:
                break
    print(f"Extracted {len(subsections)} subsections for {collection_path.name}")

    output = {
        "metadata": {
            "input_documents": [pdf.name for pdf in pdf_files],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": s["importance_rank"],
                "page_number": s["page_number"]
            } for s in ranked_sections[:10]
        ],
        "subsection_analysis": subsections[:10]
    }

    output_file = collection_path / f"{collection_path.name}_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Completed {collection_path.name} in {time.time() - start_time:.2f}s")

def main():
    cwd = Path(".")
    collection_dirs = [d for d in cwd.iterdir() if d.is_dir() and d.name.startswith("Collection ")]
    if not collection_dirs:
        print("No collection folders found.")
        return
    for collection_dir in collection_dirs:
        process_collection(collection_dir)

if __name__ == "__main__":
    main() 