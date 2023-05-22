from websocket import create_connection
from contextlib import closing
from random import random
import logging
logging.basicConfig(filename = 'market.log', filemode = 'w', format = '%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
from pycapital import Capital
import json
import time
from datetime import datetime, timedelta
import getpass
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler



NERO     = "\033[38;5;233m"
GIALLO   = "\033[38;5;226m"
BLU      = "\033[38;5;27m"
VERDE    = "\033[0;32m"
ROSSO    = "\033[0;31m"
BIANCO   = "\033[0;97m"
GRIGIO   = "\033[38;5;244m"
PANNA    = "\033[38;5;188m"
RESET    = "\033[0m"
ROSSO_FG = "\033[0;41m"
VERDE_FG = "\033[48;5;40m"
BOLD     = "\033[1m"


logo = f"""{PANNA}

                              ███ █   █ ███   █   █ ███ ███ █ █ ███ ███   ███ █   █ ███ ███
                              █   █   █ █     ██ ██ █ █ █ █ █ █ █    █     █  ██  █ █   █ █
                              █   █ █ █  █    █ █ █ █ █ ██  ██  ███  █     █  █ █ █ ███ █ █
                              █   ██ ██   █   █   █ ███ █ █ █ █ █    █     █  █  ██ █   █ █
                              ███ █   █ ███   █   █ █ █ █ █ █ █ ███  █    ███ █   █ █   ███                          
<════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════>{RESET}
"""
def sendPing(client, ws):
	client.getToken()
	CST = client.CST
	TOKEN = client.TOKEN
	ping ={
		"destination": "ping",
		"correlationId": 1,
		"cst": f"{CST}",
		"securityToken": f"{TOKEN}"
	}
	ping = json.dumps(ping)
	ws.send(ping)
	response = ws.recv()
	logging.info(str(response))	

def _sendPing(client):
	client.getToken()
	CST = client.CST
	TOKEN = client.TOKEN
	with closing(create_connection('wss://api-streaming-capital.backend-capital.com/connect')) as ws:

		ping ={
			"destination": "ping",
			"correlationId": 1,
			"cst": f"{CST}",
			"securityToken": f"{TOKEN}"
		}

		ping = json.dumps(ping)
		ws.send(ping)
		response = ws.recv()
		logging.info(str(response))
		#response = json.loads(response)


def cliMarket(response, stocks, UP, CLR):


	colonne = [UP," Time","Symbol","Company Name","$ Price","% Chg","  News",CLR]
	print("{}{:<20} {:<20}  {:<25} {:<20} {:<20} {:<20}{}\n".format(*colonne))


	epic = response['payload']['epic']

	tStamp     = response['payload']['timestamp']
	tStamp     = datetime.fromtimestamp(int(str(tStamp)[:10]))
	timeString = tStamp.strftime( "%H:%M:%S" )

	#float price
	price = response['payload']['bid']

	if epic not in stocks:
		stocks[epic]['price']  = price
		stocks[epic]['time']   = tStamp
		stocks[epic]['lprice'] = 0
	else:
		stocks[epic]['lprice'] = stocks[epic]['price']
		stocks[epic]['price']  = price
		stocks[epic]['time']   = timeString


	for stock,value in stocks.items():

		MAX_LEN = 12
		nSpace  = MAX_LEN - len(str(value['price']))

		if value['price'] > value['lprice']:
			price = f"{VERDE_FG}{NERO}{BOLD}{value['price']} {nSpace*' '}{RESET}"

		else:
			price = f"{ROSSO_FG}{NERO}{BOLD}{value['price']} {nSpace*' '}{RESET}"


		stock_list = [value['time'], stock, value['name'], price, value['chg'], value['news']]

		# CALCOLO LA LUNGHEZZA DEL CODICE ANSI PER AVERE UNA SPAZIATURA DINAMICA
		len_colorazione = len(price)
		len_cifra = len(str(value['price'])) + nSpace

		formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
		print(formatsting.format(*stock_list))

	time.sleep(0.5)




email = input('Insert your capital.com email: ')
pssw =  getpass.getpass("Insert your password:")
api_key =  getpass.getpass("Insert your api key:")
client = Capital(email, pssw, api_key)
CST = client.CST
TOKEN = client.TOKEN


with open("epic.txt","r+") as file:

    elencoEpic = []
    stocks = {}
    count = 1

    for line in file.readlines():
        epic = line.split('#')[0].strip()
        epicName = line[:-1].split('#')[-1].strip()
        elencoEpic.append(epic)
        stocks[epic] = {'time':"00:00:00",'name':epicName,'price':0,'lprice':0,'chg':0,'vol':0,'news':0}
        print("{:<3} {:<20}".format(elencoEpic.index(epic),epicName[:15]),end = '')
        if count == 8:
            count = 0
            print()
        count += 1


seleioneUtente = input("\n\nScrivi i numeri degli asset desiserati separandoli con uno spazio: ")
epics = [elencoEpic[int(sel)] for sel in seleioneUtente.split()]
stocks = { k:v for k,v in stocks.items() if k in epics}

os.system("cls||clear")

# scheduler = BackgroundScheduler()
# scheduler.add_job(sendPing, 'interval', minutes=2, id='ping', args=[client])
# scheduler.start()
# #logging.getLogger('apscheduler.executors.default').propagate = False


with closing(create_connection('wss://api-streaming-capital.backend-capital.com/connect')) as ws:
	sub = {
		"destination": "marketData.subscribe",
		"correlationId": 1,
		"cst": f"{CST}",
		"securityToken": f"{TOKEN}",
		"payload": {"epics": epics}
	}

	sub = json.dumps(sub)
	ws.send(sub)

	numero_stock = len(stocks)+2
	UP     = f"\x1B[{numero_stock}A" # sposta il cursore in alto tanto quanto il numero_stock
	CLR    = "\x1B[0K"
	print(logo,"\n"*numero_stock)
	start = datetime.now()

	while True:
		response =  ws.recv()
		logging.info(str(response))
		response = json.loads(response)
		if response['destination'] == 'quote':
			cliMarket(response, stocks, UP, CLR)
		if (datetime.now() - timedelta(minutes=2)) > start:
			start = datetime.now()
			sendPing(client, ws)


