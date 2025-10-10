# index/build_index.py
import json, pickle, os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

DATA_FILES = [r"C:\Users\Prithviraj\crminal-law-chatbot\data\statutes.json",r"C:\Users\Prithviraj\crminal-law-chatbot\data\judgements.json"]
OUT_INDEX = "ipc_faiss.index"
OUT_META = "metadata.pkl"

def load_docs():
    docs=[]
    for p in DATA_FILES:
        if os.path.exists(p):
            docs.extend(json.load(open(p,encoding="utf-8")))
    return docs

def main():
    docs = load_docs()
    texts = []
    meta=[]
    for d in docs:
        if d['type']=="statute":
            texts.append(d['text'])
        else:
            # use summary + excerpt
            texts.append(d.get('summary') or d.get('text') or "")
        meta.append(d)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, OUT_INDEX)
    with open(OUT_META,"wb") as f:
        pickle.dump(meta, f)
    print("Index & metadata saved.")

if __name__=="__main__":
    main()