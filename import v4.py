# Import v4
# From txt year file automated search and data extraction from a database using Selenium, with options for single or double year selection, and saving results in CSV format.
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common import exceptions as e
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import sys
# Wait FIRST, then find
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)
#Waiter function to ensure elements are loaded before we try to interact with them, to avoid errors.
def fullwait():
    wait.until(EC.presence_of_element_located((By.ID, "f_CodExercicioConvenio")))
    wait.until(EC.presence_of_element_located((By.ID, "f_Ex")))
    wait.until(EC.presence_of_element_located((By.ID, "f_CodOrgao")))
#Extractor FUnction
def extractor_from_RSGov(year0, year1, data_url):
    print("Opening browser to acess the database...")
    driver.get(data_url)
    frame = driver.find_elements(By.TAG_NAME, "frame")
    driver.switch_to.frame(0)
    print("Switched to the frame 0.")
    fullwait()
    Portal = driver.find_element(By.TAG_NAME, "form")
    Portal_name = Portal.get_attribute("name")
    site_name = driver.title.replace(" ", "_")
    os.makedirs("C:/Users/betor/Desktop/py_downloads", exist_ok=True)
    os.makedirs(f"C:/Users/betor/Desktop/py_downloads/{site_name}/{Portal_name}", exist_ok=True)
    print(f"Directory created for the site: C:/Users/betor/Desktop/py_downloads/{site_name}")
    fullwait()
    # Year dropdowns
    click_year0 = driver.find_element(By.ID, "f_CodExercicioConvenio")
    select_click_year0 = Select(click_year0)
    fullwait()
    click_year1 = driver.find_element(By.ID, "f_Ex")
    select_click_year1 = Select(click_year1)
    try:
        if year0 is None:
            select_click_year0.select_by_index(0)
            option_year_value0 = "blank"
        else:
            select_click_year0.select_by_visible_text(year0)
            option_year_value0 = year0
    except Exception as e:
        print(f"Error selecting the first year option: {e}")
        input("Press Enter to exit and try again...")
        driver.quit(); return False, None, None
    fullwait()
    try:
        select_click_year1.select_by_visible_text(year1)
        option_year_value1 = year1
    except Exception as e:
        print(f"Error selecting the first year option: {e}")
        input("Error. Press Enter to exit and try again...")
        driver.quit(); return False, None, None
    print(f"First dropdown: '{option_year_value0}', Second dropdown: '{option_year_value1}'")
    # Orgão List
    WebDriverWait(driver, 15).until(
        lambda d: len(d.find_element(By.ID, "f_CodOrgao")
                    .find_elements(By.TAG_NAME, "option")) > 94 #To assure that, even with slow loading, all options in the orgao dropdown are loaded before we try to find them
    )
    Orgao_list = driver.find_element(By.ID, "f_CodOrgao")
    Orgao_Options = Orgao_list.find_elements(By.TAG_NAME, "option")
    table_org = [
        {
            "#": i,
            "Name": opt.text.strip()
        }
        for i, opt in enumerate(Orgao_Options)
    ]
    df2 = pd.DataFrame(table_org)
    print(df2)
    csv_path_orgao = f"C:/Users/betor/Desktop/py_downloads/{site_name}/{Portal_name}/{option_year_value0}_{option_year_value1}_orgaooptions.csv"
    df2.to_csv(csv_path_orgao, index=False)
    print(f"Options saved as a table in CSV format! File saved to: {csv_path_orgao}")
    click_orgao = driver.find_element(By.ID, "f_CodOrgao")
    select_click_orgao = Select(click_orgao)
    IOorgao = "70" # 70 is the id for the SEDUC/RS, you can change it to select another orgao or use input() to ask the user for the orgao ID to select
    selected_option_orgao = df2[df2["#"] == int(IOorgao)]
    if selected_option_orgao.empty:
        print(f"No option found for orgao ID {IOorgao}")
        driver.quit(); return False, None, None
    option_orgao_name = selected_option_orgao["Name"].values[0]
    new_orgao_name = option_orgao_name.strip().replace(" ", "_")
    print(f"Orgao selected: {option_orgao_name}")
    try:
        fullwait()
        click_orgao = driver.find_element(By.ID, "f_CodOrgao")        
        select_click_orgao = Select(click_orgao)
        select_click_orgao.select_by_visible_text(option_orgao_name.strip())
    except Exception as e:
        print(f"Error selecting the orgao option: {e}")
        input("Option not found. Press Enter to exit and try again...")
        driver.quit(); return False, None, None
    # Clicar buscar
    fullwait()
    
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
        click_buscar = driver.find_element(By.ID, "btPesquisar")
        fullwait()
        try:
            click_buscar.click()
        except Exception as e:
            print(f"Error: {e}")
            try:
                wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
                driver.execute_script("arguments[0].click();", click_buscar)
            except Exception as e2:
                print(f"JavaScript click also failed: {e2}")
                input("Press Enter to exit...")
                driver.quit(); return False, None ,None
    except Exception as e3:
            print(f"Error: {e3}")
            input("Press Enter to exit...")
            driver.quit(); return False, None, None      
    #Buscar dados na página e organizar em tabela csv
    try:
        wait.until(EC.presence_of_element_located((By.ID, "dadosContainer")))  # Wait for the results to load
        results_container = driver.find_element(By.ID, "dadosContainer")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))  # Wait for the table to be present
        result_table = results_container.find_element(By.TAG_NAME, "table")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "thead")))  # Wait for the table header to be present
        thead = result_table.find_element(By.TAG_NAME, "thead")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tr")))  # Wait for the header row to be present
        header_row = thead.find_element(By.TAG_NAME, "tr")
        header_cells = header_row.find_elements(By.TAG_NAME, "th")
        headers = [cell.text.strip() for cell in header_cells]
        print(f"Found {len(headers)} headers: {headers}")
    except Exception as e:
        print(f"Error finding results container: {e}")
        input("Press Enter to exit...")
        driver.quit(); return False, None ,None
    rows_data = []
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))  # Wait for the table body to be present
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
    except Exception as e:
        print(f"Error finding tbody rows: {e}")
        input("Press Enter to exit..."); driver.quit(); return False, None ,None
    df_search = pd.DataFrame(rows_data)
    print(f"Found {len(df_search)} data rows.")
    print(df_search)
    csv_path_search = f"C:/Users/betor/Desktop/py_downloads/{site_name}/{Portal_name}/{option_year_value0}_{option_year_value1}_{new_orgao_name}_searchresults.csv"
    df_search.to_csv(csv_path_search, index=False)
    #End Chrome session
    driver.quit()
    print("Browser closed.")
    return True, site_name, Portal_name

#Main Loop
data_url = input("Enter the database's URL: ")
mode_select = input("Select the mode (1 for double year, 0 for single year): ")
year_file = input('Enter the path to the year file: ')
try: 
    with open(year_file, 'r') as file:
        for line_num, line in enumerate(file, 1):
                YearIO = line.strip()
                if not YearIO:          # skip empty lines
                    continue
                if not YearIO.isdigit():
                    print(f"Warning: line {line_num} ('{YearIO}') is not a valid year – skipping", file=sys.stderr)
                    continue
                if mode_select == "1":
                    year0, year1 = YearIO, YearIO
                elif mode_select == "0":
                    year0, year1 = None, YearIO
                else:
                    print("Invalid mode. Exiting...")
                    sys.exit(1)
                print(f"\n--- Processing year: {YearIO} ---")
                extraction_success, site_name, Portal_name = extractor_from_RSGov(year0, year1, data_url)
                if not extraction_success:
                    print(f"Failed for year {YearIO}, continuing to next...")
except FileNotFoundError:
    input(f"Year file not found at '{year_file}'. Press Enter to exit and try again...")
    sys.exit(1)
print("\nAll years processed.")
print(f"Data saved in: C:/Users/betor/Desktop/py_downloads/{site_name}/{Portal_name}/")
print("\nScript finished successfully.")
input("Press Enter to exit...")