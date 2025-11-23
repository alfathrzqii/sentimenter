from flask import Flask, render_template, request, url_for, flash, redirect
from model import predict_sentiment, analyze_sentiment_from_file, get_sentiment_counts, generate_wordcloud_base64
import os
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

    if request.method == 'POST':
        if 'text_input' in request.form:
            input_text = request.form.get('text_input', '')
            if input_text:
                prediction_result = predict_sentiment(input_text)
        
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

                df, error = analyze_sentiment_from_file(file_path, text_column)

                if error:
                    flash(error, 'danger')
                    os.remove(file_path) 
                    return redirect(url_for('analysis'))

                sentiment_counts = get_sentiment_counts(df)
                wordcloud = generate_wordcloud_base64(df, text_column)
                results_table = df.to_html(classes='table table-striped table-hover', index=False, border=0)
                os.remove(file_path)
            else:
                flash('Format file tidak diizinkan. Gunakan .csv atau .xlsx', 'danger')
                return redirect(url_for('analysis'))
            
    return render_template('analysis.html', 
                           prediction=prediction_result, 
                           text=input_text,
                           sentiment_counts=sentiment_counts, 
                           results_table=results_table,
                           wordcloud=wordcloud)

@app.route('/about')
def about():
    """Merender halaman about."""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)