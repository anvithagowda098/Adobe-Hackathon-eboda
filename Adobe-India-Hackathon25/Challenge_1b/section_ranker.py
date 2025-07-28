import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter

class SectionRanker:
    def __init__(self):
        self.importance_weights = {
            'semantic_similarity': 0.7,  # Increased
            'keyword_match': 0.1,        # Decreased
            'section_position': 0.05,    # Decreased
            'section_length': 0.05,      # Decreased
            'title_relevance': 0.1       # Decreased
        }
        
    def rank_sections(self, sections, section_embeddings, persona_vector, spec):
        """Rank sections based on persona and job relevance"""
        scored_sections = []
        
        for i, section_emb in enumerate(section_embeddings):
            if i < len(sections):
                section = sections[i]
                
                # Calculate multiple relevance scores
                scores = self._calculate_relevance_scores(
                    section, section_emb, persona_vector, spec
                )
                
                # Weighted final score
                final_score = sum(
                    scores[key] * self.importance_weights[key]
                    for key in scores
                )
                
                scored_sections.append({
                    'document': section['document'],
                    'page_number': section.get('page', 1),
                    'section_title': section.get('title', 'Untitled'),
                    'importance_rank': len(scored_sections) + 1,  # Will be updated after sorting
                    'relevance_score': final_score,
                    'detailed_scores': scores,
                    'text_preview': section['text'][:200] + "..." if len(section['text']) > 200 else section['text']
                })
        
        # Sort by relevance score
        scored_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Update importance ranks
        for i, section in enumerate(scored_sections):
            section['importance_rank'] = i + 1
            # Remove detailed scores from final output
            section.pop('detailed_scores', None)
            section.pop('relevance_score', None)
        
        return scored_sections
    
    def _calculate_relevance_scores(self, section, section_emb, persona_vector, spec):
        """Calculate various relevance scores for a section"""
        scores = {}
        
        # 1. Semantic similarity with persona embedding
        scores['semantic_similarity'] = cosine_similarity(
            [section_emb['embedding']], 
            [persona_vector['embedding']]
        )[0][0]
        
        # 2. Keyword matching score
        scores['keyword_match'] = self._calculate_keyword_score(
            section['text'], persona_vector, spec
        )
        
        # 3. Section position score (earlier sections often more important)
        scores['section_position'] = max(0, 1 - (section.get('page', 1) - 1) * 0.1)
        
        # 4. Section length score (moderate length preferred)
        text_len = len(section['text'])
        optimal_length = 1000
        scores['section_length'] = max(0, 1 - abs(text_len - optimal_length) / optimal_length)
        
        # 5. Title relevance score
        scores['title_relevance'] = self._calculate_title_relevance(
            section.get('title', ''), persona_vector, spec
        )
        
        return scores
    
    def _calculate_keyword_score(self, text, persona_vector, spec):
        """Calculate keyword matching score"""
        text_lower = text.lower()
        score = 0
        
        # Job-specific keywords
        job_text = spec['job_to_be_done'].lower()
        job_keywords = re.findall(r'\b\w+\b', job_text)
        for keyword in set(job_keywords):
            if len(keyword) > 3 and keyword in text_lower:
                score += 0.1
        
        # Persona-specific keywords
        if 'keyword_weights' in persona_vector:
            for keyword, weight in persona_vector['keyword_weights'].items():
                if keyword in text_lower:
                    score += 0.05 * weight
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_title_relevance(self, title, persona_vector, spec):
        """Calculate title relevance score"""
        if not title:
            return 0
        
        title_lower = title.lower()
        score = 0
        
        # Check for job-related terms in title
        job_terms = spec['job_to_be_done'].lower().split()
        for term in job_terms:
            if len(term) > 3 and term in title_lower:
                score += 0.2
        
        # Check for persona-related terms
        persona_terms = persona_vector.get('job_focus', [])
        for term in persona_terms:
            if term.lower() in title_lower:
                score += 0.3
        
        return min(score, 1.0)
    
    def extract_subsections(self, top_sections, document_texts, persona_vector):
        """Extract and analyze subsections from top sections"""
        subsections = []
        
        for section in top_sections[:5]:  # Top 5 sections only
            doc_name = section['document']
            if doc_name in document_texts:
                # Extract subsections from the full document text
                doc_text = document_texts[doc_name]
                section_subsections = self._find_subsections(
                    doc_text, section, persona_vector
                )
                subsections.extend(section_subsections)
        
        # Sort subsections by relevance
        subsections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Clean up and format
        for subsection in subsections:
            subsection.pop('relevance_score', None)
        
        return subsections[:10]  # Return top 10 subsections
    
    def _find_subsections(self, doc_text, parent_section, persona_vector):
        """Find relevant subsections within a document section"""
        subsections = []
        
        # Simple approach: split by paragraphs and sentences
        paragraphs = doc_text.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 100:  # Minimum length threshold
                # Calculate relevance for this paragraph
                relevance = self._calculate_paragraph_relevance(
                    paragraph, persona_vector
                )
                
                if relevance > 0.3:  # Relevance threshold
                    subsections.append({
                        'document': parent_section['document'],
                        'page_number': parent_section['page_number'],
                        'refined_text': paragraph.strip(),
                        'relevance_score': relevance
                    })
        
        return subsections
    
    def _calculate_paragraph_relevance(self, paragraph, persona_vector):
        """Calculate relevance score for a paragraph"""
        # Simple keyword-based relevance
        score = 0
        para_lower = paragraph.lower()
        
        if 'keyword_weights' in persona_vector:
            for keyword, weight in persona_vector['keyword_weights'].items():
                if keyword in para_lower:
                    score += 0.1 * weight
        
        # Focus area matching
        for focus in persona_vector.get('job_focus', []):
            if focus.lower() in para_lower:
                score += 0.2
        
        return min(score, 1.0)