document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const queryInput = document.getElementById('query');
    const askButton = document.getElementById('askButton');
    const responseDiv = document.getElementById('response');
    const metadataDiv = document.getElementById('metadata');
    const loader = document.getElementById('loader');
    const pdfFileInput = document.getElementById('pdfFile');
    const uploadButton = document.getElementById('uploadButton');
    const uploadStatusDiv = document.getElementById('uploadStatus');

    // Check if backend is ready
    async function checkStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            return data.status === 'ready';
        } catch (error) {
            console.error('Error checking status:', error);
            return false;
        }
    }

    // Handle ask button click
    askButton.addEventListener('click', async function() {
        const query = queryInput.value.trim();
        
        if (!query) {
            alert('Silakan masukkan pertanyaan.');
            return;
        }
        
        // Show loader
        loader.style.display = 'block';
        responseDiv.textContent = 'Sedang berpikir...';
        metadataDiv.textContent = '';
        
        try {
            // Check if system is ready
            const isReady = await checkStatus();
            if (!isReady) {
                responseDiv.textContent = 'Sistem sedang menginisialisasi. Silakan coba lagi sebentar.';
                loader.style.display = 'none';
                return;
            }
            
            // Send query to API
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Check if similarity score is too low (below 40%)
            if (data.similarity_score < 0.4) {
                responseDiv.textContent = `Maaf, pertanyaan "${query}" tidak relevan dengan dokumen atau tidak dapat ditemukan dalam konteks yang tersedia. Silakan coba pertanyaan lain tentang budidaya lele.`;
            } else {
                // Display response
                responseDiv.textContent = data.answer;
            }
            
            // Display metadata
            metadataDiv.textContent = `Skor kesamaan: ${(data.similarity_score * 100).toFixed(2)}% | Waktu pemrosesan: ${data.processing_time}`;
            
        } catch (error) {
            console.error('Error:', error);
            responseDiv.textContent = `Error: ${error.message}`;
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });

    // Allow pressing Enter to submit query
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            askButton.click();
        }
    });

    // Handle file upload
    uploadButton.addEventListener('click', async function() {
        const file = pdfFileInput.files[0];
        
        if (!file) {
            alert('Silakan pilih file PDF.');
            return;
        }
        
        if (file.type !== 'application/pdf') {
            alert('Silakan pilih file PDF yang valid.');
            return;
        }
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Show upload status
        uploadStatusDiv.textContent = 'Mengunggah...';
        
        try {
            // Send file to API
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display upload status
            uploadStatusDiv.textContent = data.message;
            
            // Clear input
            pdfFileInput.value = '';
            
        } catch (error) {
            console.error('Error:', error);
            uploadStatusDiv.textContent = `Error: ${error.message}`;
        }
    });

    // Initial status check
    checkStatus().then(isReady => {
        if (!isReady) {
            responseDiv.textContent = 'Sistem sedang menginisialisasi. Silakan tunggu sebentar sebelum mengajukan pertanyaan.';
        }
    });
});