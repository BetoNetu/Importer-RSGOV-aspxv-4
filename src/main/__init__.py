#!./.venv/bin/python

# -------------------------------------------------------------------------------------------------------------------
# Arquivo Principal: Faz a lógica inicial e chama a função extratora
# -------------------------------------------------------------------------------------------------------------------

from pathlib import Path
from sys import exit

from scrapper import extractor_from_RSGov

ROOT=Path(__file__).parent.parent
OUTPATH=ROOT/"download"

def main():

    Path.mkdir(OUTPATH,exist_ok=True)
    data_url = input("Enter the database's URL: ")
    mode_select = input("Select the mode (1 for double year, 0 for single year): ")
    start_year = int(input('Enter the start year: ').strip())
    end_year = int(input('Enter the start year: ').strip())
    # range(i,j) = [i, i+1,i+2, ..., j-1]
    # ṕor isso 
    for i in range(start_year,(end_year+1),1):
            YearIO:int = i
            if mode_select == "1":
                year0, year1 = YearIO, YearIO
            elif mode_select == "0":
                year0, year1 = None, YearIO
            else:
                print("Invalid mode. Exiting...")
                exit(1)
            print(f"\n--- Processing year: {YearIO} ---")
            extraction_success, site_name, form_name = extractor_from_RSGov(year0, year1, data_url)
            if not extraction_success:
                print(f"Failed for year {YearIO}, continuing to next...")
    return site_name, form_name

if __name__ == '__main__':


    site_name, form_name=main()
    print("\nAll years processed.")
    print(f"Data saved in: {form_name}")
    print("\nScript finished successfully.")
    input("Press Enter to exit...")