import requests
from bs4 import BeautifulSoup
from datetime import datetime

concursos = {
    "tjto22": {},
    "tceto22": {},
    "senado22/1": {},
    "senado22/2": {},
    "senado22/3": {},
    "senado22/4": {},
}

for concurso in concursos:
    url = f"https://conhecimento.fgv.br/concursos/{concurso}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    h1_element = soup.find("h1", id="page-title")
    table_element = soup.find("table")
    tr_element = table_element.find_all("tr")[1]
    td_elements = tr_element.find_all("td")
    concursos[concurso]["nome"] = h1_element.text.strip().removeprefix("Concurso Público para o ")
    concursos[concurso]["data"] = datetime.strptime(td_elements[0].text, "%d/%m/%Y")
    concursos[concurso]["texto"] = td_elements[1].text
    

for c in sorted(concursos.items(), key=lambda x: x[1]["data"], reverse=True):
    print("# [{}](./{}/)".format(c[1]["nome"], c[0].replace("/", "-")))
    print("{}: {}\n".format(c[1]["data"].strftime("%d/%m/%Y"), c[1]["texto"]))