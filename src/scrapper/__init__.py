# -------------------------------------------------------------------------------------------------------------------
# Função Extratora V4: 1) Vai ao site fornecido; 2) Procura por elementos específicos da na página html; 3) Faz a
# busca a partir de critérios definidos (realizando as buscas em modo simples e duplo) 4) Salva os dados em CSV.
# 
# Especificamente desenvolvida para o Portal XXX (https://www.)
# Chamada por ../main/__init__.py
# -------------------------------------------------------------------------------------------------------------------

from pathlib import Path
from typing import Literal

import pandas as pd
import selenium.webdriver.remote.errorhandler as sel_error
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from main import OUTPATH

# Configuração do Browser
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(browser, 10)

# Função de espera para assegurar que os elementos são carregados antes de tentar interagir com eles,
# evitando erros
def fullwait():

    wait.until(EC.presence_of_element_located((By.ID, "f_CodExercicioConvenio")))
    wait.until(EC.presence_of_element_located((By.ID, "f_Ex")))
    wait.until(EC.presence_of_element_located((By.ID, "f_CodOrgao")))

# Função Extratora
def extractor_from_RSGov(year0:int|None, year1:int, data_url:str) -> tuple[Literal[True],str,str|None]|tuple[Literal[False],None,None]:
    exit:bool=False
    sel_errors_and_others:tuple=(
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
    # Vai ao Site
    print("Opening browser to acess the database...")
    browser.get(data_url)

    # Muda para o Data Frame 0
    browser.find_elements(By.TAG_NAME, "frame")
    browser.switch_to.frame(0)
    print("Switched to the frame 0.")
    fullwait()
    
    # Procura o formulário de pesquisa na página
    form:WebElement = browser.find_element(By.TAG_NAME, "form")
    # Pega o nome do formulário
    try:
        form_name:str|None = form.get_attribute("name")
        if form_name != None:
            form_name:str=form_name.replace("f_","")
    except sel_errors_and_others as e:
        print(f"{e}")
        site_name:str=browser.title.replace(" ", "-").replace("f_","")
        form_name:str=site_name
    
    site_name:str= browser.title.replace(" ", "-").replace("f_","")
    portal_path=OUTPATH/f"{site_name.lower()}"
    form_path=portal_path/f"{form_name.lower() if form_name is not None else site_name}"
    Path.mkdir(form_path, exist_ok=True)
    print(f"Directory created for the site: {form_path}")
    fullwait()
    
    # Campos dropdowns dos anos
    year_field0 = browser.find_element(By.ID, "f_CodExercicioConvenio")
    select_year_field0 = Select(year_field0)
    fullwait()
    year_field1 = browser.find_element(By.ID, "f_Ex")
    select_year_field1 = Select(year_field1)
    
    try:
        if year0 is None:
            select_year_field0.select_by_index(0)
            option_year_value0 = "blank"
        else:
            select_year_field0.select_by_visible_text(str(year0))
            option_year_value0 = year0
    except sel_errors_and_others as e:
        print(f"Error selecting the first year option: {e}")
        input("Press Enter to exit and try again...")
        browser.quit(); return exit, None, None
    
    fullwait()
    
    try:
        select_year_field1.select_by_visible_text(str(year1))
        option_year_value1 = year1
    except sel_errors_and_others as e:
        print(f"Error selecting the first year option: {e}")
        input("Error. Press Enter to exit and try again...")
        browser.quit(); return exit, None, None
    print(f"First dropdown: '{option_year_value0}', Second dropdown: '{option_year_value1}'")  
    
    # Lista de Órgãos
    WebDriverWait(browser, 15).until(
        lambda d: len(d.find_element(By.ID, "f_CodOrgao").find_elements(By.TAG_NAME, "option")) > 94 
    # Para garantir que, mesmo com carregamento lento, todas as opções no menu suspenso de órgão sejam 
    # carregadas antes de tentarmos encontrá-las.
    )

    Orgao_list = browser.find_element(By.ID, "f_CodOrgao")
    Orgao_Options = Orgao_list.find_elements(By.TAG_NAME, "option")
    table_org = [
        {
            "#": i,
            "Name": opcao.text.strip()
        }
        for i, opcao in enumerate(Orgao_Options)
    ]
    df_orgao = pd.DataFrame(table_org)
    print(df_orgao)
    csv_path_orgao = form_path/f"{option_year_value0}_{option_year_value1}_orgaooptions.csv"
    df_orgao.to_csv(csv_path_orgao, index=False)
    print(f"Options saved as a table in CSV format! File saved to: {csv_path_orgao}")
    
    # Selecionar Órgão
    click_orgao = browser.find_element(By.ID, "f_CodOrgao")
    Select(click_orgao)
    CodOrgao = "70" 
    # 70 é o ID para a SEDUC/RS; você pode alterá-lo para selecionar outro órgão ou usar input() para perguntar ao usuário qual 
    # ID de órgão selecionar.
    orgao_selecionado = df_orgao[df_orgao["#"] == int(CodOrgao)]
    if orgao_selecionado.empty:
        print(f"No option found for orgao ID {CodOrgao}")
        browser.quit(); return exit, None, None
    
    nome_orgao_selecionado = orgao_selecionado["Name"].values[0]
    new_orgao_name = nome_orgao_selecionado.strip().replace(" ", "_")
    print(f"Orgao selected: {nome_orgao_selecionado}")
    
    try:
        fullwait()
        click_orgao = browser.find_element(By.ID, "f_CodOrgao")        
        select_click_orgao = Select(click_orgao)
        select_click_orgao.select_by_visible_text(nome_orgao_selecionado.strip())
    except sel_errors_and_others as e:
        print(f"Error selecting the orgao option: {e}")
        input("Option not found. Press Enter to exit and try again...")
        browser.quit(); return exit, None, None
    fullwait()
    
    # Clicar buscar (Robusto para evitar probelemas)
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
        click_buscar = browser.find_element(By.ID, "btPesquisar")
        fullwait()
        try:
            click_buscar.click()
        except sel_errors_and_others as e:
            print(f"Error: {e}")
            try:
                wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
                browser.execute_script("arguments[0].click();", click_buscar)
            except sel_errors_and_others as e:
                print(f"JavaScript click also failed: {e}")
                input("Press Enter to exit...")
                browser.quit(); return exit, None ,None
    except sel_errors_and_others as e:
            print(f"Error: {e}")
            input("Press Enter to exit...")
            browser.quit(); return exit, None, None

# Buscar dados na página e organizar em tabela csv
    #Headers da tabela de Resultados
    
    try:
        wait.until(EC.presence_of_element_located((By.ID, "dadosContainer")))  
        # Espera os resultados carregar
        results_container = browser.find_element(By.ID, "dadosContainer")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))  
        # Espera os elementos estarem presentes
        result_table = results_container.find_element(By.TAG_NAME, "table")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "thead")))  
        # Espera os headers da tabela estarem presentes
        thead = result_table.find_element(By.TAG_NAME, "thead")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tr")))  
        # Espera que a linha dos headers da tabela estejam presentes
        header_row = thead.find_element(By.TAG_NAME, "tr")

        # Condensa os headers em uma lista
        header_cells = header_row.find_elements(By.TAG_NAME, "th")
        headers = [cell.text.strip() for cell in header_cells]
        print(f"Found {len(headers)} headers: {headers}")
    except sel_errors_and_others as e:
        print(f"Error finding results container: {e}")
        input("Press Enter to exit...")
        browser.quit(); return exit, None ,None
    
    # Data
    
    rows_data = []
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))  
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
    except sel_errors_and_others as e:
        print(f"Error finding tbody rows: {e}")
        input("Press Enter to exit..."); browser.quit(); return False, None ,None
    
    # Gearar o Data Frame e salvar no CSV
    
    df_search = pd.DataFrame(rows_data)
    print(f"Found {len(df_search)} data rows.")
    print(df_search)
    csv_path_search = form_path/f"{option_year_value0}_{option_year_value1}_{new_orgao_name}_searchresults.csv"
    df_search.to_csv(csv_path_search, index=False)
    exit:bool= True
    #End Chrome session
    browser.quit()
    print("Browser closed.")
    
    return exit, site_name, form_name