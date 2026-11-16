"""### Scrapper:
1. Vai ao site informado; 
2. Procura por elementos específicos da na página html;
3. Faz a busca a partir de critérios definidos (realizando as buscas em modo simples e duplo);
4. Salva os dados em CSV."""

# -------------------------------------------------------------------------------------------------------------------
# Função Extratora: 1) Vai ao site fornecido; 2) Procura por elementos específicos da na página html; 3) Faz a
# busca a partir de critérios definidos (realizando as buscas em modo simples e duplo) 4) Salva os dados em CSV.
# 
# Especificamente desenvolvida para o Portal XXX (https://www.)
# Chamada por ../main/__init__.py
# -------------------------------------------------------------------------------------------------------------------

from pathlib import Path
from time import sleep
from typing import Literal

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


class Scrapper:
    """Classe contendo toda a lógica da extração dos convênios e parcerias"""
    def __init__(self, headless: bool = False)->None:
        """Inicia o navegador e variáveis importantes"""
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        self.browser = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.browser, 5)
        self.iter = 0
        self.sel_errors_and_others:tuple=(
            #Selenium Exceptions
            sel_error.DetachedShadowRootException,
            sel_error.ElementClickInterceptedException,
            sel_error.ElementNotInteractableException,
            sel_error.ElementNotSelectableException,
            sel_error.ElementNotVisibleException,
            sel_error.ExceptionMapping,
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
            BaseExceptionGroup,
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

    #Função condicional dos elementos de cada um, por enquanto parcerias e convênios tem f_EX==f_CodExercicio

    #parcerias = f_ex
    #convênio = f_CodExercicio

    def _fullwait(self) -> None:
        """Função de espera para assegurar que os elementos são carregados antes de tentar interagir com eles, evitando erros"""
        self.wait.until(EC.presence_of_element_located((By.ID, "f_CodExercicioConvenio")))
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "f_Ex"))) #Parcerias
        except (sel_error.TimeoutException,sel_error.NoSuchElementException):
            print("Elment f_Ex not found\nSearching for f_CodExercicio")
            self.wait.until(EC.presence_of_element_located((By.ID, "f_CodExercicio"))) #Convênios
        self.wait.until(EC.presence_of_element_located((By.ID, "f_CodOrgao")))

    # Função Extratora
    def extractor_from_RSGov(self, year0:int|None, year1:int, data_url:str) -> tuple[Literal[True],str,str|None]|tuple[Literal[False],None,None]:
        """Função Extratora. Controla o self.browser, vai ao site, executa a busca e salva os dados em CSV"""

        # Garante que o primeiro só abre uma janela
        if self.iter > 0:
            self.__init__()
        self.iter = min(self.iter, 1)
        success:bool=False
        # Vai ao Site
        print("Abrindo naveador para acessar o banco de dados")
        self.browser.get(data_url)

        # Muda para o Data Frame 0
        self.browser.find_elements(By.TAG_NAME, "frame")

        self.browser.switch_to.frame(0)
        print("Mudou para o frame 0.")
        sleep(1)

        # Procura o formulário de pesquisa na página
        form:WebElement = self.browser.find_element(By.TAG_NAME, "form")
        # Pega o nome do formulário
        try:
            form_name:str|None = form.get_attribute("name")
            if form_name != None: form_name:str=form_name.replace("f_","")
        except self.sel_errors_and_others as e:
            print(f"{e}")
            site_name:str=self.browser.title.replace(" ", "-").replace("f_","")
            form_name:str=site_name

        site_name:str= self.browser.title.replace(" ", "-").replace("f_","")
        portal_path=OUTPATH/f"{site_name.lower()}"
        form_path=portal_path/f"{form_name.lower() if form_name is not None else site_name}"
        Path.mkdir(Path(f"{form_path}"), parents=True, exist_ok=True)
        print(f"Pasta criada para o site: {form_path}")
        sleep(1.5)

        # Campos dropdowns dos anos
        year_field0 = self.browser.find_element(By.ID, "f_CodExercicioConvenio")#Ambos
        select_year_field0 = Select(year_field0)
        sleep(1.5)
        try:
            year_field1 = self.browser.find_element(By.ID, "f_Ex") #Parcerias
        except (sel_error.TimeoutException,sel_error.NoSuchElementException):
            print("Elmento f_Ex não localizado\nBuscando por f_CodExercicio")
            year_field1 = self.browser.find_element(By.ID, "f_CodExercicio") #Convênios


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
            self.browser.quit(); return success, None, None

        sleep(1.5)

        try:
            select_year_field1.select_by_visible_text(str(year1))
            option_year_value1 = year1
        except self.sel_errors_and_others as e:
            print(f"Error selecting the first year option: {e}")
            input("Error. Press Enter to exit and try again...")
            self.browser.quit(); return success, None, None
        print(f"First dropdown: '{option_year_value0}', Second dropdown: '{option_year_value1}'")  

        # Lista de Órgãos
        
        WebDriverWait(self.browser, 30).until(Scrapper._orgao_populado)
        Orgao_list = self.browser.find_element(By.ID, "f_CodOrgao")
        Orgao_Options = Orgao_list.find_elements(By.TAG_NAME, "option")
        
        table_org = [{"Orgão": opcao.text.strip()} for opcao in Orgao_Options]
        df_orgao = pd.DataFrame(table_org)
        print(df_orgao)
        
        csv_path_orgao = form_path/f"{option_year_value0}_{option_year_value1}_orgaooptions.csv"
        df_orgao.to_csv(csv_path_orgao, index=False)
        print(f"Options saved as a table in CSV format! File saved to: {csv_path_orgao}")
        
        # Selecionar Órgão
        click_orgao = self.browser.find_element(By.ID, "f_CodOrgao")
        Select(click_orgao)
        
        # logica para fazer o nome a) ser senitizado e b) vir de algum lugar
        want_name:str="SECRETARIA DA EDUCACAO"
        linha:pd.DataFrame = df_orgao.copy().index[df_orgao.copy()["Orgão"] == want_name]
        if linha.empty:
            print(f"Nome não encontrado: {want_name}")
            self.browser.quit(); return success, None, None
        new_orgao_name = want_name.strip().replace(" ", "_")
        print(f"Orgão selecionado: {want_name}")

        try:
            sleep(1.5)
            click_orgao = self.browser.find_element(By.ID, "f_CodOrgao")        
            select_click_orgao = Select(click_orgao)
            select_click_orgao.select_by_visible_text(want_name.strip().upper())
        except self.sel_errors_and_others as e:
            print(f"Error ao selecionar o orgão: {e}")
            self.browser.quit(); return success, None, None
        sleep(1.5)

        # Clicar buscar (Robusto para evitar probelemas)
        try:
            self.wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
            click_buscar = self.browser.find_element(By.ID, "btPesquisar")
            sleep(1.5)
            try:
                click_buscar.click()
            except self.sel_errors_and_others as e:
                print(f"Error: {e}")
                try:
                    self.wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
                    self.browser.execute_script("arguments[0].click();", click_buscar)
                except self.sel_errors_and_others as e:
                    print(f"JavaScript click also failed: {e}")
                    self.browser.quit(); return success, None ,None
        except self.sel_errors_and_others as e:
                print(f"Error: {e}")
                self.browser.quit(); return success, None, None

    # Buscar dados na página e organizar em tabela csv
        #Headers da tabela de Resultados
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "dadosContainer")))  
            # Espera os resultados carregar
            results_container = self.browser.find_element(By.ID, "dadosContainer")

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))  
            # Espera os elementos estarem presentes
            result_table = results_container.find_element(By.TAG_NAME, "table")

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "thead")))  
            # Espera os headers da tabela estarem presentes
            thead = result_table.find_element(By.TAG_NAME, "thead")

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "tr")))  
            # Espera que a linha dos headers da tabela estejam presentes
            header_row = thead.find_element(By.TAG_NAME, "tr")

            # Condensa os headers em uma lista
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            headers = [cell.text.strip() for cell in header_cells]
            print(f"Found {len(headers)} headers: {headers}")
        except self.sel_errors_and_others as e:
            print(f"Erro ao encontrar os resultados do container de dados: {e}")
            self.browser.quit(); return success, None ,None

        # Data

        rows_data = []
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))  
            # Wait for the table body to be present
            tbody = result_table.find_element(By.TAG_NAME, "tbody")
            data_rows = tbody.find_elements(By.TAG_NAME, "tr")
            for row in data_rows:
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
            self.browser.quit(); return False, None ,None

        # Gearar o Data Frame e salvar no CSV

        df_search = pd.DataFrame(rows_data)
        print(f"Localizaram-se {len(df_search)} linhas com dados.")
        print(df_search)
        csv_path_search = form_path/f"{option_year_value0}_{option_year_value1}_{new_orgao_name}_searchresults.csv"
        df_search.to_csv(csv_path_search, index=False)
        
        #End Chrome session
        self.browser.quit()
        print("Navegador fechado.")
        success:bool= True
        return success, site_name, form_name