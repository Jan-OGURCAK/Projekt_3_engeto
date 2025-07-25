"""
main.py: Třetí projekt do Engeto Online Python Akademie

author: Jan OGURČÁK
email: jan.ogurcak@seznam.cz
"""




from bs4 import BeautifulSoup
import requests
import time
import sys
import csv
import random


def kontrola_poctu_parametru():
    """ 
    Funkce kontroluje pocet parametru
    Pokud je vsechno OK program pokračuje,
    pokud ne program končí
    
    """
    
    poc_parametru = len(sys.argv[1:])   # Zjišťuji počet parametrů
    glob["poc_parametru"] = poc_parametru
        
    print("\n")
    if poc_parametru == 2: # Kdayž všechno OK, zapisuji...
        glob["param_url"] = sys.argv[1]
        glob["param_path"] = sys.argv[2]
        print("Počet parametrů OK")

    else:                   # Když ne tak končím
        print("\n")
        print(f'Požadovaný počet parametrů je 2, skutečný počet parametrů {poc_parametru}\n')
        print('Nápověda:')
        print('Program požaduje předání dvou parametrů:')
        print('  - definici okresu')
        print('     - může být URL adresa okresu')
        print('     - může být jméno okresu') 
        print('       pokud jméno obsahuje mezeru (kupř Hradec Králové) musí být v uvozovkách')
        print('       kupř."Hradec Králové"')     
        print('  - cestu cílového souboru\n')
        print('Příklad:')
        print('Main.py "Hradec Králové" c:\\tmp\\soubor.csv' )
        konec_programu()
    
def kontrola_path_souboru():
    """
    Funkce kontoluje platnost path výstupního souboru
    pokusným zápisem.
    
    """
    vsechno_OK = True
    path = sys.argv[2]
            
    try:                     # pokus o zapsání souboru
        with open(path, "w") as f:
            zapisovac = csv.writer(f)
            zapisovac.writerow("Testík")
                
    except FileNotFoundError: # Když se zápis nepovede, program končí
            
        print(f"Cesta k souboru {path} neexistuje")
        print("Prosím zkuste program spustit znovu se správýym parametrem.")
        konec_programu()
        
    return vsechno_OK

def nacti_stranku(zprava: str, url: str) -> dict:
    """
    Funkce stáhne internetovou stránku dle parametru url
    a převede ji do formátu BeautifulSoup.

    Args:
        zprava (str): Text s informací pro uživateli jaká stránka bude stažena
        url (str): Adresa požadované stránky

    Returns:
        dict:   result_OK - spojení proběhlo OK
                status_code - číselný kód statusu spojení
                status_message - textová informace o statusu spojenípythoncd
                soup - soubordata formátu BeautifulSoup
    """
    
    odpoved = {"result_OK": False,
               "status_code": None,
               "status_message": None,
               "soup": None
               }
    
    def dej_status_spojeni(kod_chyby: int):
        """
        Funkce vyhodnotí stavový kód knihovny
        Requests a přímo přepisuje parametry nadřízené funkce
        odpoved["result_OK"] a odpoved["status_message]

        Args:
            kod_chyby (int): response.status_code knihovny Requests
        """
 
        hlavicka = "Error " + str(kod_chyby) + " "
        
        nonlocal odpoved
        
        odpoved["Result_OK"] = False
        
        if 400 <= kod_chyby <500: # Pokus o určení strany na které je problém.. (nesmělý...)
            hlavicka += "Strana uživatele"
        
        elif 500 <= kod_chyby <600:
            hlavicka += "Strana serveru"        
        else:
            hlavička = "Strana blíže nespecifikována"

        match kod_chyby:            # Pokus o bližší specifikaciproblému (opět nesmělý...)
            case 200:
                status_txt = "Transfer OK"
                odpoved["Result_OK"] = True
            case 400:
                status_txt = hlavicka + " - chyba syntaxu"
            case 401:
                status_txt = hlavicka + " - je požadovana autorizace"
            case 403:
                status_txt = hlavicka + " - server oddmitl odpoved"        
            case 404:
                status_txt = hlavicka + " - dokument nebyl nalezen"    
            case 408:
                status_txt = hlavicka + " - prekrocení času na odpoved"   
            case 409:
                status_txt = hlavicka + " - stránka už není dostupná"    
            case 500:
                status_txt = hlavicka + " - interní chyba serveru"
            case 503:
                status_txt = hlavicka + " - služba dočasně nedostupná"   
            case _:
                status_txt = hlavicka + "Status není znám"

        odpoved["status_message"] = status_txt
        
        return 
        
    print("\n")
    print(f"Vysílám žádust o {zprava}. ({url})") # Komentář pro uživatele, o jakou žádost jde a výpis url
    
    start_time = time.time() # Spuštění měření času komunikace
    
    pokusu = 1
    
    zpozdeni = round(random.uniform(0.1, 0.15), 3) # Náhodně generované zpoždění zabrání "zacyklení"
    time.sleep(zpozdeni)                           # serveru
    
    odpoved["status_code"] = None
    
    while odpoved["status_code"] != 200 and pokusu <= glob["requests_pocet_opakovani"]: # Po neúspěšné žádosti opakuje 
                                        # vysílání glob["requests_pocet_opakovani"] kráte
        try:
            
            response = requests.get(url) # Vlastní žádost
    
            odpoved["status_code"] = response.status_code # Načtení status kódu
        
            dej_status_spojeni(odpoved["status_code"]) # Hlášení o výsledku (OK, NOK ...)
            print(odpoved["status_message"])
        
        except:                            # Došlo k chybě
        
            print("Chyba spojení! Pravděpodobně špatná adresa serveru...")
            pokusu += 1
            print(f"Pokus o načtení číslo: {pokusu}")
            time.sleep(glob["requests_zpozdeni"]) # Vyčkávání před opakováním dotazu glob["requests_zpozdeni"] sekund

    print(f"Délka spojení: {round(time.time() - start_time, 3)} s", end="\n") # Konec měření a hlášení o délce
    
    if odpoved["status_code"] == 200: # Všechno OK, vracíme "soup"
        odpoved["soup"] = BeautifulSoup(response.text, "html.parser")

        
    else: # Nedopadlo to. Hlášení a konec programu
        print("\n")
        print(f"Na žádost o {zprava} nepřišla korektní odpověď")
        konec_programu()
       
    return odpoved

def dej_ciselnik_obci():
    """
    Funkce přebere z glob["param_url"] adresu strany seznamu obcí žádaného
    okresu, načte parametry obcí a výsledný dict: vrátí jako návratovou hodnotu 

        Returns:
            dict: - str: nazev -> název obce
                  - str: cislo -> číslo obce
                  - str: url   -> url obce
    """
    obce = []
    
    def dekoduj_tr(tr) -> dict:
        """
        Vnořená funkce. Dekóduje jednotlivé řádky html tabulky (tr>), zjistí
        parametry obce a výsledný dict: vrátí jako parametr
        Args:
            tr (bs4.element.Tag): radek tabulky tr> ve formatu bs4

        Returns:
            (dict): parametry obce
        """
        obec = {}
            
        obec["nazev"] = tr.find(class_="overflow_name") # Má řádek třídu "overflow_name" ?
        obec["cislo"] = tr.find(class_="cislo")         # Má řádek třídu "cisla" ?
        obec["url"] = tr.find(class_="center")          # Má řádek třídu "center" ?
        
        
        if None not in obec.values(): # když platí 3x ano...
            
            if obec["url"].getText() == "X": # obsahuje třída "center" text "X" ?
                
                obec["nazev"] = obec["nazev"].getText() # Zápis textů tříd "qwerflow_name" a "cisla" 
                obec["cislo"] = obec["cislo"].getText()
                td = obec["url"].find("a")
                obec["url"] = glob["koren_url"]  + td.get("href") # Zápis odkazu "href" (url). Musíme přidat kořen adresy!!!
            
        return obec
        
        
    response = nacti_stranku("seznam obci", glob["param_url"]) # Načti stránku dle argumentů a převeď na 
                                                               # BeautifulSoup
    all_tr = response["soup"].find_all("tr") # Z BeautifulSoup vybereme všechny řádky tabulky
    
    obce.clear()
    
    for tr in all_tr: # Pro všechny řádky tabulky výběru
            
        if len(tr.find_all("td")) == 3:     # Když řádek tabulky obsahuje právě tři buňky
            obec = dekoduj_tr(tr)           # Pošlem řádek na dekódování
            if None not in obec.values():   # Když je obec dekódována korektně, zapíšem (Různé náhodné kombinace v tr)
                    obce.append(obec)  
                    
    if len(obce) == 0:
        print("\n")
        print(f"Zadaná stránka {glob['param_url']} neobsahuje žádná použitelná data!")
        konec_programu()    
        
    return obce

def preved_na_int(retezec) -> int: 
    """_summary_

    Args:
        retezec (Any): vstupní hodnota

    Returns:
        int: argument konvertován na int nebo 0
        
    """
    navrat = 0
    
    try:
        navrat = int(retezec)
        
    except:
        pass
    
    return navrat
    
def vytvor_dict_vysledku():
    """
    Funkce bere řádek po řádku číselník obcí glob["cielnik_obci"], vyžádá si data obce
    a tyto data dekóduje do řadku dict: Rádky appenduje do list: glob["data_pro_export"]
    """
    
    def dekoduj_hlavicku(soup):
        """
        Funkce přebírá jako parametr data tabulky stánky obce.
        Vybírá požadované parametry vrací je jako dict

        Args:
            soup (typebs4.element.Tag): data BautifulSoup - id="ps311_t1"

        Outputs:
            vytváří nebo přidává klíče do dict:radek (Zázbnam obce)
                    - (str:) "Voličů v seznamu     : (int:)
                    - (str:) "Vydaných obálek"     : (int:)       
                    - (str:) "Odevzdaných obálek"  : (int:)               
                    - (str:) "Platných hlasů"      : (int:)         
        """
        
        nonlocal radek
        nonlocal obec
        
        statistika = {
                    "Voličů v seznamu": soup.find(headers="sa2"), # Načtení jednotlivých buněk
                    "Vydaných obálek": soup.find(headers="sa3"),
                    "Odevzdaných obálek": soup.find(headers="sa5"),
                    "Platných hlasů": soup.find(headers="sa6")
        }
        
        
        if None not in statistika.values():                        # Proběhlo vyhledávání OK?
            
            for index, (klic, hodnota)  in enumerate(statistika.items()): # Teď si u jednotlivých položek vyžádám parametr text
                int_hodnota_bunky = preved_na_int(hodnota.getText())
                
                if klic in radek.keys():    # Když klíč už v řádku existuje
                    
                    radek[klic] += int_hodnota_bunky  # Hodnotu appendujem
                    
                else:                       # Nebo
                    
                    radek[klic] = int_hodnota_bunky   # klíč přidáme
                    
        else:                                   # Hmmm... někde je chyba
            print("\n")
            print(f"Chyba při dekódování hlavičky obce {obec['nazev']}")
            konec_programu()
                

    def dekoduj_tabulku(tabulka):
        """

        Args:
            tabulka (typebs4.element.Tag): data BautifulSoup - class_="t2_470"
    
        Outputs:
            vytváří nebo appenduje klíče do dict:radek (Zázbnam výsledků obce)
                    - str: "nazev_ strany        : (int:) Počet voličů

        
        """
        
        all_tr = tabulka.find_all("tr") # V tabulce vyhledáme všechny řádky...
        
        for tr in all_tr:               # A vyhodnotíme jeden podruhém
            
            strana_nazev = tr.find(class_="overflow_name")
            cisla = tr.find_all(class_="cislo")
            
            if strana_nazev != None and len(cisla) == 3: # Když se poveslo najít žádané hodnoty
                
                strana_nazev = strana_nazev.getText()                 # načtem jejich atribut "text"
                strana_hlasu = preved_na_int(cisla[1].getText()) # a převedem na int:
                    
                if strana_nazev in radek.keys():                # Když klíč "jmeno_strany" existuje... (více okrsků)
                    
                    radek[strana_nazev] += strana_hlasu         # appendujem počet hlasů
                    
                else:                                           # jinak (první nebo jediný okrsek)
                    
                    radek[strana_nazev] = strana_hlasu          # zavedem klíč jako nový
                    
            
                
        
        return radek
        
        
    def dej_url_vsech_okrsku(soup, obec):
        okrsky = []
        
        if soup.find(id="ps311_t1") is not None: # Je to jenoduchá hlavička (tzn. pouze jeden okrsek) ?
            okrsky.append(obec["url"]) # Zapíšem původní url
            
        else: # Obec má vícero okrsků
            
            all_td = soup.find_all("td", {"class":"cislo"}) # Najdem všechny řádky
    
            for td in all_td: # Pro všechny řádky poskládáme url okrsku
                okrsky.append(glob["koren_url"]   + td.find("a").get("href"))
                
        return okrsky
    
    sestava = []
        
          
        
    
    for obec in glob["ciselnik_obci"]: # Z číselníku obcí čtem obce
        
        response = nacti_stranku(f'stránku obce {obec["nazev"]}', obec["url"]) # Načti stránku dle argumentů a převeď na 
                                                                               # BeautifulSoup
        url_vsech_okrsku = dej_url_vsech_okrsku(response["soup"], obec)
        
        radek = {}
        
        radek = {"Číslo": obec["cislo"], # Zapiš první sloupce řádku
                 "Název": obec["nazev"],
                 "Počet okrsků": len(url_vsech_okrsku)
                 }
        
        cislo_okrsku = 1
        
        for url in url_vsech_okrsku: # Postupně načtem všechny okrsky
            
            if len(url_vsech_okrsku) != 1: # Když je pouze jeden okrsek není nutno načítat stránku nanovo
                response = nacti_stranku(f'stránku okrsku {cislo_okrsku} obce {obec["nazev"]}', url) # Načti stránku dle argumentů a převeď na 
                                                                                   # BeautifulSoup
            tabulky = response["soup"].find_all(class_="table") # Vyberu pouze tabulky
        
            dekoduj_hlavicku(tabulky[0])  # Zdekóduji hlavičku stránky
            
            del tabulky[0] # Data hlavičky už nebudu potřebovat
        
            for tabulka in tabulky:
                dekoduj_tabulku(tabulka) # Vyhodnotím jednotlivé tabulky stran a zapíšu hodnoty
                
            cislo_okrsku += 1
            
    
            
        sestava.append(radek) # Přidám hotový řádek obce do sestavy
        

    glob["data_pro_export"] = sestava # A hotovou sestavu exportuji

    return

def vytvor_soubor(): # Vytvořím .csv
    
    try:
        with open(glob["param_path"], mode="w", newline='') as f:
            hlavicky = glob["data_pro_export"][0].keys()
            zapisovac = csv.DictWriter(f, delimiter=";", fieldnames=hlavicky)

            zapisovac.writeheader()
            zapisovac.writerows(glob["data_pro_export"])
    except:
        print("\n")       
        print(f"Při pokusu o zápis výstupního souboru došlo k chybě!")
        print("Výstupní soubor je pravděpodobně otevřen v jiném programu.")
        konec_programu()

def hledej_okres(param_str:str):

    hledany_okres = param_str.lower().strip() # Odstraníme zbytečné znaky " " a převedem na malá písmena
    
    okres = None
     
    def analyzuj_td(all_td):
        nonlocal okres
        pom_okres = {}
        
        text = all_td[0].getText()
        
        if text[0:2] == "CZ": # OK zdá se že se jedná o korektní řádek
            pom_okres["ID"] = text
            pom_okres["nazev"] = all_td[1].getText()
            odkaz = all_td[3].find("a")
            pom_okres["url"] = glob["koren_url"]  + odkaz.get("href")
            
            if hledany_okres == str(pom_okres["nazev"]).lower().strip(): # Je to ten kýžený okres..?
                okres = pom_okres
                
    
    response = nacti_stranku("stránku přehledu krajů", glob["kraje_url"]) # Načtu stránku
    
    all_tables = response["soup"].find_all(class_="table") # Vyberu pouze tabulky
    
    for table in all_tables: # A pak pěkně tabulku za tabulkou
        
        if okres != None: break # Když se povedlo tak končím
        
        all_tr = table.find_all("tr") # Vyberu pouze jednotlivé řádky
        
        for tr in all_tr:  # Rozeberu na jednotlivé řádky
            
            if okres != None: break # Když se povedlo tak končím
            
            all_td = tr.find_all("td") # Rozeberu řádek na buňky
            
            if len(all_td) == 4: # Když odpovídá počet buněk tak to pošku na dekódování
                analyzuj_td(all_td)
                
    if okres != None:   # Našlo se něco..?
        glob["param_url"] = okres["url"]
        print("\n")    
        print(f'Nalezen okres {okres["nazev"]} kód -> {okres["ID"]} url -> {okres["url"]}')       
    else:               # Neúspěch, končím
        print("\n")    
        print(f"Okres s názvem {param_str} nebyl nalezen")
        konec_programu()  
        
def start_programu():

    kontrola_poctu_parametru()
    kontrola_path_souboru()
    
    if "www.volby.cz" not in glob["param_url"]:  hledej_okres(glob["param_url"])
        
    glob["ciselnik_obci"] = dej_ciselnik_obci()
    
    vytvor_dict_vysledku()
    vytvor_soubor()
    
    print("\n")
    print("Program byl řádně ukončen!")
    print("\n")    

def konec_programu():
    
    print("\n")
    print("Při běhu programu došlo ke kritické chybě a program byl ukončen.")
    print("Prosím okuste se sputit program s jinými parametry a případně kotaktujte autora.", "\n")
    exit()
    
parkoviste = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"

glob = {
    "poc_parametru":0,
    "param_url": "",
    "koren_url":"https://www.volby.cz/pls/ps2017nss/",
    "kraje_url": "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ", 
    "param_path": "",
    "ciselnik_obci": [],
    "data_pro_export": [],
    "program_prerusen": False,
    "requests_pocet_opakovani":5,
    "requests_zpozdeni":0.5
}

################### Start programu #####################################################
if __name__ == "__main__": 
    start_programu()


