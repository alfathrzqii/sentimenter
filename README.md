# **Sentimenter — Analisis Sentimen IndoBERT**

Sentimenter adalah aplikasi web berbasis **Flask** yang menggunakan model **IndoBERT** dari Hugging Face untuk melakukan **analisis sentimen teks berbahasa Indonesia**.

Aplikasi ini mendukung analisis teks tunggal maupun analisis massal dari file.

---

## 🚀 **Fitur Utama**

### ✅ **1. Analisis Teks Tunggal**
Prediksi sentimen:
- **Positif**
- **Negatif**
- **Netral**

### ✅ **2. Analisis File Massal**
- Upload file **`.csv`** atau **`.xlsx`**
- Memilih satu kolom teks untuk dianalisis
- Otomatis menghasilkan:
  - **Bar Chart**
  - **Pie Chart**
  - **Word Cloud**

### ✅ **3. Visualisasi**
Menampilkan berbagai grafik hasil analisis secara otomatis.

### ✅ **4. Tabel Hasil**
Menampilkan DataFrame hasil analisis langsung di halaman aplikasi.

---

## 📁 **Struktur Proyek**

```
/sentimenter
│
├── /static/
│   ├── /css/
│   ├── /images/
│
├── /uploads/             # Folder otomatis untuk file upload sementara
│
├── /templates/
│   ├── layout.html       # Template dasar dengan sidebar
│   ├── home.html         # Halaman landing
│   ├── dashboard.html    # Halaman visualisasi (dummy)
│   ├── analysis.html     # Halaman analisis teks & file
│   └── about.html        # Halaman about
│
├── app.py                # Routing utama Flask
├── model.py              # Pemuatan model dan fungsi visualisasi ML
├── requirements.txt      # Dependency Python
└── README.md             # Dokumentasi proyek
```

---

## 🔧 **Cara Menjalankan Aplikasi**

### **1. Clone atau Salin Proyek**
Buat folder baru dan salin semua file proyek ke dalamnya.

### **2. Buat Virtual Environment**
```bash
python -m venv venv
```

### **3. Aktifkan Virtual Environment**

#### Windows (PowerShell)
```bash
.\venv\Scripts\activate
```

#### Windows (CMD)
```bash
venv\Scripts\activate
```

#### macOS / Linux
```bash
source venv/bin/activate
```

### **4. Install Kebutuhan**
```bash
pip install -r requirements.txt
```

> Catatan: instalasi `torch` mungkin memakan waktu cukup lama.

### **5. Jalankan Aplikasi**
```bash
flask run
```

Jika ini run pertama, model IndoBERT akan otomatis diunduh dari Hugging Face.

### **6. Buka Aplikasi**
```
http://127.0.0.1:5000
```

---

## This website live on:
```
https://sentimenter-jiid.onrender.com/
```