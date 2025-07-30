import asyncio
import websockets
from pycapital import Capital
import json
from datetime import datetime, timedelta
import getpass
import os
import logging

GIALLO = "\033[38;5;226m"
BLU    = "\033[38;5;27m"
VERDE  = "\033[0;32m"
ROSSO  = "\033[0;31m"
BIANCO = "\033[0;97m"
GRIGIO = "\033[38;5;244m"
PANNA    = "\033[38;5;188m"


logo = f"""{PANNA}

                              ███ █   █ ███   █   █ ███ ███ █ █ ███ ███   ███ █   █ ███ ███
                              █   █   █ █     ██ ██ █ █ █ █ █ █ █    █     █  ██  █ █   █ █
                              █   █ █ █  █    █ █ █ █ █ ██  ██  ███  █     █  █ █ █ ███ █ █
                              █   ██ ██   █   █   █ ███ █ █ █ █ █    █     █  █  ██ █   █ █
                              ███ █   █ ███   █   █ █ █ █ █ █ █ ███  █    ███ █   █ █   ███                                     
{PANNA}<════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════>{BIANCO}
"""

async def clientws(queue,CST,TOKEN,epics):
    async with websockets.connect('wss://api-streaming-capital.backend-capital.com/connect') as ws:


        sub = {
                "destination": "marketData.subscribe",
                "correlationId": 1,
                "cst": f"{CST}",
                "securityToken": f"{TOKEN}",
                "payload": {"epics": epics}
              }

        sub = json.dumps(sub)
        await ws.send(sub)
        response = await ws.recv()
        response = json.loads(response)

        while True:
            response = await ws.recv()
            response = json.loads(response)
            if response['destination'] == 'quote':
                #print("send to queue")
                await queue.put(response)

            #print(response)
            #await sendPing(ws, client)


async def sendPing(client):
    client.getToken()
    CST = client.CST
    TOKEN = client.TOKEN
    async with websockets.connect('wss://api-streaming-capital.backend-capital.com/connect') as ws:

        ping ={
                "destination": "ping",
                "correlationId": 1,
                "cst": f"{CST}",
                "securityToken": f"{TOKEN}"
              }

        ping = json.dumps(ping)
        await ws.send(ping)
        response = await ws.recv()
        #print(response)
        #response = json.loads(response)


async def cliMarket(queue, stocks):

    numero_stock = len(stocks)+2

    UP     = f"\x1B[{numero_stock}A" # sposta il cursore in alto tanto quanto il numero_stock
    CLR    = "\x1B[0K"


    print(logo,"\n"*numero_stock)

    while True:
        #break
        colonne = [UP,"Time","Symbol","Company Name","$ Price","% Chg","News",CLR]
        print("{}{:<20} {:<20}  {:<25} {:<20} {:<20} {:<20}{}\n".format(*colonne))

        response = await queue.get()
        if response is None:
            break

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

            if value['price'] > value['lprice']:
                price = f"{VERDE}{value['price']}{BIANCO}"
            else:
                price = f"{ROSSO}{value['price']}{BIANCO}"


            stock_list = [value['time'], stock, value['name'], price, value['chg'], value['news']]

            # CALCOLO LA LUNGHEZZA DEL CODICE ANSI PER AVERE UNA SPAZIATURA DINAMICA
            len_colorazione = len(price)
            len_cifra = len(str(value['price']))

            formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
            print(formatsting.format(*stock_list))

        await asyncio.sleep(0.5)



async def main(client, CST, TOKEN, epics, stocks):

    queue = asyncio.Queue()
    await asyncio.gather(clientws(queue,CST,TOKEN,epics), cliMarket(queue,stocks))


email = input('Insert your capital.com email: ')
pssw =  getpass.getpass("Insert your password:")
api_key =  getpass.getpass("Insert your api key:")


client = Capital(email, pssw, api_key)
CST = client.CST
TOKEN = client.TOKEN
# client.selezioneEpic()
with open("epic2.txt","r+") as file:

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
newstocks = { k:v for k,v in stocks.items() if k in epics}
# print(selezioneEpic)
# print(newstocks)
# epics = ["OIL_CRUDE","NATURALGAS","GOLD"]

logging.getLogger('apscheduler.executors.default').propagate = False

os.system("cls||clear")

try:
    asyncio.run(main(client,CST, TOKEN, epics, newstocks))
except asyncio.CancelledError:
    client.session.close()
