#Librerias API
from flask import Flask, jsonify, request, make_response
import urllib
import json
import os
#Librerias Web Scraping
from bs4 import BeautifulSoup
import urllib.request
import re
import requests
import pandas as pd

app = Flask(__name__)




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
    puntos = int(abs(round(new_negro-new_dolarBCV)) /1000)
    return new_negro, new_dolarBCV, puntos




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
        limpio.append('- ' + line[0:7] + ':' + ' ' + line[7:])
    return limpio

def ayer():
    url = "http://www.monitordolarvenezuela.com"
    response = requests.get(url)
    page=response.content
    soup = BeautifulSoup(page, 'html.parser')
    #print(soup)
    ayer = soup.find_all("div", {"class": "col-6 col-md-3 col-lg-3 ayer text-center"})
    ayerr = [item.text for item in ayer]
    limpio = []
    for line in ayerr:
        limpio.append('- ' + line[0:7] + ':' + ' ' + line[7:])
    return limpio


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("queryResult").get("action") == "input.bcv":
        result = req.get("queryResult")
        #pregunta = result.get("queryText")
        dolarBCV, fecha = scrapBCV()
        monitor = scrapMonitor()
        new_negro, new_dolarBCV, puntos = calcularpuntos(monitor, dolarBCV)
        if new_dolarBCV > new_negro:
            speech = ("El dolar BCV es de Bs {} para la fecha del {} 🤑.\n Está {} puntos por arriba del negro.\n El dolar BCV se actualiza diariamente.\n".format(dolarBCV,fecha, puntos))
        else:
            speech = ("El dolar BCV es de Bs {} para la fecha del {} 🤑.\n Está {} puntos por debajo del negro.\n El dolar BCV se actualiza diariamente.\n".format(dolarBCV,fecha, puntos))
        print("Response:")
        print(speech)
        return {'fulfillmentText': speech}
    if req.get("queryResult").get("action") == "input.negro":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        monitor = scrapMonitor()
        dolarBCV, fecha = scrapBCV()
        new_negro, new_dolarBCV, puntos = calcularpuntos(monitor, dolarBCV)
        if new_negro > new_dolarBCV:
            speech = ("El dolar Negro es de {} para la fecha del {} 🤑.\n Está {} puntos por arriba del BCV.\n El dolar negro se actualiza cada 30 minutos.\n".format(monitor,fecha, puntos))
        else:
            speech = ("El dolar Negro es de {} para la fecha del {} 🤑.\n Está {} puntos por debajo del BCV.\n El dolar negro se actualiza cada 30 minutos.\n".format(monitor,fecha, puntos))

        print("Response:")
        print(speech)
        return {'fulfillmentText': speech}
    if req.get("queryResult").get("action") == "input.promedios":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        listaa =[]
        titulos, numeros, porcentaje = promedios()
        for i in range(len(titulos)):
            listaa.append("- En *{}*: {} Bs, cambió {}\n".format(titulos[i],numeros[i], porcentaje[i] ))
        listToStr = ' '.join([str(elem) for elem in listaa]) 
        print("Response:")
        print(listToStr)
        return {'fulfillmentText': listToStr}
    if req.get("queryResult").get("action") == "input.hoy":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        listaa =[]
        lista = hoy()
        for i in range(len(lista)):
            listaa.append("{}\n".format(lista[i]))
        listToStr = ' '.join([str(elem) for elem in listaa]) 
        listToStr = "*Resumen del dólar negro de hoy* \n" + listToStr 
        print("Response:")
        print(listToStr)
        return {'fulfillmentText': listToStr}
    if req.get("queryResult").get("action") == "input.ayer":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        listaa =[]
        lista = ayer()
        for i in range(len(lista)):
            listaa.append("{}\n".format(lista[i]))
        listToStr = ' '.join([str(elem) for elem in listaa]) 
        listToStr = "*Resumen del dólar negro de ayer* \n" + listToStr 
        print("Response:")
        print(listToStr)
        return {'fulfillmentText': listToStr}
    if req.get("queryResult").get("action") == "input.DolaBs":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        parameters = result.get("parameters")
        tipodolar  = parameters.get("tipodolar")
        number  = parameters.get("number")
        dolarBCV, fecha = scrapBCV()
        monitor = scrapMonitor()
        new_negro, new_dolarBCV, puntos = calcularpuntos(monitor, dolarBCV)
        bcv_mult = round(new_dolarBCV*number)
        negro_mult = round(new_negro*number)
        bcv_mult = str(format(bcv_mult, ",.2f").replace(",", "X").replace(".", ",").replace("X", "."))
        negro_mult = str(format(negro_mult, ",.2f").replace(",", "X").replace(".", ",").replace("X", "."))
        print("Este es tipo dolar", tipodolar[0])
        print("Este es number", number)
        llave = str(tipodolar[0])
        tipocambio = {'BCV': {'precio':bcv_mult}, 'negro':{'precio':negro_mult} }
        speech = ("Serían {} Bs a tasa {} 💲 ".format(str(tipocambio[llave]['precio']),llave))
        print("Response:")
        print(speech)
        return {'fulfillmentText': speech}
    if req.get("queryResult").get("action") == "DolaresBolivaresRsp.DolaresBolivaresRsp-custom":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        parameters = result.get("parameters")
        tipodolar  = parameters.get("tipodolar")
        outputContexts = result.get("outputContexts")
        contexto = outputContexts[0]
        dolarBCV, fecha = scrapBCV()
        monitor = scrapMonitor()
        new_negro, new_dolarBCV, puntos = calcularpuntos(monitor, dolarBCV)
        bcv_mult = round(new_dolarBCV*float(contexto['parameters']['number']))
        negro_mult = round(new_negro*float(contexto['parameters']['number']))
        bcv_mult = str(format(bcv_mult, ",.2f").replace(",", "X").replace(".", ",").replace("X", "."))
        negro_mult = str(format(negro_mult, ",.2f").replace(",", "X").replace(".", ",").replace("X", "."))
        if (isinstance(tipodolar, str)):
            llave = str(tipodolar)
        else:
            llave = str(tipodolar[0])
        tipocambio = {'BCV': {'precio':bcv_mult}, 'negro':{'precio':negro_mult} }
        speech = ("Serían {} Bs a tasa {} 💲 ".format(str(tipocambio[llave]['precio']),llave))
        print('Estos son los parametros', float(contexto['parameters']['number']))
        print("Response:")
        print(speech)
        return {'fulfillmentText': speech}
    if req.get("queryResult").get("action") == "input.BsaDolares":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        parameters = result.get("parameters")
        tipodolar  = parameters.get("tipodolar")
        number  = parameters.get("number")
        number = str(number)
        counter = number.count('.') 
        if counter > 1:
            number = number.replace('.', '') 
            number = float(number)
            number = number / 10
        print("number despues del replace", number)
        print("number despues del replace haciendole float", float(number))

        dolarBCV, fecha = scrapBCV()
        monitor = scrapMonitor()
        new_negro, new_dolarBCV, puntos = calcularpuntos(monitor, dolarBCV)
        bcv_mult = float(number) / new_dolarBCV
        negro_mult = float(number) / new_negro
        bcv_mult = str(round(bcv_mult , 2))
        bcv_mult = bcv_mult.replace('.', ',') 
        negro_mult = str(round(negro_mult , 2))
        negro_mult = negro_mult.replace('.', ',') 
        print("Este es tipo dolar", tipodolar[0])
        print("Este es number", number)
        if (isinstance(tipodolar, str)):
            llave = str(tipodolar)
        else:
            llave = str(tipodolar[0])
        tipocambio = {'BCV': {'precio':bcv_mult}, 'negro':{'precio':negro_mult} }
        speech = ("Serían {} $ a tasa {} 💲 ".format(str(tipocambio[llave]['precio']),llave))
        print("Response:")
        print(speech)
        return {'fulfillmentText': speech}
    if req.get("queryResult").get("action") == "BolivaresaDolaresRsp.BolivaresaDolaresRsp-custom":
        result = req.get("queryResult")
        pregunta = result.get("queryText")
        parameters = result.get("parameters")
        tipodolar  = parameters.get("tipodolar")
        outputContexts = result.get("outputContexts")
        contexto = outputContexts[0]
        dolarBCV, fecha = scrapBCV()
        monitor = scrapMonitor()
        new_negro, new_dolarBCV, puntos = calcularpuntos(monitor, dolarBCV)
        bcv_mult =  float(contexto['parameters']['number']) / new_dolarBCV
        negro_mult = float(contexto['parameters']['number']) / new_negro

        bcv_mult = str(round(bcv_mult , 2))
        bcv_mult = bcv_mult.replace('.', ',') 
        negro_mult = str(round(negro_mult , 2))
        negro_mult = negro_mult.replace('.', ',') 
        if (isinstance(tipodolar, str)):
            llave = str(tipodolar)
        else:
            llave = str(tipodolar[0])
        tipocambio = {'BCV': {'precio':bcv_mult}, 'negro':{'precio':negro_mult} }
        speech = ("Serían {} $ a tasa {} 💲 ".format(str(tipocambio[llave]['precio']),llave))
        print('Estos son los parametros', float(contexto['parameters']['number']))
        print("Response:")
        print(speech)
        return {'fulfillmentText': speech}


"""
    parameters = result.get("parameters")
    zone  = parameters.get("tipodolar")
    print("este es zone", zone)
    llave = str(zone)
    print('Este es queryText', result.get("queryText") )
    dolar, fecha = scrapBCV()
    monitor = scrapMonitor()

    tipocambio = {'BCV': {'precio':dolar,'fecha':fecha}, 'negro':{'precio':monitor, 'fecha':fecha +' horas'} }
    speech = "El dolar " + zone + " es " + str(tipocambio[llave]['precio']) + " para la fecha del " + str(tipocambio[llave]['fecha'] + ' 🤑')
    print("Response:")
    print(speech)
    return {'fulfillmentText': speech}
"""

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)




