from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedding generator with a sentence transformer model
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        
    def generate_embeddings(self, texts):
        """
        Generate embeddings for a list of texts
        
        Args:
            texts (list): List of text strings
            
        Returns:
            numpy.ndarray: Array of embeddings
        """
        return self.model.encode(texts)
    
    def generate_query_embedding(self, query):
        """
        Generate embedding for a single query text
        
        Args:
            query (str): Query text
            
        Returns:
            numpy.ndarray: Query embedding
        """
        return self.model.encode(query)

