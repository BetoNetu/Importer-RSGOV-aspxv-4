"""Itens exportáveis para mútliplos arquivos"""
from pathlib import Path

ROOT:Path=Path(__file__).parent.parent.parent
OUTPATH=ROOT/"download"

if __name__ == "__main__":
    (OUTPATH/"teste").mkdir(exist_ok=True)