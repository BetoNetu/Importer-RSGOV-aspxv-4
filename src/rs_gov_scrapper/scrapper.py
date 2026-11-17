"""### Scrapper:
1. Vai ao site informado; 
2. Procura por elementos específicos da na página html;
3. Faz a busca a partir de critérios definidos (realizando as buscas em modo simples e duplo);
4. Salva os dados em CSV.
---
#### Implementado

- [Portal de Parcerias](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ParceriaFirmada-PESQUISAR_OUT.aspx)
- [Portal de Convênios (WIP)](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-ConvenioFirmado-PESQUISAR_OUT.aspx)
---
#### To-do

- [Editais de Chamamento](https://portalfpe.sefaz.rs.gov.br/sefaconv/apl/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PortalEditalConvenio-PESQUISAR_OUT.aspx)
- [Dispenda de Eligibilidade Bonito <  2025](https://www.convenioseparcerias.rs.gov.br/dispensas-e-inexigibilidades) - Será um parto
- [Dispenda de Eligibilidade Feio   >= 2025](https://portalfpe.sefaz.rs.gov.br/SefaConv/APL/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PORTALPUBLICACAOCONVENIO-Pesquisar_Out.aspx?chave=1) 
- [Intenção de Recisão](https://www.convenioseparcerias.rs.gov.br/intencoes-de-rescisao-dos-termos-de-colaboracao-e-de-fomento)
- [Manifestação de Interesse](https://portalfpe.sefaz.rs.gov.br/sefaconv/apl/FPE-Transacao.aspx?/SefaConv/APL/ProgramasNet/FPE-PortalMisConvenio-Pesquisar_Out.aspx)
"""
# -------------------------------------------------------------------------------------------------------------------
# Função Extratora: 1) Vai ao site fornecido; 2) Procura por elementos específicos da na página html; 3) Faz a
# busca a partir de critérios definidos (realizando as buscas em modo simples e duplo) 4) Salva os dados em CSV.
# 
# Especificamente desenvolvida para o Portal de Convênios e Parcerias do RS (https://www.)

# Implementado: 
# Chamada por ../main/__init__.py
# -------------------------------------------------------------------------------------------------------------------

import sys
from textwrap import dedent
from time import sleep
from typing import Any, Literal

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

from rs_gov_scrapper.defaults import OUTPATH


class RSGovScrapper:
    """Classe contendo toda a lógica da extração dos convênios e parcerias"""
    # Declarações da classe
    def __init__(self, headless: bool = False)->None:
        """Inicia o navegador e variáveis importantes"""
        print("Inicializando scrapper")
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 5)
        self.iter = 0
        # Para ele não crashar sozinho em cada try que deu errado
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
    def _orgao_populado(driver:WebDriver)->int|Literal[False]:
        """Aguarda o f_CodOrgao option ser atualizado"""
        try:
            opcoes = driver.find_elements(By.CSS_SELECTOR, "#f_CodOrgao option")
            return len(opcoes) > 1   # "blank" + pelo menos uma real
        except sel_error.StaleElementReferenceException:
            return False  # se o DOM foi substituído, tenta de novo
    
    def _waiter(self, EC_name:str,locator:tuple[str,str]|WebElement) -> bool:
        """Lida com as opções de espera"""
        for i in range(3):
            try:
                match EC_name:
                    case "presence_of_element_located":
                        EC_var=EC.presence_of_element_located(locator)            # ty: ignore[invalid-argument-type]
                        WebDriverWait(self.driver,5).until(EC_var)
                    case "presence_of_all_elements_located":
                        EC_var=EC.presence_of_all_elements_located(locator) # ty: ignore[invalid-argument-type]
                        WebDriverWait(self.driver, 5).until(EC_var)
                    case "element_to_be_clickable":
                        EC_var=EC.element_to_be_clickable(locator)
                        WebDriverWait(self.driver,5).until(EC_var)
                    case "_orgao_populado":
                        WebDriverWait(self.driver,5).until(RSGovScrapper._orgao_populado)
                    case _:
                        raise ValueError(f"EC_name desconhecido: {EC_name}")
                return True
            except self.sel_errors_and_others:
                if i == 2:
                    raise
                sleep(0.2)
        return False

# Busca por elementos (finde_element e find_elements) 
    def _finder(self, locator:tuple[Any,Any], plural:bool=False) -> WebElement | list[WebElement]:
        """Lida com a localização de elementos. Busca e retorna o objeto.
        Implementa driver.find_element() e driver.find_elements() de modo chamável"""
        
        print(f"Localizando elemento: {locator}")
        for i in range(3):
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
            print(f"Elemento(s) {locator}, localizado(s)")
            #print(elemento)
            return elemento
        else:
            print(f"Elemento {locator} não localizado")
            return elemento
    
# Interação com elementos já localizados
    def _extract_pipeline(
        self,
        primary_element:WebElement,
        file_data:list|None,
        ) -> None:
        
        """Lida com a extração dos dados do site para um csv"""

    def _element_inetraction(
        self,
        elemento:WebElement|list[WebElement],
        action:str|None,
        file_data:list|None=None
        ) -> bool|WebElement|list[WebElement]|None:

        """Uma pipeline condensada para operar o navegador e a página (busca de elementos html)"""
        for i in range(3):
            try:
                match action:
                    case "Select":
                        Select(elemento)  # ty: ignore[invalid-argument-type]
                    case "click":         # O list_elements nunca chegará em click, tenho que agarntir isso
                        elemento.click()  # ty: ignore[unresolved-attribute] 
                    case "extract":
                        self._extract_pipeline(elemento, file_data) # ty: ignore[invalid-argument-type]
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
        locator:tuple,
        action:str|None,
        finder_plural:bool=False,
    ) -> bool | WebElement | list[WebElement]| None:
        try:
            self._waiter(EC_name,locator)
            elemento=self._finder(locator,finder_plural)
            elemento=self._element_inetraction(elemento,action)
            return elemento
        except self.sel_errors_and_others as e:
            print(f"{e}")
            print(dedent(f"""
            Pipeline do elemento {locator if locator else "None"} falhou.
            Dados da Chamada:
            elemento: {elemento if elemento else "None"}
            
            EC_name:{EC_name}
            action:{action if type(action) is str else "None"}
            finder_plural:{finder_plural}
            """))
            self.driver.quit()
            print("exiting")
            sys.exit(0)

        # """Função de espera para assegurar que os elementos são carregados antes de tentar interagir com eles, evitando erros"""
        # self.wait.until(EC.presence_of_element_located((By.ID, "f_CodExercicioConvenio")))
        # self.wait.until(EC.presence_of_element_located((By.ID, "f_Ex"))) #Parcerias
        # print("Elment f_Ex not found\nSearching for f_CodExercicio")
        # self.wait.until(EC.presence_of_element_located((By.ID, "f_CodExercicio"))) #Convênios
        # self.wait.until(EC.presence_of_element_located((By.ID, "f_CodOrgao")))


#Função condicional dos elementos de cada um
    def _fields(self):
        print("foo")
    #parcerias = f_ex
    #convênio = f_CodExercicio
    #parcerias = f_ex, 70 (seduc), wait until > 94
    #convênio = f_CodExercicio. 19 (seduc), wair until > 20?

# Função Extratora
    def scrapper(self, year0:int|None, year1:int, data_url:str) -> tuple[Literal[True],str,str|None]|tuple[Literal[False],None,None]:
        """Função Extratora. Controla o navegador, vai ao site, executa a busca e salva os dados em CSV"""

        # Garante que o primeiro só abre uma janela
        if self.iter > 0:
            print("(Re)inicializando scrapper")
            self.__init__()
        self.iter = min(self.iter, 1)
        success:bool=False
        # Vai ao Site
        print("Abrindo naveador para acessar o banco de dados")
        self.driver.get(data_url)

        # Muda para o Data Frame 0
        self.element_pipeline(
            "presence_of_all_elements_located",
            (By.TAG_NAME, "frame"),
            "switch",
            finder_plural=True
        )
        print("Mudou para o frame 0.")

        # Procura o formulário de pesquisa na página
        form=self.element_pipeline(
            "presence_of_element_located",
            (By.TAG_NAME, "form"),
            None
        )
        if form is None:
            raise RuntimeError("formulário não encontrado")
        # Pega o nome do formulário e do site
        site_name:str=self.driver.title.replace(" ", "-").replace("f_","").replace("fpe---","")                                              
        form_name:str|None = form.get_attribute("name")           # ty: ignore[unresolved-attribute]
        form_name:str=form_name.replace("f_","").replace("frm","")                       # ty: ignore[unresolved-attribute]
        self.wait.until(EC.element_to_be_clickable(form))  # ty: ignore[invalid-argument-type]          
        
        # Continuar daqui

        portal_path=OUTPATH/f"{site_name.lower()}"
        form_path=portal_path/f"{form_name.lower() if form_name is not None else site_name}"
        form_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Pasta criada para o site: {form_path}")

        
    # Campos dropdowns dos anos
        year_field0 = self.driver.find_element(By.ID, "f_CodExercicioConvenio")#Ambos
        self.wait.until(EC.element_to_be_clickable(year_field0))
        select_year_field0 = Select(year_field0)
        try:
            year_field1 = self.driver.find_element(By.ID, "f_Ex") #Parcerias
        except (sel_error.TimeoutException,sel_error.NoSuchElementException):
            print("Elmento f_Ex não localizado\nBuscando por f_CodExercicio")
            year_field1 = self.driver.find_element(By.ID, "f_CodExercicio") #Convênios
        
        self.wait.until(EC.element_to_be_clickable(year_field1))
        select_year_field1 = Select(year_field1)

        try:
            if year0 is None:
                select_year_field0.select_by_index(0)
                option_year_value0 = "blank"
            else:
                select_year_field0.select_by_visible_text(str(year0))
                option_year_value0 = year0
        except self.sel_errors_and_others as e:
            print(f"Error selecting the first year option: {e}")
            self.driver.quit(); return success, None, None
        try:
            select_year_field1.select_by_visible_text(str(year1))
            option_year_value1 = year1
        except self.sel_errors_and_others as e:
            print(f"Error selecting the first year option: {e}")
            input("Error. Press Enter to exit and try again...")
            self.driver.quit(); return success, None, None
        print(f"First dropdown: '{option_year_value0}', Second dropdown: '{option_year_value1}'")  
        sys.exit(0) #temp
    # Lista de Órgãos
        
        WebDriverWait(self.driver, 30).until(RSGovScrapper()._orgao_populado)
        
        Orgao_list = self.driver.find_element(By.ID, "f_CodOrgao")
        Orgao_Options = Orgao_list.find_elements(By.TAG_NAME, "option")
        
        table_org = [{"Orgão": opcao.text.strip()} for opcao in Orgao_Options]
        df_orgao = pd.DataFrame(table_org)
        print(df_orgao)
        
        csv_path_orgao = form_path/f"{option_year_value0}_{option_year_value1}_orgaooptions.csv"
        df_orgao.to_csv(csv_path_orgao, index=False)
        print(f"Options saved as a table in CSV format! File saved to: {csv_path_orgao}")
        
        # Selecionar Órgão
        self.wait.until(EC.presence_of_element_located((By.ID, "f_CodOrgao")))
        click_orgao = self.driver.find_element(By.ID, "f_CodOrgao")
        Select(click_orgao)
        
        # logica para fazer o nome a) ser senitizado e b) vir de algum lugar
        want_name:str="SECRETARIA DA EDUCACAO"
        linha:pd.DataFrame = df_orgao.copy().index[df_orgao.copy()["Orgão"] == want_name]
        if linha.empty:
            print(f"Nome não encontrado: {want_name}")
            self.driver.quit(); return success, None, None
        new_orgao_name = want_name.strip().replace(" ", "_")
        print(f"Orgão selecionado: {want_name}")

        try:
            self.wait.until(EC.element_to_be_clickable(click_orgao)) 
            select_click_orgao = Select(click_orgao)
            select_click_orgao.select_by_visible_text(want_name.strip().upper())
        except self.sel_errors_and_others as e:
            print(f"Error ao selecionar o orgão: {e}")
            self.driver.quit(); return success, None, None

    # Clicar buscar (Robusto para evitar probelemas)
        try:
            self.wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
            click_buscar = self.driver.find_element(By.ID, "btPesquisar")
            try:
                click_buscar.click()
            except self.sel_errors_and_others as e:
                print(f"Error: {e}")
                try:
                    self.wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
                    self.driver.execute_script("arguments[0].click();", click_buscar)
                except self.sel_errors_and_others as e:
                    print(f"JavaScript click also failed: {e}")
                    self.driver.quit(); return success, None ,None
        except self.sel_errors_and_others as e:
                print(f"Error: {e}")
                self.driver.quit(); return success, None, None

    # Buscar dados na página e organizar em tabela csv
        #Headers da tabela de Resultados
        try:
            
            self.wait.until(EC.presence_of_all_elements_located((By.ID, "dadosContainer")))  
            # Espera os resultados carregar
            results_container = self.driver.find_element(By.ID, "dadosContainer")

            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))  
            # Espera os elementos estarem presentes
            result_table = results_container.find_element(By.TAG_NAME, "table")

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
            print(f"Found {len(headers)} headers: {headers}")
        except self.sel_errors_and_others as e:
            print(f"Erro ao encontrar os resultados do container de dados: {e}")
            self.driver.quit(); return success, None ,None

        # Data
        rows_data = []
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "tbody")))  
            # Wait for the table body to be present
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
        except self.sel_errors_and_others as e:
            print(f"Erro ao localizar linhas de tbody: {e}")
            self.driver.quit(); return False, None ,None

        # Gearar o Data Frame e salvar no CSV

        df_search = pd.DataFrame(rows_data)
        print(f"Localizaram-se {len(df_search)} linhas com dados.")
        print(df_search)
        csv_path_search = form_path/f"{option_year_value0}_{option_year_value1}_{new_orgao_name}_searchresults.csv"
        df_search.to_csv(csv_path_search, index=False)
        
        #End Chrome session
        self.driver.quit()
        print("Navegador fechado.")
        success:bool= True
        return success, site_name, form_name