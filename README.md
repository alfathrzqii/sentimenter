Proyek Sentimenter - Flask & IndoBERT

Ini adalah kerangka kerja aplikasi web untuk analisis sentimen bahasa Indonesia menggunakan Flask dan model IndoBERT dari Hugging Face.

Struktur Proyek

/
|-- app.py             # File utama Flask
|-- model.py           # Logika pemuatan & prediksi model ML
|-- requirements.txt   # Kebutuhan library Python
|-- templates/
|   |-- layout.html    # Template dasar (sidebar, layout)
|   |-- home.html      # Halaman landing
|   |-- dashboard.html # Halaman dashboard
|   |-- analysis.html  # Halaman form analisis
|   |-- about.html     # Halaman tentang


Cara Menjalankan Proyek

Buat Lingkungan Virtual (Direkomendasikan)

python -m venv venv
source venv/bin/activate  # Di Windows, gunakan: venv\Scripts\activate


Install Kebutuhan

pip install -r requirements.txt


(Catatan: torch dan transformers adalah library yang cukup besar. Proses download mungkin memakan waktu beberapa saat.)

Jalankan Aplikasi Flask

flask run


Atau, jika Anda ingin menjalankan dalam mode debug:

python app.py


Buka Aplikasi
Buka browser Anda dan navigasikan ke http://127.0.0.1:5000.

Download Model (Saat Pertama Kali)
Saat Anda pertama kali mengunjungi halaman /analysis dan mengirimkan form, model.py akan terpicu. Jika model belum di-download, library transformers akan secara otomatis men-download model IndoBERT (sekitar 400-500MB) ke cache Anda. Ini hanya terjadi sekali.

RUN di Virtual Environment

python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
flask run