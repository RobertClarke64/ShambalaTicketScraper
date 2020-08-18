import requests
from bs4 import BeautifulSoup

URL = "https://www.su.nottingham.ac.uk/jobs/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id='web-scraper')

file = open("templatenojobs.html", "w+")
template = file.write(results.prettify())
file.close()
