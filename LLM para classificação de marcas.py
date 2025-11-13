import re
import pandas as pd
from langchain_community.vectorstores import Chroma
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from nltk.corpus import stopwords
import nltk
from nltk.util import ngrams
import tkinter as tk
from tkinter import messagebox
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

nltk.download('stopwords', quiet=True)

# === Carregar o PDF ===
pdf_path = resource_path("viena.pdf")
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# === Extrair texto por parágrafo ===
paragrafos = []
for doc in documents:
    for bloco in doc.page_content.split(" \n \n"):
        bloco = bloco.strip()
        if bloco:
            paragrafos.append(bloco)

# === Limpeza de texto ===
clean_paragrafos = []
for p in paragrafos:
    p = re.sub(r"[ \xa0]+", " ", p)
    p = re.sub(r"\s+", " ", p)
    clean_paragrafos.append(p.strip())

# === Regex para separar classe e descrição ===
pattern = re.compile(
    r"^(?P<classe>(?:\*?\s*A?\s*)?\d+(?:\.\d+){0,2})\s*-?\s*(?P<descricao>.+)",
    re.DOTALL
)

entries = []
for bloco in clean_paragrafos:
    match = pattern.match(bloco)
    if match:
        classe = match.group("classe").strip()
        descricao = match.group("descricao").strip()
        if (
            len(descricao) < 3
            or "CLASSIFICAÇÃO" in descricao.upper()
            or "EDIÇÃO" in descricao.upper()
            or "LISTA" in descricao.upper()
        ):
            continue
        entries.append({
            "classe": classe,
            "descricao": descricao,
            "linha_original": bloco
        })

chroma_client = chromadb.EphemeralClient()

# === DataFrame e vetor ===
df = pd.DataFrame(entries).drop_duplicates()
embedding_model = HuggingFaceEmbeddings(model_name=resource_path("models/all-MiniLM-L6-v2"))
metadados = df[["classe", "linha_original"]].to_dict(orient="records")

vectorstore = Chroma.from_texts(df["descricao"].tolist(), 
                                embedding_model, 
                                metadatas=metadados, 
                                client=chroma_client)

stopwords_pt = set(stopwords.words('portuguese'))

# === Função auxiliar ===
def limpar_texto(texto):
    palavras = [w.lower() for w in re.findall(r'\w+', texto) if w.lower() not in stopwords_pt]
    bi_grams = [' '.join(b) for b in ngrams(palavras, 2)]
    tri_grams = [' '.join(b) for b in ngrams(palavras, 3)]
    return set(palavras + bi_grams + tri_grams)

# === Função principal de busca ===
def buscar_resultados(query):
    palavras = limpar_texto(query)
    resultados_por_palavra = []
    similaridade = 0.75

    for palavra in palavras:
        res = vectorstore.similarity_search_with_score(palavra, k=25)
        for doc, score in res:
            if score <= similaridade:
                resultados_por_palavra.append({
                    "classe": doc.metadata['classe'],
                    "texto": doc.page_content.strip(),
                    "palavra_query": palavra,
                    "score": round(score, 3)
                })

    df_sem = pd.DataFrame(resultados_por_palavra)
    if df_sem.empty:
        return pd.DataFrame()
    df_sem = df_sem.sort_values('score').drop_duplicates(subset='texto')
    return df_sem

# === Função do botão ===
def executar_busca():
    query = entrada_query.get("1.0", "end-1c").strip()
    if not query:
        messagebox.showwarning("Aviso", "Por favor, digite uma query.")
        return

    resultados = buscar_resultados(query)

    # === Gera o arquivo de saída ===
    saida_dir = os.path.dirname(sys.executable)
    saida_path = os.path.join(saida_dir, "resultados.txt")
    with open(saida_path, "w", encoding="utf-8") as f:
        f.write(f"Query: {query}\n\n\n")
        if not resultados.empty:
            f.write("🔎 Resultados com score <= 0.75:\n\n")
            for i, r in enumerate(resultados.to_dict(orient="records"), start=1):
                f.write(f"--- Resultado {i} ---\n")
                f.write(f"Palavra da query: {r['palavra_query']}\n")
                f.write(f"Score: {r['score']:.3f}\n")
                f.write(f"Classe: {r['classe']}\n")
                f.write(f"Texto: {r['texto']}\n\n")
        else:
            f.write("Nenhum resultado encontrado.\n")

    messagebox.showinfo("Sucesso", "Arquivo 'resultados.txt' gerado com sucesso!")
    entrada_query.delete("1.0", "end")  # limpa o campo para nova consulta

# === Função para sair com segurança ===
def fechar_programa():
    if messagebox.askyesno("Sair", "Deseja realmente encerrar o programa?"):
        janela.destroy()
        sys.exit(0)

# === Interface Tkinter ===
janela = tk.Tk()
janela.title("Busca Inteligente")
janela.geometry("500x300")
janela.protocol("WM_DELETE_WINDOW", fechar_programa)

label = tk.Label(janela, text="Digite sua query:", font=("Arial", 12))
label.pack(pady=10)

entrada_query = tk.Text(janela, height=4, width=50, font=("Arial", 11))
entrada_query.pack(pady=5)

botao = tk.Button(janela, text="Buscar", command=executar_busca,
                  font=("Arial", 12), bg="#0078D7", fg="white")
botao.pack(pady=10)

botao_sair = tk.Button(janela, text="Sair", command=fechar_programa,
                       font=("Arial", 11), bg="#D9534F", fg="white")
botao_sair.pack(pady=5)

janela.mainloop()