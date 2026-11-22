"""### Scrapper:
1. Vai ao site informado; 
2. Procura por elementos específicos da na página html;
3. Faz a busca a partir de critérios definidos (realizando as buscas em modo simples e duplo);
4. Salva os dados em CSV.
---
#### Implementado

- [Portal de Parcerias](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ParceriaFirmada-PESQUISAR_OUT.aspx)
- [Portal de Convênios](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ConvenioFirmado-PESQUISAR_OUT.aspx)
---
#### To-do

- [Editais de Chamamento](https://portalfpe.sefaz.rs.gov.br/sefaconv/apl/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PortalEditalConvenio-PESQUISAR_OUT.aspx)
- [Dispenda de Eligibilidade Feio   >= 2025](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PORTALPUBLICACAOCONVENIO-Pesquisar_Out.aspx?chave=1) 
- [Intenção de Recisão](https://www.convenioseparcerias.rs.gov.br/intencoes-de-rescisao-dos-termos-de-colaboracao-e-de-fomento)
- [Manifestação de Interesse](https://portalfpe.sefaz.rs.gov.br/sefaconv/apl/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PortalMisConvenio-Pesquisar_Out.aspx)
- [Dispenda de Eligibilidade Bonito <  2025](https://www.convenioseparcerias.rs.gov.br/dispensas-e-inexigibilidades) - Será um parto
"""
import csv
import sys
from textwrap import dedent
from time import sleep
from typing import Any

import pandas as pd
import selenium.webdriver.remote.errorhandler as sel_error
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

#from selenium.webdriver.firefox import options as Options
#from selenium.webdriver.firefox import service as Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from rs_gov_scrapper.defaults import OUTPATH, URLS, print_and_log


class RSGovScrapper:
    """### Scrapper:
    1. Vai ao site informado; 
    2. Procura por elementos específicos da na página html;
    3. Faz a busca a partir de critérios definidos (realizando as buscas em modo simples e duplo);
    4. Salva os dados em CSV.
    ---
    #### Implementado

    - [Portal de Parcerias](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ParceriaFirmada-PESQUISAR_OUT.aspx)
    - [Portal de Convênios](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ConvenioFirmado-PESQUISAR_OUT.aspx)
    ---
    #### To-do

    - [Editais de Chamamento](https://portalfpe.sefaz.rs.gov.br/sefaconv/apl/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PortalEditalConvenio-PESQUISAR_OUT.aspx)
    - [Dispenda de Eligibilidade Feio   >= 2025](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PORTALPUBLICACAOCONVENIO-Pesquisar_Out.aspx?chave=1) 
    - [Intenção de Recisão](https://www.convenioseparcerias.rs.gov.br/intencoes-de-rescisao-dos-termos-de-colaboracao-e-de-fomento)
    - [Manifestação de Interesse](https://portalfpe.sefaz.rs.gov.br/sefaconv/apl/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PortalMisConvenio-Pesquisar_Out.aspx)
    - [Dispenda de Eligibilidade Bonito <  2025](https://www.convenioseparcerias.rs.gov.br/dispensas-e-inexigibilidades) - Será um parto
    """
    # Inicialização da classe
    def __init__(self, headless: bool = False)->None:
        """Inicia o navegador e variáveis importantes"""
        print_and_log("Inicializando scrapper")
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 30) # TimeOut Generoso
        self.iter = 0
        self.sel_errors_and_others:tuple=(
            #Selenium Exceptions
            sel_error.DetachedShadowRootException,
            sel_error.ElementClickInterceptedException,
            sel_error.ElementNotInteractableException,
            sel_error.ElementNotSelectableException,
            sel_error.ElementNotVisibleException,
            sel_error.ImeActivationFailedException,
            sel_error.ImeNotAvailableException,
            sel_error.InsecureCertificateException,
            sel_error.InvalidArgumentException,
            sel_error.InvalidCookieDomainException,
            sel_error.InvalidCoordinatesException,
            sel_error.InvalidElementStateException,
            sel_error.InvalidSelectorException,
            sel_error.InvalidArgumentException,
            sel_error.JavascriptException,
            sel_error.MoveTargetOutOfBoundsException,
            sel_error.NoAlertPresentException,
            sel_error.NoSuchCookieException,
            sel_error.NoSuchElementException,
            sel_error.NoSuchFrameException,
            sel_error.NoSuchShadowRootException,
            sel_error.NoSuchWindowException,
            sel_error.ScreenshotException,
            sel_error.SessionNotCreatedException,
            sel_error.StaleElementReferenceException,
            sel_error.TimeoutException,
            sel_error.UnableToSetCookieException,
            sel_error.UnexpectedAlertPresentException,
            sel_error.UnknownMethodException,
            sel_error.WebDriverException,
            #stdlib Exceptisons
            TypeError,
            SyntaxError,
            IndexError,
        )
    @staticmethod
    def orgao_populado(driver:WebDriver)->int|bool:
        """Aguarda o f_CodOrgao option ser atualizado"""
        try:
            opcoes = driver.find_elements(By.CSS_SELECTOR, "#f_CodOrgao option")
            return len(opcoes) > 1   # "blank" + pelo menos uma real
        except sel_error.StaleElementReferenceException:
            return False  # se o DOM foi substituído, tenta de novo
    
    def _waiter(self, EC_name:str,locator:tuple|WebElement) -> bool:
        """Lida com as opções de espera"""
        for i in range(3):
            try:
                match EC_name:
                    case "presence_of_element_located":
                        EC_var=EC.presence_of_element_located(locator)            # ty: ignore[invalid-argument-type]
                        WebDriverWait(self.driver,10).until(EC_var)
                    case "presence_of_all_elements_located":
                        EC_var=EC.presence_of_all_elements_located(locator) # ty: ignore[invalid-argument-type]
                        WebDriverWait(self.driver, 10).until(EC_var)
                    case "element_to_be_clickable":
                        EC_var=EC.element_to_be_clickable(locator)
                        WebDriverWait(self.driver,10).until(EC_var)
                    case "orgao_populado":
                        WebDriverWait(self.driver,10).until(RSGovScrapper.orgao_populado)

                    case _:
                        raise ValueError(f"EC_name desconhecido: {EC_name}")
                return True
            except self.sel_errors_and_others:
                if i == 2:
                    raise
                sleep(0.2)
        return False

    def _finder(self, locator:tuple[Any,Any]|WebElement, plural:bool=False) -> WebElement | list[WebElement]:
        """Lida com a localização de elementos. Busca e retorna o objeto.
        Implementa driver.find_element() e driver.find_elements() de modo chamável"""
        print_and_log(f"Localizando elemento: {locator}")
        for i in range(3):
            if not isinstance(locator,tuple):
                locator:tuple[Any]=(locator,)
            try:
                if plural != True:
                    elemento:WebElement = self.driver.find_element(*locator)
                else:
                    elemento:list[WebElement] = self.driver.find_elements(*locator)
                break
            except self.sel_errors_and_others:
                if i == 2:
                    raise    
                sleep(0.2)
        if elemento is not None:
            print_and_log(f"Elemento(s) {locator}, localizado(s)")
            #print_and_log(elemento)
            return elemento
        else:
            print_and_log(f"Elemento {locator} não localizado")
            return elemento
    
# Interação com elementos já localizados
    def extract_pipeline(
        self,
        primary_element:WebElement,
        ) -> list[dict[str,str|None]]|None:
        """Lida com a extração dos dados do site para um csv"""
    #Headers da tabela de Resultados
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))  
            # Espera os elementos estarem presentes
            result_table = primary_element.find_element(By.TAG_NAME, "table")

            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "thead")))  
            # Espera os headers da tabela estarem presentes
            thead = result_table.find_element(By.TAG_NAME, "thead")

            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))  
            # Espera que a linha dos headers da tabela estejam presentes
            header_row = thead.find_element(By.TAG_NAME, "tr")

            # Condensa os headers em uma lista
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "th")))
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            headers = [cell.text.strip() for cell in header_cells]
            print_and_log(f"{len(headers)} headers encontrados: {headers}")
        except self.sel_errors_and_others as e:
            print_and_log(f"Erro ao encontrar os resultados do container de dados: {e}")
            self.driver.quit()
            return None

    # Dados
        rows_data = []
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tbody")))
            print() 
            # Espera pelo corpo da tabela
            tbody = result_table.find_element(By.TAG_NAME, "tbody")
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))  
            data_rows = tbody.find_elements(By.TAG_NAME, "tr")
            for row in data_rows:
                self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))  
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                row_dict = {}
                for i, cell in enumerate(cells):
                    col_name = headers[i] if i < len(headers) else f"col_{i}"
                    row_dict[col_name] = cell.text.strip()
                links = row.find_elements(By.TAG_NAME, "a")
                row_dict["Hyperlink"] = links[0].get_attribute("href") if links else ""
                rows_data.append(row_dict)
            return rows_data
        except self.sel_errors_and_others as e:
            print(e)
            return None

    def _element_inetraction(
        self,
        elemento:WebElement|list[WebElement],
        action:str|None,
        select_value:str|int=""
        ) -> bool|Select|WebElement|list[WebElement]|None:

        """Uma pipeline condensada para operar o navegador e a página (busca de elementos html)"""
        for i in range(3):
            try:
                match action:
                    case "select_by_visible_text":
                        select_elemento=Select(elemento)  # ty: ignore[invalid-argument-type]
                        select_elemento.select_by_visible_text(select_value)  # ty: ignore[invalid-argument-type]
                    case "select_by_index":
                        select_elemento=Select(elemento) # ty: ignore[invalid-argument-type]
                        select_elemento.select_by_index(select_value)  # ty: ignore[invalid-argument-type]
                    case "click":         # O list_elements nunca chegará em click, tenho que agarntir isso
                        elemento.click()  # ty: ignore[unresolved-attribute] 
                    case "switch":
                        # Todos os portais tem frame zero, qualquer coisa só adicionar um parâmetro e mudar
                        self.driver.switch_to.frame(0)
                    case None:
                        return elemento
                    case _:
                        raise ValueError(f"ação desconhecida: {action}")
                return True
            except self.sel_errors_and_others:
                if i == 2:
                    raise
        return False
        
    
    def element_pipeline(
        self,
        EC_name:str,
        locator:tuple|WebElement,
        action:str|None,
        finder_plural:bool=False,
        select_value:str|int="",
    ) -> bool | WebElement | list[WebElement] | Select |None:
        """Lógica padronizada para lidar com os elementos"""
        try:
            if self._waiter(EC_name,locator):
                elemento=self._finder(locator,finder_plural)
                elemento=self._element_inetraction(elemento,action,select_value)
                return elemento
                # O elemento de _element_interaction deve ser
                # imediatamente retornado para evitar que saia
                # do escopo da função
        except self.sel_errors_and_others as e:
            print_and_log(f"{e}")
            print_and_log(dedent(f"""
            Pipeline do elemento {locator if locator else "None"} falhou.
            Dados da Chamada:
            elemento: {"None" if elemento is None else elemento}
            
            EC_name:{EC_name}
            action:{action if type(action) is str else "None"}
            finder_plural:{finder_plural}
            """))
            self.driver.quit()
            print_and_log("Saindo")
            sys.exit(1)

#Função condicional dos elementos de cada um
    def campos(self, data_url:str, URLS:dict[str,str]=URLS) -> tuple[str,str]:
        """Filtra os nomes dos campos com base na URL"""
        print_and_log("Definindo nome dos elementos com base na URL do Portal")
        key = next((k for k, v in URLS.items() if v == data_url), None)
        match key:
            case "Parcerias":
                name_ano_dropdown_1=(By.ID,"f_Ex") # esse é o que muda de nome
            case "Convênios":
                name_ano_dropdown_1=(By.ID,"f_CodExercicio")
        print_and_log(f"Selecionado: Portal de {key}")
        print_and_log(f"Url: {data_url}")
        print_and_log("Primeiro dropdown campo: \"_CodExercicioConvenio\"")
        print_and_log(f"Segundo dropdown campo: \"{name_ano_dropdown_1}\"")
        return name_ano_dropdown_1

    #parcerias = f_ex
    #convênio = f_CodExercicio

# Função Extratora
    def scrapper(self, want_name:str, year0:int|None, year1:int, data_url:str) -> tuple[bool,str|None,str|None]:
        """Função Extratora. Controla o navegador, vai ao site, executa a busca e salva os dados em CSV"""
        # Garante que o primeiro só abre uma janela
        if self.iter > 0:
            print_and_log("(Re)inicializando scrapper")
            self.__init__()
        self.iter = min(self.iter, 1)
        success:bool=False
        # Vai ao Site
        print_and_log("Abrindo naveador para acessar o banco de dados")
        self.driver.get(data_url)

        # Muda para o Data Frame 0
        self.element_pipeline(
            "presence_of_all_elements_located",
            (By.TAG_NAME, "frame"),
            "switch",
            finder_plural=True
        )
        print_and_log("Mudou para o frame 0.")

    # Pega o nome do formulário e do site
        site_name:str=self.driver.title
        site_name = site_name.replace(" ", "-").replace("f_","").replace("FPE---","").lower()                                            
        
    # Procura o formulário de pesquisa na página
        form=self.element_pipeline(
            "presence_of_element_located",
            (By.TAG_NAME, "form"),
            None
        )

        if form is None:
            raise RuntimeError("formulário não encontrado")

        form_tries:int=3
        while form_tries > 0:
            try:
                form_name:str|None = form.get_attribute("name")  # ty: ignore[unresolved-attribute]
                form_name:str=form_name.replace("f_","").replace("frm","").lower()  # ty: ignore[unresolved-attribute]
                wait_form=self.wait.until(EC.element_to_be_clickable(form))  # ty: ignore[invalid-argument-type]
                if wait_form is not False and form_name is not None:
                    break
            except sel_error.StaleElementReferenceException:
                form_tries+=1
                print_and_log("Formulário fico stale, tentando novamente")
                print_and_log(f"Tentativas: {form_tries}/3")
                form=self.element_pipeline(
                "presence_of_element_located",
                (By.TAG_NAME, "form"),
                None
                )
                if form_tries>=3 and form_name is None:
                    print_and_log("Formulário não encontrado após rechecagem")
                    print_and_log("Tente novamente mais tarde")
                    self.driver.quit(); return success, None, None
    # Cria a pasta para os resultados
        portal_path=OUTPATH/f"{site_name}"
        form_path=portal_path/f"{form_name if form_name is not None else site_name}"
        form_path.mkdir(parents=True, exist_ok=True)
        
        print_and_log(f"Pasta criada para o site: {form_path}")

#=========================================================
# Lógica dos grupos de portais pode se divir a partir aqui
#=========================================================

    # Define os anos para os campos
        name_ano_dropdown_1=self.campos(data_url)

    # Campos dropdowns dos anos
        try:
            if year0 is None:
                self.element_pipeline(
                    "presence_of_all_elements_located",
                    (By.ID, "f_CodExercicioConvenio"), 
                    "select_by_index",
                    select_value=0
                )
            else:
                self.element_pipeline(
                "presence_of_element_located",
                (By.ID, "f_CodExercicioConvenio"), 
                "select_by_visible_text",
                select_value=str(year0)
                )
        except self.sel_errors_and_others as e:
            print_and_log(f"Error selecting the first year option: {e}")
            self.driver.quit(); return success, None, None
        try:
            self.element_pipeline( #Parcerias
            "element_to_be_clickable",
            name_ano_dropdown_1, 
            "select_by_visible_text",
            select_value=str(year1)
            )
        except self.sel_errors_and_others as e:
            print_and_log(f"Error selecting the second year option: {e}")
            self.driver.quit(); return success, None, None
        print_and_log(f"Primeiro dropdown: {year0 if year0 is not None else "None"}")
        print_and_log(f"Segundo dropdown: {year1}")  
        
    # Lista de Órgãos
        Orgao_field = self.element_pipeline(
            "orgao_populado",
            (By.ID, "f_CodOrgao"),
            None
        )
        Orgao_Options = Orgao_field.find_elements(By.TAG_NAME, "option")  # ty: ignore[unresolved-attribute]
        table_org = [{"Orgão": opcao.text.strip()} for opcao in Orgao_Options]
        df_orgao = pd.DataFrame(table_org)
        csv_path_orgao = form_path/f"{year0 if year0 is not None else "None"}_{year1}_OrgaoOptions.csv"
        df_orgao.to_csv(csv_path_orgao, index=False)
        print_and_log("Opções salvas como tabela em CSV!")
        print_and_log("Arquivo de opções de Órgãos salvo em:")
        print_and_log(f"{csv_path_orgao}")
        
    # Checa se o nome do Órgão está na lista, se não, vai embora
        linha:pd.DataFrame = df_orgao.copy().index[df_orgao.copy()["Orgão"] == want_name]
        if linha.empty:
            print_and_log(f"Nome não encontrado: {want_name}")
            self.driver.quit(); return success, None, None

        try:          
           self.element_pipeline(
                "element_to_be_clickable",
                (By.ID, "f_CodOrgao"),
                "select_by_visible_text",
                select_value=want_name
            )
        except self.sel_errors_and_others as e:
            print_and_log(f"Error ao selecionar o orgão: {e}")
            self.driver.quit(); return success, None, None
    
    # Clicar buscar (Robusto para evitar probelemas)
        try:
            self.element_pipeline(
                "element_to_be_clickable",
                (By.ID, "btPesquisar"),
                "click"
            )
        except self.sel_errors_and_others as e:
            print_and_log(f"Error: {e}")
            print_and_log("Clique normal falhou, tentando clique JS")
            try:
                click_buscar=self.element_pipeline(
                "element_to_be_clickable",
                (By.ID, "btPesquisar"),
                None
                )
                self.driver.execute_script("arguments[0].click();", click_buscar)
            except self.sel_errors_and_others as e:
                print_and_log(f"JavaScript click also failed: {e}")
                self.driver.quit(); return success, None ,None
    # Buscar dados na página e organizar em tabela csv        
        results_container=self.element_pipeline(
            "presence_of_all_elements_located",
            (By.ID, "dadosContainer"),
            None
        )
        rows_data=self.extract_pipeline(results_container)  # ty: ignore[invalid-argument-type]

    # Gearar o Data Frame e salvar no CSV
        if rows_data is None:
            print_and_log("A busca não retornou resultados")
            self.driver.quit(); return success, None, None

        df_search = pd.DataFrame(rows_data)
        print_and_log(f"Localizaram-se {len(df_search)} linhas com dados.")
        print_and_log(df_search)
        csv_path_search = form_path/f"{year0 if year0 is not None else "None"}_{year1}_{want_name.lower()}_searchresults.csv"
        df_search.to_csv(csv_path_search, index=False,quoting=csv.QUOTE_ALL,quotechar='"')
        
        #End Browser session
        self.driver.quit()
        print_and_log("Navegador fechado.")
        success:bool= True
        sleep(1)
        return success, site_name, form_name