from random import random
import asyncio
import websockets
from pycapital import Capital
import json
import time
from datetime import datetime
import getpass
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
 

logo = """
                             ███ █   █ ███   █   █ ███ ███ █ █ ███ ███   ███ █   █ ███ ███                           
                             █   █   █ █     ██ ██ █ █ █ █ █ █ █    █     █  ██  █ █   █ █                           
                             █   █ █ █  █    █ █ █ █ █ ██  ██  ███  █     █  █ █ █ ███ █ █                           
                             █   ██ ██   █   █   █ ███ █ █ █ █ █    █     █  █  ██ █   █ █                            
                             ███ █   █ ███   █   █ █ █ █ █ █ █ ███  █    ███ █   █ █   ███                            
<===================================================================================================================>
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
            await queue.put(response)


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
        #response = await ws.recv()
        #response = json.loads(response)



async def cliMarket(queue):

    stocks = { 
               "NATURALGAS":{'time':" 00:00:00",'name':'Natural Gas','price':0,'lprice':0,'chg':0,'vol':0,'news':6},
               "OIL_CRUDE":{'time':" 00:00:00",'name':'West Texas Intermediate','price':0,'lprice':0,'chg':0,'vol':0,'news':15},
               "GOLD":{'time':" 00:00:00",'name':'Gold/Dollaro','price':0,'lprice':0,'chg':0,'vol':0,'news':2},
             }

    numero_stock = len(stocks)+2

    UP     = f"\x1B[{numero_stock}A" # sposta il cursore in alto tanto quanto il numero_stock
    CLR    = "\x1B[0K"
    VERDE  = "\033[0;32m"
    ROSSO  = "\033[0;31m"
    BIANCO = "\033[0;97m"

    print(logo,"\n"*numero_stock)

    while True:

        colonne = [UP,"  Time","Symbol","Company Name","$ Price","% Chg"," News",CLR]
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
            stocks[epic]['time']   = " "+timeString


        for stock,value in stocks.items():

            if value['price'] > value['lprice']:
                price = f"{VERDE}{value['price']} {BIANCO}" 
            else:
                price = f"{ROSSO}{value['price']} {BIANCO}" 

      
            stock_list = [value['time'], stock, value['name'], price, value['chg'], value['news']]

            # CALCOLO LA LUNGHEZZA DEL CODICE ANSI PER AVERE UNA SPAZIATURA DINAMICA
            len_colorazione = len(price)
            len_cifra = len(str(value['price']))

            formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
            print(formatsting.format(*stock_list))

        time.sleep(0.5)
        
 

async def main(CST, TOKEN, epics):

    queue = asyncio.Queue()
    await asyncio.gather(clientws(queue,CST,TOKEN,epics), cliMarket(queue))
 

email = input('Insert your capital.com email: ')
pssw =  getpass.getpass("Insert your password:")
api_key =  getpass.getpass("Insert your api key:")
client = Capital(email, pssw, api_key)
CST = client.CST
TOKEN = client.TOKEN

epics = ["OIL_CRUDE","NATURALGAS","GOLD"]

loop = asyncio.get_event_loop()

scheduler = AsyncIOScheduler()
scheduler.add_job(sendPing, 'interval', minutes=2, id='ping', args=[client])
scheduler.start()

os.system("cls||clear")

task = loop.create_task(main(CST, TOKEN, epics))

try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    client.session.close()