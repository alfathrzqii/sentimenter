from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from model import predict_sentiment, analyze_sentiment_from_file, get_sentiment_counts, generate_wordcloud_base64
import os
import uuid
import time
from werkzeug.utils import secure_filename

# Konfigurasi folder upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'gantidenganyangaman' 

# Pastikan folder upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Memeriksa apakah ekstensi file diizinkan."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files(folder, max_age_seconds=3600):
    """Menghapus file yang lebih tua dari batas waktu tertentu."""
    try:
        now = time.time()
        for f in os.listdir(folder):
            f_path = os.path.join(folder, f)
            if os.path.isfile(f_path) and os.stat(f_path).st_mtime < now - max_age_seconds:
                os.remove(f_path)
    except Exception as e:
        print(f"Error during cleanup: {e}")

@app.route('/')
def home():
    """Merender halaman home."""
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    """
    Merender halaman dashboard dengan data visualisasi IKN dan Whoosh.
    """
    # Data Hardcoded sesuai permintaan
    dashboard_data = {
        'ikn': {
            'title': 'Sentimen Masyarakat terhadap IKN',
            'counts': {'Positif': 633, 'Netral': 387, 'Negatif': 452},
            'image': 'ikn.png' # Pastikan file ini ada di static/images/
        },
        'whoosh': {
            'title': 'Sentimen Masyarakat terhadap Whoosh',
            'counts': {'Positif': 1122, 'Netral': 4270, 'Negatif': 2108},
            'image': 'whoosh.png' # Pastikan file ini ada di static/images/
        }
    }
    
    return render_template('dashboard.html', dashboard_data=dashboard_data)

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    """
    Merender halaman analisis. Menangani analisis teks tunggal DAN upload file.
    """
    prediction_result = None
    input_text = "" 
    results_table = None
    wordcloud = None 
    sentiment_counts = None 
    csv_file = None
    xlsx_file = None

    if request.method == 'POST':
        if 'text_input' in request.form:
            input_text = request.form.get('text_input', '')
            if input_text:
                prediction_result = predict_sentiment(input_text)
        
        elif 'file' in request.files:
            # Jalankan cleanup sebelum proses baru
            cleanup_old_files(app.config['UPLOAD_FOLDER'])

            file = request.files['file']
            text_column = request.form.get('text_column')

            if file.filename == '':
                flash('Tidak ada file yang dipilih', 'danger')
                return redirect(url_for('analysis'))
            
            if not text_column:
                flash('Nama kolom teks tidak boleh kosong', 'danger')
                return redirect(url_for('analysis'))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                df, error = analyze_sentiment_from_file(file_path, text_column)

                if error:
                    flash(error, 'danger')
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return redirect(url_for('analysis'))

                sentiment_counts = get_sentiment_counts(df)
                wordcloud = generate_wordcloud_base64(df, text_column)
                results_table = df.to_html(classes='table table-striped table-hover', index=False, border=0)

                # Simpan hasil ke file untuk diunduh
                analysis_id = uuid.uuid4().hex
                csv_file = f"results_{analysis_id}.csv"
                xlsx_file = f"results_{analysis_id}.xlsx"

                df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], csv_file), index=False)
                df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], xlsx_file), index=False)

                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                flash('Format file tidak diizinkan. Gunakan .csv atau .xlsx', 'danger')
                return redirect(url_for('analysis'))
            
    return render_template('analysis.html', 
                           prediction=prediction_result, 
                           text=input_text,
                           sentiment_counts=sentiment_counts, 
                           results_table=results_table,
                           wordcloud=wordcloud,
                           csv_file=csv_file,
                           xlsx_file=xlsx_file)

@app.route('/download/<filename>')
def download_file(filename):
    """Mengizinkan user mendownload file hasil analisis dengan aman."""
    # Mencegah directory traversal
    filename = secure_filename(filename)
    file_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Validasi path agar tetap di dalam folder upload
    upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
    if not file_path.startswith(upload_dir) or not os.path.exists(file_path):
        flash('File tidak ditemukan atau akses dilarang.', 'danger')
        return redirect(url_for('analysis'))

    # Tentukan nama file download
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'csv'
    download_name = f"hasil_sentimen.{ext}"

    return send_file(file_path, as_attachment=True, download_name=download_name)

@app.route('/about')
def about():
    """Merender halaman about."""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)