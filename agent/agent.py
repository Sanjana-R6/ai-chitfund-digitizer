import json
import re
import requests
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")
import easyocr

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
OCR_LANGS = ["en", "te"]
FOREMAN_COMMISSION_RATE = 0.05

_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(OCR_LANGS, gpu=False)
    return _reader

def run_ocr(image_path: str) -> str:
    reader = get_reader()
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)

EXTRACTION_PROMPT = """Extract chit fund information from the OCR text and return valid JSON only. No explanation, no markdown fences.

Fields:
- chit_value: total chit value in rupees (integer)
- num_members: number of members (integer)
- month_number: auction month number (integer)
- winning_bid: lowest bid amount in rupees (integer)
- member_name: name of prized member (string)
- monthly_sub: monthly subscription per member in rupees (integer)
- foreman_name: name of foreman (string)
- auction_date: date of auction (string)
- members: list of objects with name, amount_paid, month fields

If a field is not present, use null.

OCR TEXT:
{ocr_text}
"""

def run_llm_extraction(ocr_text: str) -> dict:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": EXTRACTION_PROMPT.format(ocr_text=ocr_text),
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        raw = response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return {"error": "Ollama not running. Run: ollama serve"}

    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_response": raw}

def calculate_chit_figures(data: dict) -> dict:
    chit_value = data.get("chit_value")
    winning_bid = data.get("winning_bid")
    num_members = data.get("num_members")
    monthly_sub = data.get("monthly_sub")

    if None in (chit_value, winning_bid, num_members):
        return data

    foreman_commission = round(winning_bid * FOREMAN_COMMISSION_RATE, 2)
    prized_amount = chit_value - winning_bid
    dividend_per_member = round((winning_bid - foreman_commission) / num_members, 2)

    result = {
        "foreman_commission": foreman_commission,
        "prized_amount": prized_amount,
        "dividend_per_member": dividend_per_member,
        "bid_loss": winning_bid
    }

    if monthly_sub:
        result["net_installment_per_member"] = round(monthly_sub - dividend_per_member, 2)

    return {**data, **result}

def process_image(image_path: str) -> dict:
    if not Path(image_path).exists():
        raise FileNotFoundError(image_path)
    ocr_text = run_ocr(image_path)
    structured = run_llm_extraction(ocr_text)
    return calculate_chit_figures(structured)

if __name__ == "__main__":
    import sys, pprint
    if len(sys.argv) < 2:
        print("Usage: python agent/agent.py <image_path>")
        sys.exit(1)
    output = process_image(sys.argv[1])
    pprint.pprint(output, sort_dicts=False)