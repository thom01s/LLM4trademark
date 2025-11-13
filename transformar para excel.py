import camelot
import pandas as pd

# Caminho do arquivo PDF
arquivo = r"C:/Users/ThomasSponchiadoPast/Downloads/projetos/LLM_para_classificação_de_marcas/PortalINPI_NCL122024ENPTBR_20240101cPB.pdf"

# Extrai todas as tabelas do PDF (tenta detectar linhas da tabela automaticamente)
tabelas = camelot.read_pdf(arquivo, pages="all")

# Mostra quantas tabelas foram encontradas
print(f"{tabelas.n} tabelas encontradas.")

df = pd.concat([t.df for t in tabelas], ignore_index=True)

df = df.iloc[1:].reset_index(drop=True)

df.columns = df.iloc[0] 
df = df.iloc[1:].reset_index(drop=True)

df = df.drop(df.columns[[0, 2, 4]], axis=1)
df = df.replace(r'^\s*$', pd.NA, regex=True)
df = df.replace(['None', 'none', 'NaN', 'nan'], pd.NA)
df = df.dropna(axis=0, how='any')

print(df.head(30))

# (opcional) salvar em Excel
df.to_excel("teste.xlsx", index=False)