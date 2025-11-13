# LLM4Trademark

**LLM4Trademark** is an intelligent system that leverages **Large Language Models (LLMs)** and **semantic similarity search** to assist in the classification of products and services according to the **Nice and Viena Classification** system, commonly used for **trademark registration**.

The project integrates **AI-based semantic search**, **syntactic similarity analysis**, and **document extraction tools** to simplify the process of mapping textual product descriptions to the correct trademark classes.

---

## Features

- **Semantic Classification:**  
  Automatically classifies textual descriptions into trademark classes using sentence embeddings from **All-MiniLM-L6-v2** model.
  
- **PDF to Excel Conversion:**  
  Extracts structured classification data from **Nice Classification PDF** using **Camelot** and **Pandas**, generating clean and searchable Excel sheet.

- **PDF Analysis**
  Extracts and cleans information directly from the **Viena classification PDF** using **Pandas**.

- **Dual-Mode Similarity:**  
  Combines **semantic** (vector-based) and **syntactic** (text-based) similarity to increase accuracy in text–class associations ang generate classificatin lists **sorted by relevance**.

- **Executable Build:**  
  Converts Python scripts into standalone `.exe` files using **PyInstaller**, ensuring easy deployment without requiring a Python environment.

---

## Repository Structure

```
LLM4trademark/
│
├── models/
│ └── all-MiniLM-L6-v2/ # Pretrained embedding model used for semantic similarity
│
├── LLM4trademark_Nice.py # Main classification logic using Nice Classification data
├── LLM4trademark_Viena.py # Variant focusing on Vienna Classification (image-based brands)
│
├── build_exe.py # PyInstaller build script for creating executables
├── nice_pdf_to_excel.py # Converts Nice Classification PDF to clean Excel using Camelot & Pandas used inside LLM4trademark_Nice
│
├── cleaned_nice_doc.xlsx # Processed Excel version of the Nice Classification (result of the nice_pdf_to_excel.py)
├── Nice_classification.pdf # Nice Classification document
├── Viena_classification.pdf # Vienna Classification document (symbols & figurative elements)
├── requirements.txt # Dependencies used in the algorithms (install them before use)
│
└── results.txt (runtime) # Output file generated during program execution of any LLM4trademark algorithm
```

---

## Installation

### Clone the repository
```
bash
git clone https://github.com/thom01s/LLM4trademark.git
cd LLM4trademark
```

## Install dependencies

Create a virtual environment and install required packages:
```
pip install -r requirements.txt
```

## Usage

Run the main classifier.

For text classification using Nice Classification data:
```
python LLM4trademark_Nice.py
```

For Vienna classification (ìmage-based brands):
```
python LLM4trademark_Viena.py
```

Convert the official Nice PDF to Excel
```
python nice_pdf_to_excel.py
```
This will parse the official INPI (national institute of research and innovation) PDF and generate a structured Excel file (cleaned_nice_doc.xlsx).

Build standalone executables

You can package any of the scripts as an .exe for Windows (change the file and added data inside the algorithm):
```
python build_exe.py
```
The resulting file will appear in the dist/ folder.

## Example Workflow

-Extract Nice Classification data from PDF → Excel using nice_pdf_to_excel.py.

-Run LLM4trademark_Nice.py to embed and classify new product descriptions.

-Review generated results (resultados.txt) showing class predictions and similarity scores.

-(Optional) Package the program into a distributable .exe via build_exe.py.

## Output Example (Vienna classification) - Portuguese

```
Query: uma maçã mordida com folha no topo e uma cor sólida

Resultados com score <= 0.75:

--- Resultado 1 ---
Palavra da query: maçã
Score: 0.141
Classe: * 5.7.13
Texto: Maçãs

--- Resultado 2 ---
Palavra da query: folha
Score: 0.507
Classe: A 5.3.14
Texto: Uma folha

--- Resultado 3 ---
Palavra da query: folha topo
Score: 0.726
Classe: * 5.3.9
Texto: Folhas de nogueira-do-japão
```

Author

Thomas Sponchiado Pastore

Biomedical Engineer & AI Researcher

GitHub - https://github.com/thom01s
