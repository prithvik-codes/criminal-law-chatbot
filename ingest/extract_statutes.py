# ingest/extract_statutes.py
import pdfplumber, re, json, os
INPUT_DIR = r"C:\Users\Prithviraj\crminal-law-chatbot\data\statutes"
OUTPUT_FILE = r"C:\Users\Prithviraj\crminal-law-chatbot\data\statutes.json"

def extract_pdf_text(path):
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)

def split_sections(text):
    # Very safe pattern to match Indian bare acts like "Section 378." or "378. Theft.—"
    pattern = re.compile(r'(Section\s+(\d+)[\.\s\-\—\–].?)(?=(?:\nSection\s+\d+)|\Z)', re.IGNORECASE|re.S)
    matches = pattern.finditer(text)
    out=[]
    for m in matches:
        header = m.group(1).strip()
        sec_no = re.search(r"Section\s+(\d+)", header, re.I).group(1)
        # full section text is header (we already included rest via non-greedy)
        out.append({"type":"statute","law":"IPC","section_no":sec_no,"text":header})
    # fallback: if regex found nothing, split on numbers lines
    if not out:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        # naive fallback (not perfect)
        out.append({"type":"statute","law":"IPC","section_no":"unknown","text":"\n".join(lines[:20000])})
    return out

def main():
    docs=[]
    for fname in os.listdir(INPUT_DIR):
        if fname.lower().endswith(".pdf"):
            path=os.path.join(INPUT_DIR,fname)
            txt = extract_pdf_text(path)
            docs.extend(split_sections(txt))
    with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
        json.dump(docs,f,indent=2,ensure_ascii=False)
    print(f"Saved {len(docs)} statute items to {OUTPUT_FILE}")

if __name__ =="__main__":
    main()


