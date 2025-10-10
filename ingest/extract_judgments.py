# ingest/extract_judgments.py
import pdfplumber, re, json, os
from tqdm import tqdm

INPUT_DIR = r"C:\Users\Prithviraj\crminal-law-chatbot\data\judgements"
OUTPUT_FILE = r"C:\Users\Prithviraj\crminal-law-chatbot\data\judgements.json"

def extract_text(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

def find_sections(text):
    return list(set(re.findall(r"Section\s+(\d+)", text, re.I)))

def short_summary(text, max_chars=100000):
    # Simple heuristic: take first 1000 chars as excerpt — better: generate summary with LLM
    excerpt = text[:max_chars]
    return excerpt.replace("\n"," ")[:max_chars]

def main():
    items=[]
    for fname in tqdm(os.listdir(INPUT_DIR)):
        if not fname.lower().endswith(".pdf"): continue
        path=os.path.join(INPUT_DIR,fname)
        text = extract_text(path)
        sections = find_sections(text)
        summary = short_summary(text, max_chars=1200)
        items.append({
            "type":"case",
            "file":fname,
            "case_name": fname.replace(".pdf",""),
            "sections_cited": sections,
            "summary": summary,
            "full_text_path": path
        })
    with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
        json.dump(items,f,indent=2,ensure_ascii=False)
    print("Wrote", len(items))
if __name__=="__main__":
    main()