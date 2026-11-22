#!./.venv/bin/python
"""## rs_gov_scrapper

Scripts em Python para coleta e extração de dados de um portal web legado e mal estruturado do Governo do RS, 
com o objetivo de automatizar a obtenção de informações que seriam trabalhosas de coletar manualmente.
"""
# -------------------------------------------------------------------------------------------------------------------
# Arquivo Principal: Faz a lógica inicial e chama a função extratora
# -------------------------------------------------------------------------------------------------------------------
import argparse
import re
import sys
import unicodedata
from time import sleep

from rs_gov_scrapper.defaults import LOGDIR, OUTPATH, print_and_log
from rs_gov_scrapper.scrapper import RSGovScrapper


def arguments() -> argparse.Namespace:
    """Coleta argumentos"""
    parser=argparse.ArgumentParser(
        prog="RSGovScrapperConvParc",
        description="Vai ao Portal de Convênios e Parceria e busca pelo URL informado",
        epilog="Caso não passe nenhuma opção você poderá informar os valores pelo terminal"
    )
    parser.add_argument('-A','--ano-inicial',default=2018,help="informa o ano de início da busca")
    parser.add_argument('-a','--ano-final',default=2025,help="informa o ano final da busca")
    parser.add_argument('-u','--url',help="url do formulário de busca")
    parser.add_argument('-o','--orgao',default="Secretaria da Educação",help="o orgão que deja pesquisar")
    parser.add_argument('-f','--arquivo',help="informa um arquivo de texto (.txt) com uma url por linha")
    
    args=parser.parse_args()
    if args.url is not None and args.arquivo is not None:
        print("-u e -f são mutualmente excludentes\nPor favor, escolha apenas 1")
        sys.exit(1)
    elif not all((
        isinstance(args.ano_inicial, int),
        isinstance(args.ano_final, int),
        isinstance(args.orgao, str),
        # A relação entre args.url e args.arquivo é de NAND
        # quando os tipos são corretos
        (
            (isinstance(args.url, str) and args.arquivo is None)
            or (isinstance(args.arquivo, str) and args.url is None)
            or(args.arquivo is None and args.url is None)
        ),
    )):
        print("Argumentos inválidos, por favor forneça valores com tipos válidos:\n-a|-A: número inteiro\n-o: nome completo do órgão\n-u: uma url\n-f: um caminho de arquivo válido")
        sys.exit(1)

    return args
    
def user_inputs(args:argparse.Namespace)->tuple[list[str],int,int,str]:
    print(args)
# Pegando inputs

# Url
    url:str|None=args.url
    file:str|None=args.arquivo
    if url is not str and file is None:
        url = input("Insira o URL do banco de dados URL: ")
    # Se um arquivo for informado arg.file deixa de ser None
    # logo ele vira str e entra nessa condição
    elif file and not url:
        try:
            with open(args.arquivo,"r") as f:
                data_url:list[str]=f.readlines()
            for i,v in enumerate(data_url):
                data_url[i]=v.strip()
        except FileNotFoundError as e:
            print(e)
            raise
    
    if url:
        data_url=[url]

    # Ano inicial
    start_year=args.ano_inicial
    if start_year <= 2000:
        start_year = int(input('Coloque o ano de início da busca: ').strip())
    
    #Ano Final
    end_year=args.ano_final
    if end_year <= 2000:
        end_year = int(input('Coloque o ano final da busca: ').strip())
    
    # Normalizando nome da secretaria/orgão
    want_name:str=args.orgao
    if not want_name:
        want_name:str= input("Qual órgão deseja pesquisar?")
    want_name_decomposed = unicodedata.normalize("NFD", want_name)
    want_name=re.sub(r"[\u0300-\u036f]", "", want_name_decomposed)
    want_name=want_name.upper()

    return data_url, start_year, end_year, want_name

def Processing()->tuple[str|None,str|None]:
    args=arguments()
    data_url, start_year, end_year, want_name= user_inputs(args)

    OUTPATH.mkdir(exist_ok=True)
    LOGDIR.mkdir(exist_ok=True)
    
    # range(i,j) = [i, i+1,i+2, ..., j-1]
    # ṕor isso  end_year+1
    years:range=range(start_year,(end_year+1),1)
    print(years)
    # Mandar fazer direto as urls
    for url in data_url:
        for each in years:
            # Sempre o double mode pois o outro campo de ano é só para liberar
            # o Campo dos órgãos. Além disso ele serve de "subfiltro", ele libera
            # apenas os órgãos que tem naquele ano (o que é honestamente um design 
            # pouco intuitivo). Sem contar o limite de 1000 entradas por chamada
            year0, year1 = each, each
            print_and_log("----------------------------------------------")
            print_and_log(f"---     Processando Ano: {each}         ---")
            print_and_log("----------------------------------------------")
            print_and_log(f"Órgão: {want_name}")
            s = RSGovScrapper()
            print(f"Passando {year0} e {year1} to scrapper")
            extraction_success, site_name, form_name = s.scrapper(want_name, year0, year1, url)

            if extraction_success is not True and len(years) > 1:
                print_and_log(f"Falha para o ano {each}, continuando para o próximo...")
            elif extraction_success is not True and len(years) < 1:
                print_and_log(f"Problemas com o ano {each}, recomenda-se revisão manual")    

            if len(years) > 1 and each != end_year:
                for idx in range(5): # Python é 0 indexed
                    print(f"\rAguardando por 5 segundos:{5-(idx+1):3d}",end="",flush=True); sleep(1)
                print_and_log("\n")
    return site_name, form_name

def main() -> None:
    try:
        site_name, form_name=Processing()
        print_and_log(f"Todos os anos processados para {site_name}.")
        print_and_log(f"Dados salvos em: {form_name}")
        print_and_log("Script terminou com successo.")
        input("Pressione Enter para sair...")
    except KeyboardInterrupt:
        print("\nCtrl+C pressionado, parando script")
        sys.exit(0)
    except Exception as e:
        print_and_log(e)
        raise

if __name__ == "__main__":
    main()