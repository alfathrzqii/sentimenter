from flask import Flask, render_template, request, url_for, flash, redirect
from model import predict_sentiment, analyze_sentiment_from_file, get_sentiment_counts, generate_wordcloud_base64
import os
from werkzeug.utils import secure_filename
import traceback
import logging

# Configure basic logging to file so we can capture tracebacks even if they don't print to the console
LOG_FILE = 'error.log'
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Konfigurasi folder upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'gantidenganyangaman' # Diperlukan untuk flash messages

# Pastikan folder upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Memeriksa apakah ekstensi file diizinkan."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Merender halaman home."""
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    """
    Merender halaman dashboard dengan konten dummy atau placeholder visualisasi.
    """
    # Placeholder data untuk contoh dummy grafik
    dummy_charts_data = {
        'kereta_cepat': {
            'bar': None, # Placeholder, bisa diganti gambar base64
            'pie': None, # Placeholder
            'title': 'Sentimen Mengenai Kereta Cepat'
        },
        'danantara': {
            'bar': None, # Placeholder
            'pie': None, # Placeholder
            'title': 'Sentimen Mengenai Danantara'
        },
        'purbaya': {
            'bar': None, # Placeholder
            'pie': None, # Placeholder
            'title': 'Sentimen Mengenai Menteri Keuangan Purbaya'
        }
    }
    
    return render_template('dashboard.html', dummy_charts=dummy_charts_data)

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    """
    Merender halaman analisis. Menangani analisis teks tunggal DAN upload file.
    """
    prediction_result = None
    input_text = "" 
    results_table = None
    wordcloud = None # Variabel untuk word cloud
    sentiment_counts = None # Mengganti bar_chart dan pie_chart

    if request.method == 'POST':
        try:
            # Cek apakah ini request analisis teks tunggal (ada 'text_input')
            if 'text_input' in request.form:
                input_text = request.form.get('text_input', '')
                if input_text:
                    prediction_result = predict_sentiment(input_text)
            
            # Cek apakah ini request upload file (ada 'file' di request.files)
            elif 'file' in request.files:
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

                    # Proses file
                    df, error = analyze_sentiment_from_file(file_path, text_column)

                    if error:
                        flash(error, 'danger')
                        os.remove(file_path) # Hapus file jika terjadi error
                        return redirect(url_for('analysis'))

                    # Panggil fungsi baru dari model.py
                    sentiment_counts = get_sentiment_counts(df)
                    wordcloud = generate_wordcloud_base64(df, text_column)
                    
                    # Buat tabel HTML dari DataFrame
                    results_table = df.to_html(classes='table table-striped table-hover', index=False, border=0)
                    
                    # Hapus file setelah diproses
                    os.remove(file_path)
                else:
                    flash('Format file tidak diizinkan. Gunakan .csv atau .xlsx', 'danger')
                    return redirect(url_for('analysis'))
        except Exception as e:
            # Tangkap dan log traceback untuk diagnosis; tampilkan pesan singkat ke user
            tb = traceback.format_exc()
            print(tb)
            flash('Terjadi kesalahan internal saat memproses permintaan. Detail: ' + str(e), 'danger')
            # Jangan expose full traceback ke user; cukup render halaman dengan flash
            return render_template('analysis.html', 
                                   prediction=prediction_result, 
                                   text=input_text,
                                   sentiment_counts=sentiment_counts,
                                   results_table=results_table,
                                   wordcloud=wordcloud)
            
    # Render template dengan semua variabel
    return render_template('analysis.html', 
                           prediction=prediction_result, 
                           text=input_text,
                           sentiment_counts=sentiment_counts, # Baru
                           results_table=results_table,
                           wordcloud=wordcloud)

@app.route('/about')
def about():
    """Merender halaman about."""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) # Aktifkan mode debug


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """
    Global exception handler: log full traceback to error.log and return a generic 500 page.
    This helps when the terminal does not show the traceback.
    """
    tb = traceback.format_exc()
    logging.error(tb)
    # Also attach to app.logger for completeness
    app.logger.error(tb)
    # Return a simple message (do not expose the full traceback in production)
    return render_template('analysis.html', prediction=None, text='', sentiment_counts=None, results_table=None, wordcloud=None), 500