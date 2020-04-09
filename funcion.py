from bs4 import BeautifulSoup
import urllib.request
import requests
import re
import pandas as pd
import json
from apscheduler.scheduler import Scheduler
from datetime import datetime



def promedios():
    url = "http://www.monitordolarvenezuela.com"
    response = requests.get(url)
    page=response.content
    soup = BeautifulSoup(page, 'html.parser')
    #print(soup)
    dolars = soup.find("div", {"class": "box-cont"})
    items = dolars.find_all("div", {"class": "box-prices row"})

    nombres_titulos = [item.find("div", {"class": "col-12 col-lg-5"}).get_text() for item in items]
    nombres_numeros = [item.find("div", {"class": "col-6 col-lg-4"}).get_text().replace("www.monitordolarvenezuela.com", "", 1) for item in items]
    nombres_porcentajes = [item.find("div", {"class": "col-4 col-lg-2 text-center"}).get_text() for item in items]

    #print(nombres_titulos)
    #print(nombres_numeros)
    #print(nombres_porcentajes)
    return nombres_titulos, nombres_numeros, nombres_porcentajes


def hoy():
    url = "http://www.monitordolarvenezuela.com"
    response = requests.get(url)
    page=response.content
    soup = BeautifulSoup(page, 'html.parser')
    #print(soup)
    dolars2 = soup.find("div", {"class": "box-style comparativa row"})
    items2 = dolars2.find_all("div", {"class": "col-6 col-md-3 col-lg-3 hoy text-center"})
    hoy = [item.text for item in items2]
    limpio = []
    for line in hoy:
        limpio.append('-' + line[0:7] + ':' + ' ' + line[7:])
    return limpio

def scrapBCV():
    url = "http://www.bcv.org.ve"
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    regex = re.compile('^')
    content_lis = soup.find("div", {"id": "dolar"})
    content_date = soup.find("span", {"class" :"date-display-single"})
    fecha = content_date.text
    dolar = content_lis.div.strong.text.strip()
    imp = print('Dolar BCV : {} para la fecha : {}'.format(dolar, fecha))
    return dolar, fecha

def scrapMonitor():
    url2 = "https://monitordolarvenezuela.com/monitor-dolar-hoy"
    response = requests.get(url2)
    page=response.content
    soup = BeautifulSoup(page, 'html.parser')
    hoy = soup.find("div", {"itemprop": "articleBody"})
    nombre = hoy.find("h2", {"class": "text-center"}).get_text()
    return nombre

cron = Scheduler(daemon=True)
cron.start()
@cron.interval_schedule(seconds=10)
def calcularpuntos(monitor, dolarBCV):
    #float del monitor
    monitorsep = monitor.split()
    new_str = monitorsep[1].replace('.', '') 
    new_str = new_str.replace(',', '.')
    new_negro = float(new_str)
    #float del BCV
    new_dolarBCV = dolarBCV.replace('.', '') 
    new_dolarBCV = new_dolarBCV.replace(',', '.')
    new_dolarBCV = float(new_dolarBCV)
    #calulo de puntos
    puntos = int(abs(int(new_negro-new_dolarBCV)) /1000)
    if new_negro > new_dolarBCV:
        print('El dolar negro está {} puntos por arriba del BCV'.format(puntos))
    else:
        print('El dolar negro está {} puntos por debajo del BCV'.format(puntos))


def DolaresaBolivares(monitor, dolarBCV):
    #float del monitor
    monitorsep = monitor.split()
    new_str = monitorsep[1].replace('.', '') 
    new_str = new_str.replace(',', '.')
    new_negro = float(new_str)
    #float del BCV
    new_dolarBCV = dolarBCV.replace('.', '') 
    new_dolarBCV = new_dolarBCV.replace(',', '.')
    new_dolarBCV = float(new_dolarBCV)
    #calulo de puntos
    mult = query*new_negro





if __name__ == '__main__':
    """    listaa =[]
    titulos, numeros, porcentaje = promedios()
    for i in range(len(titulos)):
        listaa.append("En *{}*: {} Bs, cambió {}\n".format(titulos[i],numeros[i], porcentaje[i] ))
    listToStr = ' '.join([str(elem) for elem in listaa]) 
    
    hola = hoy()
        print(hola)  """
    monitor = scrapMonitor()
    dolarBCV, fecha = scrapBCV()
    #calcularpuntos(monitor, dolarBCV)

    bcv = {
    'dolarBCV': dolarBCV,
    'fecha': fecha
    }

    negro = {
    'dolarBCV': monitor,
    'fecha': fecha
    }

    with open('bcv.json', 'w') as json_file:
        json.dump(bcv, json_file)


    
    with open('negro.json') as f:
        data = json.load(f)
        
    print("la data del negro es: ", data['dolarBCV'])

    

