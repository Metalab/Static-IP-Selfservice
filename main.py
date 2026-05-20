import requests
import re
import ipaddress
import logging
from bs4 import BeautifulSoup

url = "https://spsrakovnik.tech/hauner.vo.2023/PV"
# url = "https://metalab.at/wiki/Netzwerk/Adressen"¨

allowedNetwork = ipaddress.ip_network("192.168.0.0/16")

hostnameIndex = 0 # pro zjištění sloupce, kde je hostanme a zbytek je to stejny
macIndex = 0
ipv4Index = 0
ipv6Index = 0

tableLength = 0 # počet sloupců v tabulce
table = {}

dnsPattern = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
macPattern = r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$"

response = requests.get(url)

#Překlady:
#cell - buňka

# pokud nám ten příkaz vrátil HTML soubor stránky
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    target_heading = soup.find("h2", string="Static prototype IPs")
    if target_heading:
        target_table = target_heading.find_next("table")
        if target_table:
            print("Tabulka nalezena!\n")
            j = 0
            for row in target_table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                cells_text = [cell.get_text(strip=True).lower() for cell in cells]


                #řekne nám indexy jednotlivých sloupcu, jako je treba hostname tak kde je atd...
                if j == 0:
                    tableLength = len(cells_text)
                    i = 0
                    for cell in cells_text:
                        if "hostname" in cell:
                            hostnameIndex = i
                        elif "mac" in cell:
                            macIndex = i
                        elif "ipv4" in cell:
                            ipv4Index = i
                        elif "ipv6" in cell:
                            ipv6Index = i
                        i += 1
                    j += 1
                    #přeskočení hlavičky
                    continue
                
                #ukladani dat na aktualnim radku
                currentMac = cells_text[macIndex]
                cuurentIpv4 = cells_text[ipv4Index]
                cuurentIpv6 = cells_text[ipv6Index]

                if not re.match(macPattern, currentMac):
                    logging.error(f"Wrong format of MAC address: {currentMac}")
                    continue

                #extrahujeme prvni dva znaky z mac adresy
                macFirstTwoValue = currentMac[:2]
                macFirstTwoValue = int(macFirstTwoValue, 16)
                if macFirstTwoValue % 2 != 0:
                    logging.error(f"MAC address is multicast/broadcast: {currentMac}")
                    continue

                try:
                    ip_object = ipaddress.ip_address(cells_text[ipv4Index])
                    if ip_object not in allowedNetwork:
                        logging.error(f"IP adresa {cuurentIpv4} doesn't belong into our network")
                        continue

                # v c# je to catch
                except ValueError:
                    logging.error(f"Wrong format of IP address: {cuurentIpv4}")
                    continue
    
    
                if tableLength != len(cells_text) or cells_text[hostnameIndex] == "" :
                    currentHostname = False
                elif "." in cells_text[hostnameIndex]:
                    cells_text[hostnameIndex] = cells_text[hostnameIndex].replace(".", "-")
                    currentHostname = cells_text[hostnameIndex]
                else:
                    currentHostname = cells_text[hostnameIndex]
                    
                if currentHostname:
                    if not re.match(dnsPattern, currentHostname):
                        currentHostname = False  # Text neprošel, tak ho zahodíme

                #ukladani uz do jakoby te tabulky
                table[currentMac] = {
                    "ipv4": cuurentIpv4,
                    "ipv6": cuurentIpv6,
                }
                
                #pokud je hostname tak ho prida
                if currentHostname:
                    table[currentMac]["hostname"] = currentHostname
else:
    print(f"Chyba při stahování stránky. Status kód: {response.status_code}")

print(table)
