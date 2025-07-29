import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.indonesian_processor import normalize_indonesian_query
from app.pdf_processor import format_as_answer

class SemanticSearch:
    def __init__(self, chunks, embeddings, similarity_threshold=0.4):
        """
        Inisialisasi pencarian semantik dengan chunks dan embeddings mereka
        
        Args:
            chunks (list): Daftar potongan teks
            embeddings (numpy.ndarray): Array embeddings untuk potongan teks
            similarity_threshold (float): Ambang batas kemiripan minimal untuk hasil yang relevan
        """
        self.chunks = chunks
        self.embeddings = embeddings
        self.similarity_threshold = similarity_threshold
        
    def search(self, query_embedding, top_k=3):
        """
        Mencari potongan teks yang paling mirip dengan query
        
        Args:
            query_embedding (numpy.ndarray): Embedding dari query
            top_k (int): Jumlah hasil teratas yang akan dikembalikan
            
        Returns:
            list: Daftar tuple (chunk, skor) untuk top_k chunks yang paling mirip
        """
        # Mengubah bentuk query embedding untuk perhitungan kemiripan
        query_embedding = query_embedding.reshape(1, -1)
        
        # Menghitung kemiripan kosinus antara query dan semua chunks
        similarity_scores = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Mendapatkan indeks dari top_k skor tertinggi yang melewati threshold
        filtered_indices = [i for i, score in enumerate(similarity_scores) if score >= self.similarity_threshold]
        
        # Jika tidak ada yang melewati threshold, ambil top_k tertinggi
        if not filtered_indices and len(similarity_scores) > 0:
            filtered_indices = np.argsort(similarity_scores)[::-1][:top_k]
        
        # Urutkan indeks berdasarkan skor
        sorted_indices = sorted(filtered_indices, key=lambda i: similarity_scores[i], reverse=True)[:top_k]
        
        # Mengembalikan top_k chunks dengan skor mereka
        return [(self.chunks[i], similarity_scores[i]) for i in sorted_indices]
    
    def get_response(self, query, query_embedding):
        """
        Mendapatkan respons berdasarkan chunk yang paling relevan
        
        Args:
            query (str): Query asli pengguna
            query_embedding (numpy.ndarray): Embedding dari query
            
        Returns:
            dict: Dictionary berisi jawaban, skor kemiripan, dan metadata lainnya
        """
        # Normalisasi query untuk pencarian yang lebih baik
        normalized_query = normalize_indonesian_query(query)
        
        # Dapatkan hasil pencarian teratas
        search_results = self.search(query_embedding, top_k=3)
        
        # Jika tidak ada hasil yang melewati threshold
        if not search_results:
            return {
                "answer": f"Maaf, tidak ditemukan informasi yang relevan tentang '{query}' dalam dokumen.",
                "similarity_score": 0.0,
                "source": "Tidak ada sumber yang relevan"
            }
        
        top_chunk, top_score = search_results[0]
        
        # Format jawaban menggunakan chunk teratas
        formatted_answer = format_as_answer(query, top_chunk)
        
        # Gabungkan informasi dari beberapa chunk jika skor mereka cukup dekat
        if len(search_results) > 1 and search_results[1][1] > top_score - 0.1:
            # Tambahkan informasi dari chunk kedua jika cukup relevan
            second_chunk, _ = search_results[1]
            additional_info = format_as_answer("", second_chunk)
            if len(formatted_answer + " " + additional_info) < 500:  # Batasi panjang jawaban
                formatted_answer += " " + additional_info
        
        return {
            "answer": formatted_answer,
            "similarity_score": float(top_score),
            "source": "Potongan dokumen yang relevan"
        }