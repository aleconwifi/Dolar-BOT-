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



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("queryResult").get("action") != "input.welcome":
        return {}
    result = req.get("queryResult")
    parameters = result.get("parameters")
    zone  = parameters.get("tipodolar")
    print("este es zone", zone[0])
    llave = str(zone[0])

    dolar, fecha = scrapBCV()
    monitor = scrapMonitor()

    tipocambio = {'BCV': {'precio':dolar,'fecha':fecha}, 'negro':{'precio':monitor, 'fecha':fecha +' horas'} }
    speech = "El dolar " + zone[0] + " es " + *str(tipocambio[llave]['precio'])* + " para la fecha del " + str(tipocambio[llave]['fecha'] + ' 🤑')
    print("Response:")
    print(speech)
    return {'fulfillmentText': speech}


if __name__ == '__main__':
    #print('este es monitor ', nombre)
    app.run(host='127.0.0.1', port=80, debug=True)




