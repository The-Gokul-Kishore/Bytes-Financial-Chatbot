import boto3
import json
from boto3.session import Session

def analyze_qualitative_risk(text):
    session = Session(profile_name="my-bytes")
    bedrock = session.client("bedrock-runtime", region_name="us-east-2")

    prompt = f"[INST] Analyze the following company report for risks:\n{text}\n\nList sentiment, compliance gaps, and cybersecurity concerns. [/INST]"

    body = {
        "prompt": prompt,
        "max_gen_len": 2048,   # Llama 3 expects `max_gen_len` instead of `max_tokens`
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = bedrock.invoke_model(
        modelId="meta.llama3-3-70b-instruct-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response['body'].read().decode())

    return result.get("generation", "No analysis available.")
