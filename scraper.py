import requests
from bs4 import BeautifulSoup

URL = "https://www.su.nottingham.ac.uk/jobs/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id='web-scraper')
results = results.prettify()

file = open("templatenojobs.html", "r")
template = file.read()
file.close()

if(results != template):
    print("Page has changed")
    file = open("newpage.html", "w+")
    file.write(results)
    file.close()
