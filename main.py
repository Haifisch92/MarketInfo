import random, time

print() 

logo = """ 
      +------------------------------------------------------------------------------------------------------+
      |           ██████╗██╗    ██╗███████╗    ███████╗████████╗ ██████╗  ██████╗██╗  ██╗                    |
      |          ██╔════╝██║    ██║██╔════╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝                    |
      |          ██║     ██║ █╗ ██║███████╗    ███████╗   ██║   ██║   ██║██║     █████╔╝                     |
      |          ██║     ██║███╗██║╚════██║    ╚════██║   ██║   ██║   ██║██║     ██╔═██╗                     |
      |          ╚██████╗╚███╔███╔╝███████║    ███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗                    |
      |           ╚═════╝ ╚══╝╚══╝ ╚══════╝    ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝                    |
      +------------------------------------------------------------------------------------------------------+
"""

UP     = "\x1B[3A"
CLR    = "\x1B[0K"
VERDE  = "\033[0;32m"
ROSSO  = "\033[0;31m"
BIANCO = "\033[0;97m"

print(logo,"\n\n")

while True:
   colonne = ["  Time","Symbol","Company Name", "%Chg","Volume","News"]
   print("\x1B[3A{:<20} {:<20}  {:<25} {:<20} {:<20} {:<20}\x1B[0K".format(*colonne))


   orders = random.randrange(1, 10)
   operations = random.randrange(100, 200)
   vol1 = round(random.uniform(0.001,0.900),3)
   vol2 = round(random.uniform(0.001,0.900),3)


   named_tuple = time.localtime()
   time_string = time.strftime("%H:%M:%S", named_tuple)

   if orders%2 == 0:
      val1 = f"{VERDE}{orders}%{BIANCO}" 
   else:
      val1 = f"{ROSSO}{orders}%{BIANCO}" 

   if operations%2 == 0:
      val2 = f"{VERDE}{operations}%{BIANCO}"
   else:
      val2 = f"{ROSSO}{operations}%{BIANCO}"



   appl = [time_string,"APPL","Apple Inc.",val2,vol1,"8"]
   len_colorazione = len(val2)
   len_cifra = len(str(operations))
   formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
   print(formatsting.format(*appl))

   sp = [time_string,"SP500","Standard & Poor 500",val1,vol2,"16"]
   len_colorazione = len(val1)
   len_cifra = len(str(orders))
   formatsting = "{:<20} {:<20}  {:<25} {:<%s} {:<20} {:<20}%s"%(len_colorazione+20-len_cifra,CLR)
   print(formatsting.format(*sp))



   time.sleep(1)
