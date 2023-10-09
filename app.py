import os
from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import pandas as pd
import tempfile
import plotly.express as px
import plotly.offline as pyo

app = Flask(__name__)
app.secret_key = 'your_generated_secret_key'
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['STATIC_FOLDER'] = 'static'
ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def dashboard():
    headings_source = []
    uploaded_data = None

    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
                data = pd.read_excel(file_path)
                headings = data.columns.tolist()

                if file == 'source_mix_data.xlsx':
                    headings_source = headings

                    # Filter out "GT Data" from the uploaded data
                    uploaded_data = data[data['Source Group'] != 'GT']

    # Plotly sunburst chart
    sunburst_chart = None  # Initialize as None

    if uploaded_data is not None:
        fig = px.sunburst(uploaded_data, path=["Source Group", "Source of Business", ], values="Total Revenue", color="Mix %")
        fig.update_traces(textinfo="label+value")  # Display values instead of percentages
        sunburst_chart = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    return render_template('dashboard.html', headings_source=headings_source, uploaded_data=uploaded_data, sunburst_chart=sunburst_chart)

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist("excel_files[]")

    if not uploaded_files:
        flash('No files were uploaded.', 'error')
        return redirect('/')

    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f"Uploaded file: {filename}", 'success')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
