from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import uvicorn
from pydantic import BaseModel
import time

# Change back to absolute imports
from app.pdf_processor import process_pdf
from app.embeddings import EmbeddingGenerator
from app.search import SemanticSearch
from app.indonesian_processor import normalize_indonesian_query

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Chatbot Ikan",
    description="API untuk mendapatkan jawaban dari dokumen PDF",
    version="1.0.0"
)

# Tambahkan middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk produksi, tentukan asal yang sebenarnya
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variabel global untuk menyimpan data
pdf_chunks = []
embedding_generator = None
searcher = None
pdf_processed = False

# Fungsi inisialisasi untuk memproses PDF dan menghasilkan embedding
def initialize_system(pdf_path="data/lele.pdf"):
    global pdf_chunks, embedding_generator, searcher, pdf_processed
    
    try:
        # Proses PDF
        logger.info(f"Memproses PDF: {pdf_path}")
        pdf_chunks = process_pdf(pdf_path)
        
        # Inisialisasi generator embedding
        logger.info("Menginisialisasi generator embedding")
        embedding_generator = EmbeddingGenerator()
        
        # Hasilkan embedding untuk potongan teks
        logger.info(f"Menghasilkan embedding untuk {len(pdf_chunks)} potongan teks")
        chunk_embeddings = embedding_generator.generate_embeddings(pdf_chunks)
        
        # Inisialisasi pencarian semantik
        logger.info("Menginisialisasi pencarian semantik")
        searcher = SemanticSearch(pdf_chunks, chunk_embeddings)
        
        pdf_processed = True
        logger.info("Inisialisasi sistem selesai")
        
        return True
    except Exception as e:
        logger.error(f"Kesalahan saat menginisialisasi sistem: {str(e)}")
        return False

# Model permintaan untuk kueri
class QueryRequest(BaseModel):
    query: str

# Endpoint untuk memeriksa apakah sistem siap
@app.get("/status")
async def status():
    return {"status": "ready" if pdf_processed else "not_ready"}

# Endpoint untuk mengajukan pertanyaan
@app.post("/ask")
async def ask(request: QueryRequest):
    # Periksa apakah sistem sudah diinisialisasi
    if not pdf_processed:
        success = initialize_system()
        if not success:
            raise HTTPException(status_code=500, detail="Gagal menginisialisasi sistem")
    
    try:
        query = request.query
        logger.info(f"Pertanyaan diterima: {query}")
        
        start_time = time.time()
        
        # Normalisasi kueri bahasa Indonesia
        normalized_query = normalize_indonesian_query(query)
        
        # Hasilkan embedding untuk kueri
        query_embedding = embedding_generator.generate_query_embedding(normalized_query)
        
        # Dapatkan respons dengan query asli dan embedding
        response = searcher.get_response(normalized_query, query_embedding)
        
        process_time = time.time() - start_time
        logger.info(f"Pertanyaan diproses dalam {process_time:.2f} detik")
        
        # Tambahkan waktu pemrosesan ke respons
        response["processing_time"] = f"{process_time:.2f} detik"
        
        return response
    except Exception as e:
        logger.error(f"Kesalahan saat memproses pertanyaan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint untuk mengunggah PDF baru
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global pdf_processed
    
    try:
        # Pastikan direktori data ada
        os.makedirs("data", exist_ok=True)
        
        # Simpan file yang diunggah
        file_path = os.path.join("data", "uploaded.pdf")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        logger.info(f"PDF diunggah: {file_path}")
        
        # Reset status sistem
        pdf_processed = False
        
        # Inisialisasi sistem dengan PDF baru
        success = initialize_system(file_path)
        
        if success:
            return {"status": "success", "message": "PDF diunggah dan diproses dengan sukses"}
        else:
            raise HTTPException(status_code=500, detail="Gagal memproses PDF yang diunggah")
    except Exception as e:
        logger.error(f"Kesalahan saat mengunggah PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Pasang file statis untuk frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Acara startup untuk menginisialisasi sistem
@app.on_event("startup")
async def startup_event():
    # Inisialisasi sistem saat startup
    initialize_system()

if __name__ == "__main__":
    # Use an absolute import path for uvicorn
    # This assumes you're running from the parent directory
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)