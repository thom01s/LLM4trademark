import re
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

# === Carregar o Excel ===
excel_path = resource_path("class_marcas.xlsx")
df = pd.read_excel(excel_path)
df = df.rename(columns={
    "Nice Class": "classe",
    "Português (Brasil)": "descricao"
})

# === Garantir colunas padrão ===
df.columns = df.columns.str.strip().str.lower()
if "classe" not in df.columns or "descricao" not in df.columns:
    raise ValueError("O arquivo Excel deve conter as colunas 'classe' e 'descricao'.")

# === Limpeza e remoção de duplicatas ===
df = df.dropna(subset=["descricao"]).drop_duplicates(subset=["descricao"])

# === Inicializar cliente e embeddings ===
chroma_client = chromadb.EphemeralClient()
embedding_model = HuggingFaceEmbeddings(model_name=resource_path("models/all-MiniLM-L6-v2"))

"""
metadados = df[["classe", "descricao"]].to_dict(orient="records")

vectorstore = Chroma.from_texts(df["descricao"].tolist(), 
                                embedding_model, 
                                metadatas=metadados, 
                                client=chroma_client)
"""

stopwords_pt = set(stopwords.words('portuguese'))

# === Função auxiliar ===
def limpar_texto(texto):
    palavras = [w.lower() for w in re.findall(r'\w+', texto) if w.lower() not in stopwords_pt]
    bi_grams = [' '.join(b) for b in ngrams(palavras, 2)]
    tri_grams = [' '.join(b) for b in ngrams(palavras, 3)]
    return set(palavras + bi_grams + tri_grams)

textos_expand = []
metadados_expand = []

for _, row in df.iterrows():
    palavras = limpar_texto(row["descricao"])
    for termo in palavras:
        textos_expand.append(termo)
        metadados_expand.append({
            "classe": row["classe"],
            "descricao_original": row["descricao"]
        })

# === Cria o vetorstore com os termos individuais ===
vectorstore_palavras = Chroma.from_texts(
    textos_expand,
    embedding_model,
    metadatas=metadados_expand,
    client=chroma_client
)

from difflib import SequenceMatcher
import pandas as pd

def similaridade_sintatica(palavra, texto):
    return 1 - SequenceMatcher(None, palavra.lower(), texto.lower()).ratio()

similaridade = 0.2

def buscar_resultados(query):
    palavras = limpar_texto(query)  # <- faltava isso
    resultados_por_palavra = []     # <- deve ficar fora do loop

    for palavra in palavras:
        res_palavra = vectorstore_palavras.similarity_search_with_score(palavra, k=25)

        # Cria DataFrame com resultados filtrados e cálculo sintático
        df_temp = pd.DataFrame([
            {
                "classe": doc.metadata["classe"],
                "texto": doc.metadata["descricao_original"],
                "score_palavra": score,
                "score_sintaxe": similaridade_sintatica(palavra, doc.metadata["descricao_original"])
            }
            for doc, score in res_palavra if score <= similaridade
        ])

        if not df_temp.empty:
            # Média simples entre score semântico e sintático (quanto menor, melhor)
            df_temp["score"] = df_temp[["score_palavra", "score_sintaxe"]].mean(axis=1)
            df_temp["palavra_query"] = palavra
            resultados_por_palavra.append(df_temp)

    # Junta todos os resultados
    if not resultados_por_palavra:
        return pd.DataFrame()

    df_sem = pd.concat(resultados_por_palavra, ignore_index=True)
    df_sem = df_sem.sort_values("score").drop_duplicates(subset="texto")

    return df_sem

# === Função do botão ===
def executar_busca():
    query = entrada_query.get("1.0", "end-1c").strip()
    if not query:
        messagebox.showwarning("Aviso", "Por favor, insira um produto.")
        return

    resultados = buscar_resultados(query)

    # === Gera o arquivo de saída ===
    saida_path = os.path.join(os.path.dirname(sys.executable), "resultados.txt")
    with open(saida_path, "w", encoding="utf-8") as f:
        f.write(f"Query: {query}\n\n\n")
        if not resultados.empty:
            f.write("🔎 Resultados similares:\n\n")
            for i, r in enumerate(resultados.to_dict(orient="records"), start=1):
                f.write(f"--- Resultado {i} ---\n")
                f.write(f"Palavra da query: {r['palavra_query']}\n")
                f.write(f"Score: {r['score']:.3f}\n")
                f.write(f"Classe: {r['classe']}\n")
                f.write(f"Texto: {r['texto']}\n\n")
        else:
            f.write("Nenhum resultado encontrado.\n")

    messagebox.showinfo("Sucesso", "Arquivo 'resultados_classe.txt' gerado com sucesso!")
    entrada_query.delete("1.0", "end")

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

label = tk.Label(janela, text="Digite o tipo de produto desejado:", font=("Arial", 12))
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