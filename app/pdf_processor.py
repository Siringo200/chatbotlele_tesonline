import fitz  # PyMuPDF
import os
import re
import logging

# Import dari paket yang sama dengan import relatif
from app.indonesian_processor import preprocess_indonesian_text

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Mengekstrak teks dari file PDF
    
    Args:
        pdf_path (str): Path ke file PDF
        
    Returns:
        str: Teks yang diekstrak dari PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File PDF tidak ditemukan: {pdf_path}")
        
    text = ""
    try:
        # Buka PDF
        doc = fitz.open(pdf_path)
        
        # Ekstrak teks dari setiap halaman
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
            
        return text
    except Exception as e:
        raise Exception(f"Error saat mengekstrak teks dari PDF: {str(e)}")

def split_text_into_chunks(text, chunk_size=300, overlap=30):
    """
    Membagi teks menjadi potongan berdasarkan paragraf untuk informasi yang lebih koheren
    
    Args:
        text (str): Teks yang akan dibagi
        chunk_size (int): Target jumlah kata per potongan (digunakan sebagai panduan)
        overlap (int): Jumlah kata yang tumpang tindih antar potongan jika diperlukan
        
    Returns:
        list: Daftar potongan teks
    """
    # Bersihkan dan normalisasi teks
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Bagi teks berdasarkan paragraf (beberapa baris baru, titik diikuti spasi, dll.)
    paragraphs = re.split(r'\n\s*\n|\.\s+(?=[A-Z])', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = ""
    current_word_count = 0
    
    for paragraph in paragraphs:
        paragraph_word_count = len(paragraph.split())
        
        # Jika menambahkan paragraf ini melebihi ukuran potongan terlalu banyak
        if current_word_count > 0 and current_word_count + paragraph_word_count > chunk_size * 1.5:
            # Simpan potongan saat ini dan mulai yang baru
            chunks.append(current_chunk)
            current_chunk = paragraph
            current_word_count = paragraph_word_count
        else:
            # Tambahkan paragraf ke potongan saat ini
            if current_chunk:
                current_chunk += " " + paragraph
            else:
                current_chunk = paragraph
            current_word_count += paragraph_word_count
    
    # Tambahkan potongan terakhir jika tidak kosong
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_pdf(pdf_path="data/lele.pdf", chunk_size=300, overlap=30):
    """
    Memproses file PDF: ekstrak teks dan bagi menjadi potongan
    
    Args:
        pdf_path (str): Path ke file PDF
        chunk_size (int): Target jumlah kata per potongan
        overlap (int): Jumlah kata yang tumpang tindih antar potongan
        
    Returns:
        list: Daftar potongan teks
    """
    # Ekstrak teks dari PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Bagi teks menjadi potongan
    chunks = split_text_into_chunks(text, chunk_size, overlap)
    
    return chunks

def post_process_chunk(chunk):
    """
    Memproses potongan teks agar lebih mudah dibaca sebagai jawaban
    
    Args:
        chunk (str): Potongan teks mentah
        
    Returns:
        str: Teks yang diproses lebih cocok sebagai jawaban
    """
    # Hapus pola sitasi seperti [1], [2], dll.
    processed = re.sub(r'\[\d+\]', '', chunk)
    
    # Hapus bagian referensi
    if "daftar pustaka" in processed.lower() or "referensi" in processed.lower():
        processed = re.split(r'daftar pustaka|referensi', processed, flags=re.IGNORECASE)[0]
    
    # Hapus kalimat tidak lengkap di awal
    processed = re.sub(r'^[^A-Z].*?(?=[A-Z])', '', processed)
    
    # Hapus kalimat tidak lengkap di akhir
    if not processed.endswith('.'):
        processed = re.sub(r'[.!?][^.!?]*$', '.', processed + '.')
    
    return processed.strip()

def format_as_answer(query, chunk):
    """
    Format potongan teks sebagai jawaban yang lebih alami untuk query
    
    Args:
        query (str): Query asli
        chunk (str): Potongan teks yang relevan
        
    Returns:
        str: Jawaban yang diformat
    """
    # Bersihkan potongan
    processed_chunk = post_process_chunk(chunk)
    
    # Buat frasa pengantar berdasarkan jenis query
    if query.lower().startswith('apa '):
        intro = "Berdasarkan dokumen, "
    elif query.lower().startswith('bagaimana '):
        intro = "Menurut informasi yang tersedia, "
    elif query.lower().startswith('mengapa ') or query.lower().startswith('kenapa '):
        intro = "Dokumen menjelaskan bahwa "
    else:
        intro = "Informasi dari dokumen menyebutkan bahwa "
    
    # Gabungkan intro dengan potongan yang diproses
    answer = intro + processed_chunk
    
    return answer