# index/add_doc.py
import faiss, pickle
from sentence_transformers import SentenceTransformer

idx = faiss.read_index("ipc_faiss.index")
meta = pickle.load(open("metadata.pkl","rb"))
model = SentenceTransformer('all-MiniLM-L6-v2')

new_text = "Section 420... (or summary of case)"
vec = model.encode([new_text], normalize_embeddings=True)
idx.add(vec)
meta.append({"type":"statute","section_no":"420","text":new_text})
faiss.write_index(idx,"ipc_faiss.index")
pickle.dump(meta, open("metadata.pkl","wb"))
