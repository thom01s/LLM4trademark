import subprocess
import sys
import os

def build_exe():
    # Caminho do script principal
    script = "LLM para classificação de classes.py"

    # Arquivos e pastas a incluir no pacote
    add_data = [
        "class_marcas.xlsx;.",       # documentos
        "models;models"      # Pasta de modelos Hugging Face
    ]

    # Módulos que o PyInstaller pode não detectar automaticamente
    hidden_imports = [
        "chromadb.telemetry.product.posthog",
        "chromadb.api.rust",                   # Prevê erro comum
        "tkinter",
        "tkinter.ttk",
        "torch",
        "transformers",
        "sentence_transformers.util"
    ]

    # Argumentos básicos do PyInstaller
    args = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--clean",                             # Limpa build anterior
        "--name=LLM_classificacao_classes",     # Nome do .exe gerado
    ]

    # Adiciona arquivos extras
    for item in add_data:
        args.append(f"--add-data={item}")

    # Adiciona imports ocultos
    for hi in hidden_imports:
        args.append(f"--hidden-import={hi}")

    # Adiciona o script principal
    args.append(script)

    # Executa o PyInstaller
    print("\n=== Executando PyInstaller ===\n")
    print(" ".join(args))
    subprocess.run(args, check=True)
    print("\n✅ Empacotamento concluído com sucesso!\n")

if __name__ == "__main__":
    build_exe()