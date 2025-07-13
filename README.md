# Engeto projekt 3 -  Elections Scraper

Program slouží ke stahování dat z voleb dle jednotlivých okresů a jejich ukládání ve formátu *.csv

 ## Instalace:
 
		 Program ke své činnosti vyžaduje instalaci knihoven "Requests" a 
		 "Beautifulsoup" Tyto knihovny je možno jenoduše instalovat formou dávky 
		 ze souboru "Requirements.txt" Při instalaci je prostě potřeba do okna 
		 terminálu zadat příkaz  "pip install -r requirements.txt". 
		 Za předpokladu že je requirements.txt umístněn v jiném adresáří než
		 vlasní program, je potřeba uvést celou cestu.
		 
		 
 ## Ovládání programu
		 Program je ovládán pomocí parametrů v příkazovém řádku. Vyžaduje přítomnost 
		 dvou parametrů. 
		
 
- ### Zdroj dat ke zpracování
	zdroj může definovat buď přímo url dané stránky ( kupř.       											"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" pro okres Prostějov) nebo přímo jako jméno okresu (kupř. "Hradec králové".	 **Pozor, tento parametr zadávejte vždy v uvozovkách!** Problém může způsobit přítomnost speciálních znaků v adrese (třeba &) nebo mezera v názvu okresu (třeba Hradec Králové)
- ### Cesta k výstupnímu souboru
	cestu můžeme zadat jako kompletní (kupř. 	c\data\volby.csv) vebo můžeme zadat pouze jméno souboru (kupř. volby.csv) v tom případě bude soubor uložen do adresáře, odkud byl program spuštěn.

	### Přiklad příkazového řádku:
	**python main.py "Prostějov" c:\volby\2017\prostějov.csv**

## Vlastní běh programu
Program počas běhu stahuje v závislosti na počtu volebních okrsků mnoho internetových stránek, a proto běh programu trvá. Aby bylo zřejmé že "nezamrzl", program svoji činnost bohatě komentuje. Kupř:

**Vysílám žádust o stránku obce Alojzov. (https://www.volby.cz/pls/ps2...
Transfer OK
Délka spojení: 0.375 s**

## Ochrana před zahlcením serveru
program počas testování mnohokrát havaroval z důvodu zahlcení serveru. (Spolužáci pravděpodobně pilně testovali...😊) Program byl proto upraven následovně:

### Ochrana serveru

program před každým požadavkem chvíli vyčkává. Interval je generován náhodně v intervalu 100 až 150ms

### Opakování požadavku na data
			
při neúspešném požadavku na data program požadavek vícekrát opakuje. Počet 			opakování je nastaven v proměnné glob["requests_pocet_opakovani"] (standartně 5) a interval opakování v proměnné glob["requests_zpozdeni"] (standartně 0.5 sec)


### Ukončení programu

Program je ukončen hlášením "Program byl řádně ukončen".
