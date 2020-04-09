from apscheduler.scheduler import Scheduler
from flask import Flask
from bs4 import BeautifulSoup
import urllib.request
import requests
import re
import pandas as pd
import json
import atexit
app = Flask(__name__)

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

@cron.interval_schedule(seconds=10)
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


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    app.run()