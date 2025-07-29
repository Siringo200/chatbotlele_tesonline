import re

def preprocess_indonesian_text(text):
    """
    Melakukan pra-pemrosesan teks bahasa Indonesia
    
    Args:
        text (str): Teks yang akan diproses
        
    Returns:
        str: Teks yang sudah diproses
    """
    # Menghapus karakter khusus
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Menghapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Mengubah ke huruf kecil
    text = text.lower()
    
    # Proses lainnya khusus bahasa Indonesia bisa ditambahkan di sini
    
    return text

def normalize_indonesian_query(query):
    """
    Menormalisasi query bahasa Indonesia
    
    Args:
        query (str): Query yang akan dinormalisasi
        
    Returns:
        str: Query yang sudah dinormalisasi
    """
    # Menghapus kata-kata umum (stopwords) dalam bahasa Indonesia jika diperlukan
    # Contoh stopwords: "yang", "dan", "di", "ke", dll.
    
    # Untuk implementasi sederhana, kita hanya lakukan basic preprocessing
    return preprocess_indonesian_text(query)
