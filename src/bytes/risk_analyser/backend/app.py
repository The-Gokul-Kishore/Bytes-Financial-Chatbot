from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from bytes.risk_analyser.backend.risk_analysis.extractor import extract_text_and_kpis
from bytes.risk_analyser.backend.risk_analysis.analyzer import analyze_quantitative_risk
from bytes.risk_analyser.backend.risk_analysis.aws_bedrock_client import analyze_qualitative_risk
from bytes.risk_analyser.backend.risk_analysis.report_generator import generate_pdf_report

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        print("❌ No file received")
        return jsonify({'error': 'No file provided'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    print(f"✅ File saved at: {filepath}")

    try:
        print("🔍 Starting extraction")
        extracted_data = extract_text_and_kpis(filepath)

        print("📊 Starting quantitative analysis")
        quantitative = analyze_quantitative_risk(extracted_data['kpis'])

        # 3. Perform qualitative analysis using Bedrock LLM
        qualitative = analyze_qualitative_risk(extracted_data['text'])

        print("📝 Generating report")
        report_path = generate_pdf_report(filename, extracted_data, quantitative, qualitative)

        return send_file(report_path, as_attachment=True)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return jsonify({'error': str(e)}), 500

def run_backend(port=5000, reload=True):
    app.run(host="127.0.0.1", port=port)
if __name__ == '__main__':
    app.run(debug=True)
