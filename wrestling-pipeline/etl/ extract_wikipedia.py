
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/api/rest_v1/page/html/List_of_WWE_Champions"

html = requests.get(url).text

soup = BeautifulSoup(html, "html.parser")

tables = soup.find_all("table")

champions = []

for table in tables:

    rows = table.find_all("tr")

    for row in rows[1:]:

        cols = row.find_all(["td", "th"])

        if len(cols) >= 2:

            champions.append({
                "champion": cols[0].text.strip(),
                "reign": cols[1].text.strip()
            })

df = pd.DataFrame(champions)

df.to_csv(
    "../data/raw/champions.csv",
    index=False
)