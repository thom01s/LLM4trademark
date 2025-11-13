import subprocess
import sys
import os

def build_exe():
    script = "LLM4trademak_Nice.py" # Chose the file name
    
    add_data = [
        "class_marcas.xlsx;.",       #  Documents
        "models;models"      # Hugging Face models
    ]
    
    hidden_imports = [
        "chromadb.telemetry.product.posthog",
        "chromadb.api.rust",
        "tkinter",
        "tkinter.ttk",
        "torch",
        "transformers",
        "sentence_transformers.util"
    ]

    args = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--name=LLM_classificacao_classes",     # .exe name
    ]

    # Adiciona arquivos extras
    for item in add_data:
        args.append(f"--add-data={item}")

    # Adiciona imports ocultos
    for hi in hidden_imports:
        args.append(f"--hidden-import={hi}")
        
    args.append(script)

    print("\n=== Executing PyInstaller ===\n")
    print(" ".join(args))
    subprocess.run(args, check=True)
    print("\n .exe file writen with success!\n")

if __name__ == "__main__":

    build_exe()
