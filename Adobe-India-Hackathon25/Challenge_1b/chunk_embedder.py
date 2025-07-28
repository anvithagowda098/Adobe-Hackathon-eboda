import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class ChunkEmbedder:
    def __init__(self, chunk_size=500, overlap=100):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def embed_sections(self, sections):
        """Create embeddings for document sections with chunking"""
        section_embeddings = []
        
        for section in sections:
            # Split section into chunks
            chunks = self._create_chunks(section['text'])
            
            # Create embeddings for each chunk
            chunk_embeddings = []
            for chunk in chunks:
                if len(chunk.strip()) > 20:  # Skip very short chunks
                    embedding = self.model.encode(chunk)
                    chunk_embeddings.append({
                        'text': chunk,
                        'embedding': embedding,
                        'length': len(chunk)
                    })
            
            # Aggregate chunk embeddings for section
            if chunk_embeddings:
                section_embedding = self._aggregate_embeddings(chunk_embeddings)
                section_embeddings.append({
                    'section_id': len(section_embeddings),
                    'document': section['document'],
                    'title': section.get('title', 'Unknown'),
                    'page': section.get('page', 1),
                    'embedding': section_embedding,
                    'chunks': chunk_embeddings,
                    'text': section['text']
                })
        
        return section_embeddings
    
    def _create_chunks(self, text, use_sentences=True):
        """Create overlapping chunks from text"""
        if use_sentences:
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) <= self.chunk_size:
                    current_chunk += " " + sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                    
                    # Add overlap from previous chunk
                    if chunks and len(chunks[-1]) > self.overlap:
                        overlap_text = chunks[-1][-self.overlap:]
                        current_chunk = overlap_text + " " + current_chunk
            
            if current_chunk:
                chunks.append(current_chunk.strip())
                
            return chunks
        else:
            # Simple character-based chunking
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.overlap):
                chunk = text[i:i + self.chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
            return chunks
    
    def _aggregate_embeddings(self, chunk_embeddings):
        """Aggregate multiple chunk embeddings into section embedding"""
        # Weighted average based on chunk length
        embeddings = np.array([ce['embedding'] for ce in chunk_embeddings])
        weights = np.array([ce['length'] for ce in chunk_embeddings])
        weights = weights / weights.sum()
        
        return np.average(embeddings, axis=0, weights=weights)
    
    def compute_similarity(self, embedding1, embedding2):
        """Compute cosine similarity between two embeddings"""
        return cosine_similarity([embedding1], [embedding2])[0][0]