#!./.venv/bin/python
"""## rs_gov_scrapper

Scripts em Python para coleta e extração de dados de um portal web legado e mal estruturado do Governo do RS, 
com o objetivo de automatizar a obtenção de informações que seriam trabalhosas de coletar manualmente.

---
#### To do

- Argparse + if not arg -> input
    - Arquivos
    - datas
    - url
"""
# -------------------------------------------------------------------------------------------------------------------
# Arquivo Principal: Faz a lógica inicial e chama a função extratora
# -------------------------------------------------------------------------------------------------------------------
import re
import sys
import unicodedata
from time import sleep

from rs_gov_scrapper.defaults import LOGDIR, OUTPATH, print_and_log
from rs_gov_scrapper.scrapper import RSGovScrapper


def Processing()->tuple[str|None,str|None]:
    OUTPATH.mkdir(exist_ok=True)
    LOGDIR.mkdir(exist_ok=True)
    
    # Pegando inputs
    data_url = input("Insira o URL do banco de dados URL: ")
    start_year = int(input('Coloque o ano de início da busca: ').strip())
    if start_year == 0 or start_year is None:
        start_year=2018 #My default
    end_year = int(input('Coloque o ano de início da busca: ').strip())
    if end_year == 0 or end_year is None:
        start_year=2025 #My default
    # Normalizando nome da secretaria/orgão
    want_name:str= input("Qual órgão deseja pesquisar?")
    if want_name is None or want_name == "":
       want_name="Secretaria da Educação"
    want_name_decomposed = unicodedata.normalize("NFD", want_name)
    want_name=re.sub(r"[\u0300-\u036f]", "", want_name_decomposed)
    want_name=want_name.upper()

    # range(i,j) = [i, i+1,i+2, ..., j-1]
    # ṕor isso  end_year+1
    modes:list[int]=[0,1]
    years:range=range(start_year,(end_year+1),1)
    # Mandar fazer direto os modosProcessing
    for mode in modes:
        for i in years:
                YearIO:int = i
                if mode == 1:
                    year0, year1 = YearIO, YearIO
                    mode="duplo"
                elif mode == 0:
                    year0, year1 = None, YearIO
                    mode="simples"
                print_and_log(f"Órgão {want_name}")
                print_and_log("----------------------------------------------")
                print_and_log(f"---     Processando Ano: {YearIO}-{mode} ---")
                print_and_log("----------------------------------------------")
                s = RSGovScrapper()
                extraction_success, site_name, form_name = s.scrapper(want_name, year0, year1, data_url)  # ty: ignore[not-iterable]
                if extraction_success != True and len(years) > 1:
                    print_and_log(f"Falha para o ano {YearIO}, continuando para o próximo ({years[i]})...")
                else:
                    print_and_log(f"Problemas com o ano {years[i]}, saindo..."); sys.exit(1)    
                if len(years) > 1:
                    for idx in range(5): # Python é 0 indexed
                        print(f"\rAguardando por 5 segundos:{5-(idx+1):3d}%",end="",flush=True); sleep(1)
                    print_and_log("\n")

    return site_name, form_name

def main() -> None:
    try:
        site_name, form_name=Processing()
        print_and_log(f"Todos os anos processados para {site_name}.")
        print_and_log(f"Dados salvos em: {form_name}")
        print_and_log("\nScript finished successfully.")
        input("Pressione Enter para sair...")
    except KeyboardInterrupt:
        print("Ctrl+C pressionado, parando script")
        sys.exit(0)
    except Exception as e:
        print_and_log(e)
        raise

if __name__ == "__main__":
    main()