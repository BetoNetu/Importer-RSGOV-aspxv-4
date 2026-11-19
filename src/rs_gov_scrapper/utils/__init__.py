import re

from rs_gov_scrapper.defaults import LOGDIR


def clear_logs() -> None:
    count=0
    for file in LOGDIR.iterdir():
        name, ext = str(file).split(".")
        if ext =="txt" and re.search("log", name):
            file.unlink()
            count+=1
    print(f"{count} arquivos de log excluídos de {LOGDIR}")