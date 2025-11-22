import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Gunakan backend 'Agg' agar tidak error di server
import matplotlib.pyplot as plt
import io
import base64
import re
from wordcloud import WordCloud, STOPWORDS

# --- Bagian 1: Pemuatan Model IndoBERT ---

MODEL_NAME = "crypter70/IndoBERT-Sentiment-Analysis"
tokenizer = None
model = None

def load_model():
    """
    Lazy-load the tokenizer and model. This avoids long blocking downloads during module import
    and prevents the Flask app from hanging when importing `model.py`.
    """
    global tokenizer, model
    if tokenizer is not None and model is not None:
        return
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model.eval()
        print(f"Model {MODEL_NAME} loaded successfully.")
    except Exception as e:
        print(f"Error loading model {MODEL_NAME}: {e}")
        print("Model and tokenizer set to None. Predictions will not work.")
        tokenizer = None
        model = None

# Definisikan label berdasarkan konfigurasi model
labels = ['Positif', 'Netral', 'Negatif']

def predict_sentiment(text):
    """
    Memprediksi sentimen dari satu string teks.
    """
    # Pastikan model dimuat secara lazy jika belum
    if model is None or tokenizer is None:
        load_model()
    if not model or not tokenizer:
        print("Model or tokenizer is not loaded. Cannot predict.")
        return "Error: Model not loaded."
        
    try:
        # Ubah input menjadi string jika bukan (penting untuk data dari file)
        text = str(text)
        
        # Tokenisasi teks
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        
        # Dapatkan prediksi model
        with torch.no_grad(): # Nonaktifkan perhitungan gradien untuk inferensi
            outputs = model(**inputs)
        
        # Dapatkan probabilitas (logits) dan cari ID kelas dengan prob tertinggi
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
        
        # Petakan ID ke label yang sesuai
        return labels[predicted_class_id]

    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error: Prediction failed."

# --- Bagian 2: Analisis File ---

def analyze_sentiment_from_file(file_path, text_column_name):
    """
    Membaca file (CSV atau XLSX), menerapkan prediksi sentimen ke kolom yang ditentukan.
    """
    try:
        # Baca file berdasarkan ekstensinya
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return None, "Error: Unsupported file format."

        # Cek apakah kolom yang diminta ada di DataFrame
        if text_column_name not in df.columns:
            return None, f"Error: Column '{text_column_name}' not found in the file."
            
        # Pastikan kolom teks adalah string (untuk menghindari error .apply())
        df[text_column_name] = df[text_column_name].astype(str)

        # Terapkan fungsi prediksi sentimen ke kolom yang ditentukan
        # Membuat kolom baru 'Sentiment_Prediction'
        df['Sentiment_Prediction'] = df[text_column_name].apply(predict_sentiment)

        return df, None # Kembalikan DataFrame dan tidak ada error

    except FileNotFoundError:
        return None, "Error: File not found."
    except Exception as e:
        print(f"Error processing file: {e}")
        return None, "Error: Could not process the file."

# --- Bagian 3: Visualisasi (DIPERBARUI) ---

def get_sentiment_counts(df, sentiment_column='Sentiment_Prediction'):
    """
    Menghitung jumlah sentimen dan mengembalikannya sebagai kamus (dictionary).
    Siap untuk digunakan oleh Chart.js.
    """
    if sentiment_column not in df.columns:
        print(f"Error: Sentiment column '{sentiment_column}' not found.")
        return {}
    
    sentiment_counts = df[sentiment_column].value_counts()
    
    # Pastikan semua label ada, bahkan jika jumlahnya 0
    all_labels = ['Positif', 'Netral', 'Negatif']
    for label in all_labels:
        if label not in sentiment_counts:
            sentiment_counts[label] = 0
            
    # Mengembalikan sebagai kamus standar
    return sentiment_counts.to_dict()

def generate_wordcloud_base64(df, text_column_name):
    """
    Menghasilkan Word Cloud dari kolom teks dan mengembalikannya sebagai string base64.
    """
    wordcloud_base64 = None
    try:
        if text_column_name in df.columns:
            # Gabungkan semua teks menjadi satu string besar
            text = " ".join(review for review in df[text_column_name].astype(str))

            # Tambahkan stopwords dasar bahasa Indonesia
            stopwords_indonesia = set(STOPWORDS)
            stopwords_indonesia.update([
                'yg', 'dg', 'rt', 'dgn', 'ny', 'd', 'k', 'ke', 'di', 'dari', 'dan', 'ini', 'itu',
                'atau', 'pada', 'untuk', 'juga', 'dengan', 'yang', 'ke', 'ya', 'ga', 'gak', 'tidak',
                'ada', 'adalah', 'saya', 'dia', 'kamu', 'kita', 'mereka', 'saja', 'seperti',
                'telah', 'akan', 'tapi', 'namun', 'karena', 'oleh', 'saat', 'sebagai', 'bahwa'
            ])
            
            # Bersihkan teks (opsional, tapi disarankan)
            text = re.sub(r'http\S+', '', text) # Hapus URL
            text = re.sub(r'[^a-zA-Z\s]', '', text.lower()) # Hapus non-alfabet

            # Buat Word Cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                stopwords=stopwords_indonesia,
                min_font_size=10,
                colormap='viridis' # Ganti palet warna
            ).generate(text)

            # Simpan ke buffer
            buf_wc = io.BytesIO()
            wordcloud.to_image().save(buf_wc, format='PNG')
            buf_wc.seek(0)
            wordcloud_base64 = base64.b64encode(buf_wc.getvalue()).decode('utf-8')
            plt.close()
            
    except Exception as e:
        print(f"Error creating word cloud: {e}")
        wordcloud_base64 = None

    return wordcloud_base64