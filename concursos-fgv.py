import argparse
import os
import json
import requests
import zlib
from bs4 import BeautifulSoup
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--token", type=str, help="Telegram bot authentication token")
args = parser.parse_args()

basename = os.path.splitext(os.path.basename(__file__))[0]

with open(f"{basename}.json", "r") as json_file_r:
    json_concursos = json.load(json_file_r)
    tmp_concursos = {}

for concurso in json_concursos:
    tmp_concursos[concurso] = {}
    url = f"https://conhecimento.fgv.br/concursos/{concurso}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    h1_element = soup.find("h1")
    table_element = soup.find("table")
    tr_element = table_element.find_all("tr")[1]
    td_elements = tr_element.find_all("td")
    td_p_elements = td_elements[1].find_all("p")
    tmp_concursos[concurso]["nome"] = h1_element.text.strip()[24:]
    tmp_concursos[concurso]["data"] = datetime.strptime(td_elements[0].text, "%d/%m/%Y")
    tmp_concursos[concurso]["crc32"] = hex(zlib.crc32(table_element.text.encode()) & 0xffffffff)
    tmp_concursos[concurso]["texto"] = td_p_elements[0].text if len(td_p_elements) > 0 else td_elements[1].text
    #
    if args.token:
        if json_concursos[concurso] != tmp_concursos[concurso]["crc32"]:
            message = requests.utils.quote("A página do Concurso Público para o(a) {} ({}) foi atualizada\n\n{}: {}\n\nhttps://conhecimento.fgv.br/concursos/{}".format(tmp_concursos[concurso]["nome"], concurso, tmp_concursos[concurso]["data"].strftime("%d/%m/%Y"), tmp_concursos[concurso]["texto"], concurso))
            url_bot = f"https://api.telegram.org/bot{args.token}/sendMessage?chat_id=@rankingsFGV&text={message}"
            requests.get(url_bot)
    json_concursos[concurso] = tmp_concursos[concurso]["crc32"]
    
with open(f"{basename}.json", "w") as json_file_w:
    json.dump(json_concursos, json_file_w, indent=4, default=str)

print("# Concursos")

for c in sorted(tmp_concursos.items(), key=lambda x: x[1]["data"], reverse=True):
    print("\n## [{}](./{}/) *({})*".format(c[1]["nome"], c[0].replace("/", "-"), c[0]))
    print("{}: {}".format(c[1]["data"].strftime("%d/%m/%Y"), c[1]["texto"]))
