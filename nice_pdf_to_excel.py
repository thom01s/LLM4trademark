import camelot
import pandas as pd

arquivo = r"Nice_classification.pdf"

tables = camelot.read_pdf(arquivo, pages="all")

print(f"{tables.n} tables found.")

df = pd.concat([t.df for t in tables], ignore_index=True)

df = df.iloc[1:].reset_index(drop=True)

df.columns = df.iloc[0] 
df = df.iloc[1:].reset_index(drop=True)

df = df.drop(df.columns[[0, 2, 4]], axis=1)
df = df.replace(r'^\s*$', pd.NA, regex=True)
df = df.replace(['None', 'none', 'NaN', 'nan'], pd.NA)
df = df.dropna(axis=0, how='any')

print(df.head(30))

df.to_excel("cleaned_nice_doc(new).xlsx", index=False)
