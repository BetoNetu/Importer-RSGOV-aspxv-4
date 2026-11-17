"""Itens exportáveis para mútliplos arquivos"""
from datetime import datetime
from pathlib import Path
from time import strftime
from typing import Any
from zoneinfo import ZoneInfo

ROOT:Path=Path(__file__).parent.parent.parent
OUTPATH=ROOT/"download"
LOGDIR=ROOT/"log"
timestamp=datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y, %H:%M:%S")
LOGFILE=LOGDIR/f"log_RsGovScrapper_{timestamp}.txt"

def create_log_file():
    if not LOGFILE.exists():
        with open(LOGFILE,"w") as w:
            w.write(f"""
            ================================
              Logs da raspagem do Poral de
              Convênios e Parcerias do RS
            {timestamp}
            =================================
            """)
    print(f"Log inicializado em {LOGFILE}")
    return LOGFILE

def prind_and_log(arg:Any,LOGFILE):
    """Escreve para stdout e para o arquivo de log"""
    timestamp=datetime.now(ZoneInfo("America/Sao_Paulo")),strftime("%H:%M:%S,%d/%m/%Y")
    line_arg:str=f"{timestamp}: {arg}"
    

    #print
    print(line_arg)
