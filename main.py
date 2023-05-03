import random, time



logo = """ 
+-------------------------------------------------------------------------------------------------------------------+
|                                                                                                                   |    
|                    ██████╗██╗    ██╗███████╗    ███████╗████████╗ ██████╗  ██████╗██╗  ██╗                        |
|                   ██╔════╝██║    ██║██╔════╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝                        |
|                   ██║     ██║ █╗ ██║███████╗    ███████╗   ██║   ██║   ██║██║     █████╔╝                         | 
|                   ██║     ██║███╗██║╚════██║    ╚════██║   ██║   ██║   ██║██║     ██╔═██╗                         |
|                   ╚██████╗╚███╔███╔╝███████║    ███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗                        |
|                    ╚═════╝ ╚══╝╚══╝ ╚══════╝    ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝                        |
|                                                                                                                   |
+-------------------------------------------------------------------------------------------------------------------+
"""

numero_stock = 8


# DEFINISCO I CODICI ANSI

UP     = f"\x1B[{numero_stock}A" # sposta il cursore in alto tanto quanto il numero_stock
CLR    = "\x1B[0K"
VERDE  = "\033[0;32m"
ROSSO  = "\033[0;31m"
BIANCO = "\033[0;97m"

print("\n",logo,"\n"*numero_stock)

while True:
   colonne = [UP,"  Time","Symbol","Company Name", "%Chg","Volume","News",CLR]
   print("{}{:<20} {:<20}  {:<25} {:<20} {:<20} {:<20}{}".format(*colonne))

   # NUMERI RANDOM E TIME DA PRINTARE PROVVISORIAMENTE
   v1 = random.randrange(1, 10)
   v2 = random.randrange(100, 200)
   vol1 = round(random.uniform(0.001,0.900),3)
   vol2 = round(random.uniform(0.001,0.900),3)
   named_tuple = time.localtime()
   time_string = time.strftime("%H:%M:%S", named_tuple)

   # DIZIONARIO COI VALORI DEGLI STOCK
   stocks = { "APPL":{'time':time_string,'name':'Apple Inc.','chg':v2,'vol':vol1,'news':8},
              "MIB":{'time':time_string,'name':'FTSE MIB','chg':v1,'vol':vol2,'news':10},
              "SP500":{'time':time_string,'name':'Standard & Poor 500','chg':v2,'vol':vol2,'news':3},
              "BTC":{'time':time_string,'name':'Bitcoin','chg':v1,'vol':vol1,'news':5},
              "ETH":{'time':time_string,'name':'Ethereum','chg':v2,'vol':vol1,'news':6},
              "OIL":{'time':time_string,'name':'West Texas Intermediate','chg':v1,'vol':vol1,'news':15},
              "GOLD":{'time':time_string,'name':'Gold/Dollaro','chg':v2,'vol':vol2,'news':2},
            }

   for stock,value in stocks.items():

      if value['chg']%2 == 0:
         chg = f"{VERDE}{value['chg']}%{BIANCO}" 
      else:
         chg = f"{ROSSO}{value['chg']}%{BIANCO}" 


      stock_list = [value['time'], stock, value['name'], chg, value['vol'], value['news']]

      # CALCOLO LA LUNGHEZZA DEL CODICE ANSI PER AVERE UNA SPAZIATURA DINAMICA
      len_colorazione = len(chg)
      len_cifra = len(str(value['chg']))

      formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
      print(formatsting.format(*stock_list))


   time.sleep(1)
