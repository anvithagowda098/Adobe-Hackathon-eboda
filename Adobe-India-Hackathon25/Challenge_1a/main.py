import os
import json
import re
from pathlib import Path
import fitz  # pymupdf

def extract_text_with_fonts(doc):
    pages_data = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=11)["blocks"]
        text_blocks = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_blocks.append({
                            "text": span["text"].strip(),
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],
                            "page": page_num + 1
                        })
        pages_data.append(text_blocks)
    return pages_data

def is_bold(flags):
    return bool(flags & 2 ** 4)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_title_and_headings(pages_data):
    all_spans = []
    for page_data in pages_data:
        all_spans.extend(page_data)
    all_spans = [span for span in all_spans if span["text"]]
    if not all_spans:
        return None, []
    font_sizes = {}
    for span in all_spans:
        size = span["size"]
        if size not in font_sizes:
            font_sizes[size] = []
        font_sizes[size].append(span)
    sorted_sizes = sorted(font_sizes.keys(), reverse=True)
    title = None
    title_candidates = []
    for span in all_spans[:50]:
        if span["page"] <= 2:
            text = clean_text(span["text"])
            if len(text) > 5 and len(text) < 100:
                title_candidates.append((span["size"], text, span))
    if title_candidates:
        title_candidates.sort(key=lambda x: x[0], reverse=True)
        title = title_candidates[0][1]
    headings = []
    heading_sizes = []
    for size in sorted_sizes:
        spans_with_size = font_sizes[size]
        potential_headings = [
            span for span in spans_with_size
            if (is_bold(span["flags"]) or size > 12) and \
               len(clean_text(span["text"])) > 3 and \
               len(clean_text(span["text"])) < 200
        ]
        if potential_headings and len(potential_headings) < 50:
            heading_sizes.append(size)
            if len(heading_sizes) >= 3:
                break
    size_to_level = {}
    for i, size in enumerate(heading_sizes[:3]):
        size_to_level[size] = f"H{i+1}"
    for span in all_spans:
        if span["size"] in size_to_level:
            text = clean_text(span["text"])
            if len(text) > 3 and len(text) < 200:
                if title and text == title:
                    continue
                if re.search(r'[a-zA-Z]', text) and not re.match(r'^[\d\s\.\-\(\)]+$', text):
                    headings.append({
                        "level": size_to_level[span["size"]],
                        "text": text,
                        "page": span["page"]
                    })
    seen = set()
    unique_headings = []
    for heading in headings:
        key = (heading["level"], heading["text"])
        if key not in seen:
            seen.add(key)
            unique_headings.append(heading)
    return title, unique_headings

def process_single_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        pages_data = extract_text_with_fonts(doc)
        title, headings = extract_title_and_headings(pages_data)
        doc.close()
        if not title:
            title = pdf_path.stem.replace('_', ' ').replace('-', ' ').title()
        return {
            "title": title,
            "outline": headings
        }
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return {
            "title": pdf_path.stem.replace('_', ' ').replace('-', ' ').title(),
            "outline": []
        }

def process_pdfs():
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    for pdf_file in pdf_files:
        result = process_single_pdf(pdf_file)
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Processed {pdf_file.name} -> {output_file.name}")

if __name__ == "__main__":
    print("Starting processing pdfs")
    process_pdfs()
    print("completed processing pdfs")