#!./.venv/bin/python
"""## rs_gov_scrapper
Scripts em Python para coleta e extração de dados de um portal web legado e mal estruturado do Governo do RS, 
com o objetivo de automatizar a obtenção de informações que seriam trabalhosas de coletar manualmente."""
# -------------------------------------------------------------------------------------------------------------------
# Arquivo Principal: Faz a lógica inicial e chama a função extratora
# -------------------------------------------------------------------------------------------------------------------
from time import sleep

from rs_gov_scrapper.defaults import OUTPATH
from rs_gov_scrapper.scrapper import RSGovScrapper


def Processing()->tuple[str|None,str|None]:
    OUTPATH.mkdir(exist_ok=True)
    data_url = input("Enter the database's URL: ")
    start_year = int(input('Coloque o ano de início da busca: ').strip())
    if start_year == 0:
        start_year=2018 #My default
    end_year = int(input('Coloque o ano de início da busca: ').strip())
    if end_year == 1:
        start_year=2025 #My default
    # range(i,j) = [i, i+1,i+2, ..., j-1]
    # ṕor isso  end_year+1
    modes:list[int]=[0,1]
    years:range=range(start_year,(end_year+1),1)
    # Mandar fazer direto os modos
    for mode in modes:
        for i in years:
                YearIO:int = i
                if mode == 1:
                    year0, year1 = YearIO, YearIO
                    mode="duplo"
                elif mode == 0:
                    year0, year1 = None, YearIO
                    mode="simples"
                print(f"\n--- Processando Ano: {YearIO}-{mode} ---")
                s = RSGovScrapper()
                extraction_success, site_name, form_name = s.scrapper(year0, year1, data_url)
                if extraction_success != True:
                    print(f"Falha para o ano {YearIO}, continuando para o próximo ({years[i]})...")
                for i in range(5): # Python é 0 indexed
                    print(f"\rAguardando por 5 segundos:{5-(i+1):3d}%",end="",flush=True); sleep(1)
                print()

    return site_name, form_name

def main() -> None:
    site_name, form_name=Processing()
    print(f"\nAll years processed for {site_name}.")
    print(f"Data saved in: {form_name}")
    print("\nScript finished successfully.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()