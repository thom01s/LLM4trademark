timport re
import pandas as pd
from langchain_community.vectorstores import Chroma
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from nltk.corpus import stopwords
import nltk
from nltk.util import ngrams
import tkinter as tk
from tkinter import messagebox
import os
import sys
from difflib import SequenceMatcher

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

nltk.download('stopwords', quiet=True)

excel_path = resource_path("cleaned_nice_doc.xlsx")
df = pd.read_excel(excel_path)
df = df.rename(columns={
    "Nice Class": "class",
    "Português (Brasil)": "description"
})
df = df.dropna(subset=["description"]).drop_duplicates(subset=["description"])

chroma_client = chromadb.EphemeralClient()
embedding_model = HuggingFaceEmbeddings(model_name=resource_path("models/all-MiniLM-L6-v2")) # Model used to tokenize and search similarities

""" # Used to search within the whole description (below ia an implementation for each word of the description)
metadados = df[["classe", "descricao"]].to_dict(orient="records")

vectorstore = Chroma.from_texts(df["descricao"].tolist(), 
                                embedding_model, 
                                metadatas=metadados, 
                                client=chroma_client)
"""

stopwords_pt = set(stopwords.words('portuguese'))

def clean_text(text):
    words = [w.lower() for w in re.findall(r'\w+', text) if w.lower() not in stopwords_pt]
    bi_grams = [' '.join(b) for b in ngrams(words, 2)]
    tri_grams = [' '.join(b) for b in ngrams(words, 3)]
    return set(words + bi_grams + tri_grams)

text_expand = []
metadata_expand = []

for _, row in df.iterrows():
    words = clean_text(row["description"])
    for word in words:
        text_expand.append(word)
        metadados_expand.append({
            "class": row["class"],
            "original_desc": row["description"]
        })

vectorstore_palavras = Chroma.from_texts(
    text_expand,
    embedding_model,
    metadatas=metadata_expand,
    client=chroma_client
)

def sintax_similarity(word, text):
    return 1 - SequenceMatcher(None, word.lower(), word.lower()).ratio() # Sintatic similarity (used to diferentiate between same semantic classes (ex. noodle, ramen noodle, udon noodle - all same product (noodles), but with different words)

similarity = 0.2 # Can be adjusted to fit the task

def search_results(query):
    words = limpar_texto(query) 
    results_per_word = []

    for word in words:
        res_palavra = vectorstore_palavras.similarity_search_with_score(word, k=25) # Semantic search

        df_temp = pd.DataFrame([
            {
                "class": doc.metadata["class"],
                "text": doc.metadata["original_desc"],
                "semantic_score": score,
                "sintax_score": sintax_similarity(word, doc.metadata["original_desc"])
            }
            for doc, score in res_palavra if score <= similarity
        ])

        if not df_temp.empty:
            df_temp["score"] = df_temp[["semantic_score", "sintax_score"]].mean(axis=1)
            df_temp["query_word"] = word
            results_per_word.append(df_temp)

    if not results_per_word:
        return pd.DataFrame()

    df_cleaned = pd.concat(results_per_word, ignore_index=True)
    df_organized = df_cleaned.sort_values("score").drop_duplicates(subset="text")

    return df_organized

def execute_search():
    query = query_input.get("1.0", "end-1c").strip()
    if not query:
        messagebox.showwarning("Warning!", "Please, insert a product.")
        return

    results = search_results(query)

    output_path = os.path.join(os.path.dirname(sys.executable), "results.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Query: {query}\n\n\n")
        if not results.empty:
            f.write("Similar results:\n\n")
            for i, r in enumerate(results.to_dict(orient="records"), start=1):
                f.write(f"--- Result {i} ---\n")
                f.write(f"Query word: {r['query_word']}\n")
                f.write(f"Score: {r['score']:.3f}\n")
                f.write(f"Class: {r['class']}\n")
                f.write(f"Description: {r['text']}\n\n")
        else:
            f.write("There is no match for this description.\n")

    messagebox.showinfo("Sucess", "The file 'results.txt' was creates sucessfully!")
    input_query.delete("1.0", "end")

def close_program():
    if messagebox.askyesno("Exit", "Are you sure?"):
        window.destroy()
        sys.exit(0)

window = tk.Tk()
window.title("LLM4trademark - Nice")
window.geometry("500x300")
window.protocol("WM_DELETE_WINDOW", close_program)

label = tk.Label(window, text="Write the desired product type:", font=("Arial", 12))
label.pack(pady=10)

input_query = tk.Text(window, height=4, width=50, font=("Arial", 11))
input_query.pack(pady=5)

button = tk.Button(window, text="Search", command=execute_search,
                  font=("Arial", 12), bg="#0078D7", fg="white")
button.pack(pady=10)

exit_button = tk.Button(window, text="Exit", command=close_program,
                       font=("Arial", 11), bg="#D9534F", fg="white")
exit_button.pack(pady=5)

window.mainloop()


