import requests
from bs4 import BeautifulSoup
import re

URL = 'https://www.lamoncloa.gob.es/multimedia/videos/presidente/Paginas/2020/directo.aspx'

#'https://www.lamoncloa.gob.es/multimedia/videos/consejoministros/Paginas/directo.aspx'

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'html5lib') 
soup_div = soup.find("div", {"id": "div_video_contenedor"})

ss = str(soup_div)

urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ss)
print(urls[0].translate({ord(i): None for i in ',\''}))
