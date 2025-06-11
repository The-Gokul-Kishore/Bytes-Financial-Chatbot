import pdfplumber
import boto3
import json
import re

def extract_text_and_kpis(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

    # Add Textract logic if needed for scanned documents

    # Dummy KPI extractor for now
    kpis = {
        "debt_to_equity": extract_numeric_value(text, "Debt to Equity"),
        "liquidity_ratio": extract_numeric_value(text, "Liquidity Ratio"),
        "sharpe_ratio": extract_numeric_value(text, "Sharpe Ratio")
        # Add more as needed
    }
    return {"text": text, "kpis": kpis}

def extract_numeric_value(text, keyword):
    match = re.search(rf"{keyword}.*?([-+]?\d*\.?\d+)", text, re.IGNORECASE)
    return float(match.group(1)) if match else None
