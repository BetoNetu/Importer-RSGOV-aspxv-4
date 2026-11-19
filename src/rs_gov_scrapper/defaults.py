"""Itens exportáveis para mútliplos arquivos"""
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any
from zoneinfo import ZoneInfo

ROOT:Path=Path(__file__).parent.parent.parent
OUTPATH=ROOT/"download"
LOGDIR=ROOT/"log"
timestamp=datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H_%M_%S_%d_%m_%Y")
LOGFILE=LOGDIR/f"log_RsGovScrapper_{timestamp}.txt"
URLS:dict[str,str]={
    "Parcerias": "https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ParceriaFirmada-PESQUISAR_OUT.aspx",
    "Convênios": "https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ConvenioFirmado-PESQUISAR_OUT.aspx",
    
}   

def _create_log_file(LOGFILE=LOGFILE) -> Path:
    if not LOGFILE.exists():
        timestamp=datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S-%d/%m/%Y")
        LOGDIR.mkdir(exist_ok=True)
        with open(LOGFILE,"x") as x:
            x.write(dedent(f"""
            ================================
              Logs da raspagem do Poral de
              Convênios e Parcerias do RS
                    {timestamp}
            =================================
            """))
    print(f"Log inicializado em {LOGFILE}")
    return LOGFILE

def print_and_log(arg:Any,log_file=LOGFILE) -> None:
    """Escreve para stdout e para o arquivo de log"""
    timestamp=datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S-%d/%m/%Y")
    line_arg:str=dedent(f"{timestamp}: {arg}")    #print
    print(line_arg)
    with open(log_file,"a") as a:
        a.write(f"{line_arg}\n")
    
