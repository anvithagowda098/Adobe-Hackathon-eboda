import re
from sentence_transformers import SentenceTransformer
import numpy as np

class PersonaAnalyzer:
    def __init__(self):
        # Load lightweight sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Persona-specific keywords and domains
        self.persona_keywords = {
            'researcher': ['methodology', 'analysis', 'study', 'research', 'literature', 'findings'],
            'student': ['concepts', 'learning', 'understanding', 'examples', 'theory', 'practice'],
            'analyst': ['trends', 'data', 'metrics', 'performance', 'comparison', 'insights'],
            'investor': ['revenue', 'growth', 'market', 'financial', 'risk', 'opportunity'],
            'sales': ['customer', 'product', 'market', 'competitive', 'value', 'solution']
        }
        
    def analyze_persona(self, persona_desc, job_desc):
        """Analyze persona and create semantic vector for matching"""
        
        # Combine persona and job descriptions
        combined_text = f"{persona_desc} {job_desc}"
        
        # Extract persona type
        persona_type = self._extract_persona_type(persona_desc.lower())
        
        # Create base embedding
        base_embedding = self.model.encode(combined_text)
        
        # Enhance with persona-specific keywords
        keyword_weights = self._get_keyword_weights(persona_type, combined_text.lower())
        
        # Create enhanced persona vector
        persona_vector = {
            'embedding': base_embedding,
            'persona_type': persona_type,
            'keyword_weights': keyword_weights,
            'job_focus': self._extract_job_focus(job_desc)
        }
        
        return persona_vector
    
    def _extract_persona_type(self, persona_text):
        """Extract main persona category"""
        for ptype, keywords in self.persona_keywords.items():
            if any(keyword in persona_text for keyword in keywords[:2]):
                return ptype
        
        # Default classification based on common terms
        if 'phd' in persona_text or 'research' in persona_text:
            return 'researcher'
        elif 'student' in persona_text:
            return 'student'
        elif 'analyst' in persona_text or 'investment' in persona_text:
            return 'analyst'
        else:
            return 'general'
    
    def _get_keyword_weights(self, persona_type, text):
        """Calculate keyword importance weights"""
        weights = {}
        if persona_type in self.persona_keywords:
            keywords = self.persona_keywords[persona_type]
            for keyword in keywords:
                weights[keyword] = text.count(keyword) + 1
        return weights
    
    def _extract_job_focus(self, job_desc):
        """Extract key focus areas from job description"""
        focus_patterns = [
            r'focus(?:ing)? on (.+?)(?:\.|,|$)',
            r'analyze (.+?)(?:\.|,|$)',
            r'identify (.+?)(?:\.|,|$)',
            r'prepare (.+?)(?:\.|,|$)',
            r'summarize (.+?)(?:\.|,|$)'
        ]
        
        focuses = []
        for pattern in focus_patterns:
            matches = re.findall(pattern, job_desc.lower())
            focuses.extend(matches)
        
        return focuses[:3]  # Top 3 focus areas