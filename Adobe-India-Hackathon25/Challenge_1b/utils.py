import json
import PyPDF2
import pdfplumber
import re
from pathlib import Path

def load_json_input(file_path):
    """Load and validate input JSON specification"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate required fields
    required_fields = ['documents', 'persona', 'job_to_be_done']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Support documents as list of dicts (with filename/title)
    if isinstance(data['documents'], list) and data['documents'] and isinstance(data['documents'][0], dict):
        data['input_documents'] = [doc['filename'] for doc in data['documents']]
    else:
        data['input_documents'] = data['documents']
    return data

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_structured_content(self, pdf_path):
        """Extract text and structure from PDF"""
        try:
            # Try pdfplumber first for better text extraction
            return self._extract_with_pdfplumber(pdf_path)
        except Exception as e:
            print(f"pdfplumber failed for {pdf_path}: {e}")
            # Fallback to PyPDF2
            return self._extract_with_pypdf2(pdf_path)
    
    def _extract_with_pdfplumber(self, pdf_path):
        """Extract content using pdfplumber"""
        all_text = ""
        sections = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    
                    # Extract sections from this page
                    page_sections = self._extract_sections_from_text(
                        page_text, page_num
                    )
                    sections.extend(page_sections)
        
        # If no structured sections found, create default sections
        if not sections:
            sections = self._create_default_sections(all_text)
        
        return all_text, sections
    
    def _extract_with_pypdf2(self, pdf_path):
        """Extract content using PyPDF2 as fallback"""
        all_text = ""
        sections = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    
                    page_sections = self._extract_sections_from_text(
                        page_text, page_num
                    )
                    sections.extend(page_sections)
        
        if not sections:
            sections = self._create_default_sections(all_text)
        
        return all_text, sections
    
    def _extract_sections_from_text(self, text, page_num):
        """Extract sections from text using robust heuristics"""
        sections = []
        # Enhanced heading patterns
        heading_patterns = [
            r'^([A-Z][A-Z\s]{2,50})$',  # ALL CAPS headings
            r'^(.*:)$',  # Lines ending with colon
            r'^([A-Z][^\n]{0,60})$',  # Any short line starting with capital
            r'^(\w+(?:\s+\w+){3,})$',  # Lines with >3 words
        ]
        lines = text.split('\n')
        current_section_text = ""
        current_title = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            is_heading = False
            for pattern in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    if current_title and current_section_text:
                        sections.append({
                            'title': current_title,
                            'text': current_section_text.strip(),
                            'page': page_num
                        })
                    current_title = match.group(1) if match.groups() else line
                    current_section_text = ""
                    is_heading = True
                    break
            # Heuristic: treat as heading if >70% uppercase and >10 chars
            if not is_heading and len(line) > 10 and sum(1 for c in line if c.isupper()) / max(1, len(line)) > 0.7:
                if current_title and current_section_text:
                    sections.append({
                        'title': current_title,
                        'text': current_section_text.strip(),
                        'page': page_num
                    })
                current_title = line
                current_section_text = ""
                is_heading = True
            if not is_heading:
                current_section_text += line + " "
        if current_title and current_section_text:
            sections.append({
                'title': current_title,
                'text': current_section_text.strip(),
                'page': page_num
            })
        # Fallback: if no headings found, split on single newlines as sections
        if not sections and text.strip():
            paras = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
            for i, para in enumerate(paras):
                sections.append({
                    'title': f'Line {i+1}',
                    'text': para,
                    'page': page_num
                })
        return sections
    
    def _create_default_sections(self, all_text):
        """Create default sections when no structure is detected"""
        # Split text into chunks of reasonable size
        words = all_text.split()
        chunk_size = 500
        sections = []
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            sections.append({
                'title': f'Section {len(sections) + 1}',
                'text': chunk_text,
                'page': 1  # Default page
            })
        
        return sections