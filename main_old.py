import random
import time
from pycapital import Capital

logo = """

+-------------------------------------------------------------------------------------------------------------------+
|                           ███ █   █ ███   █   █ ███ ███ █ █ ███ ███   ███ █   █ ███ ███                           |
|                           █   █   █ █     ██ ██ █ █ █ █ █ █ █    █     █  ██  █ █   █ █                           |
|                           █   █ █ █  █    █ █ █ █ █ ██  ██  ███  █     █  █ █ █ ███ █ █                           |
|                           █   ██ ██   █   █   █ ███ █ █ █ █ █    █     █  █  ██ █   █ █                           | 
|                           ███ █   █ ███   █   █ █ █ █ █ █ █ ███  █    ███ █   █ █   ███                           |
+-------------------------------------------------------------------------------------------------------------------+
"""
numero_stock = 9


# DEFINISCO I CODICI ANSI

UP     = f"\x1B[{numero_stock}A" # sposta il cursore in alto tanto quanto il numero_stock
CLR    = "\x1B[0K"
VERDE  = "\033[0;32m"
ROSSO  = "\033[0;31m"
BIANCO = "\033[0;97m"

print("\n",logo,"\n"*numero_stock)

lastPrice = 0

while True:
   colonne = [UP,"  Time","Symbol","Company Name","Price","  %Chg","Volume","News",CLR]
   print("{}{:<20} {:<20}  {:<25} {:<20} {:<20} {:<20} {:<20}{}\n".format(*colonne))

   # NUMERI RANDOM E TIME DA PRINTARE PROVVISORIAMENTE
   v1 = random.randrange(1, 10)
   v2 = random.randrange(100, 200)
   vol1 = round(random.uniform(0.001,0.900),3)
   vol2 = round(random.uniform(0.001,0.900),3)
   named_tuple = time.localtime()
   time_string = time.strftime("%H:%M:%S", named_tuple)

   ask = random.randrange(1, 200)
   vol = random.randrange(100, 200)

   # DIZIONARIO COI VALORI DEGLI STOCK
   stocks = { "APPL":{'time':time_string,'name':'Apple Inc.','price':ask,'chg':v2,'vol':vol,'news':8},
              "MIB":{'time':time_string,'name':'FTSE MIB','price':ask,'chg':v1,'vol':vol,'news':10},
              "SP500":{'time':time_string,'name':'Standard & Poor 500','price':ask,'chg':v2,'vol':vol,'news':3},
              "BTC":{'time':time_string,'name':'Bitcoin','price':ask,'chg':v1,'vol':vol1,'news':5},
              "ETH":{'time':time_string,'name':'Ethereum','price':ask,'chg':v2,'vol':vol1,'news':6},
              "OIL":{'time':time_string,'name':'West Texas Intermediate','price':ask,'chg':v1,'vol':vol,'news':15},
              "GOLD":{'time':time_string,'name':'Gold/Dollaro','price':ask,'chg':v2,'vol':vol2,'news':2},
            }

   for stock,value in stocks.items():

      if value['price'] > lastPrice:
         price = f"{VERDE}{value['price']} ${BIANCO}" 
      else:
         price = f"{ROSSO}{value['price']} ${BIANCO}" 

      
      stock_list = [value['time'], stock, value['name'], price, value['chg'], value['vol'], value['news']]

      # CALCOLO LA LUNGHEZZA DEL CODICE ANSI PER AVERE UNA SPAZIATURA DINAMICA
      len_colorazione = len(price)
      len_cifra = len(str(value['price']))

      formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
      print(formatsting.format(*stock_list))

   lastPrice = ask
   time.sleep(1)
