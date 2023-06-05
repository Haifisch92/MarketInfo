import requests
import json
import pandas
import base64
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import time
import logging



logging.basicConfig(level=logging.INFO)

nodi_forex = {"forex più negoziati":"hierarchy_v1.currencies.most_traded","forex USD":"hierarchy_v1.currencies.usd","forex EUR":"hierarchy_v1.currencies.eur",
              "forex JPG":"hierarchy_v1.currencies.jpy","forex GBP":"hierarchy_v1.currencies.gbp","forex AUD":"hierarchy_v1.currencies.aud",
              "forex CAD":"hierarchy_v1.currencies.cad","forex CHF":"hierarchy_v1.currencies.chf","forex CNH":"hierarchy_v1.currencies.cnh",
              "forex HKD":"hierarchy_v1.currencies.hkd","forex TRY":"hierarchy_v1.currencies.try","forex DKK":"hierarchy_v1.currencies.dkk",
              "forex PLN":"hierarchy_v1.currencies.pln"}

nodi_titoli = {"Azioni popolari":"hierarchy_v1.shares.popular_shares","Azioni Stati Uniti":"hierarchy_v1.shares.us",
               "Azioni Regno Unito":"hierarchy_v1.shares.gb","Azioni Germania":"hierarchy_v1.shares.de",
               "Azioni Francia":"hierarchy_v1.shares.fr","Azioni Hong Kong":"hierarchy_v1.shares.hk","Azioni Italia":"hierarchy_v1.shares.it",
               "Azioni Norvegia":"hierarchy_v1.shares.no","Azioni Spagna":"hierarchy_v1.shares.es",
               "Azioni Svezia":"hierarchy_v1.shares.se","Azioni Svizzera":"hierarchy_v1.shares.ch",
               "Azioni Canada":"hierarchy_v1.shares.ca","Azioni Paesi Bassi":"hierarchy_v1.shares.nl",
               "Azioni Irlanda":"hierarchy_v1.shares.ie","Azioni Giappone":"hierarchy_v1.shares.jp",
               "Azioni Singapore":"hierarchy_v1.shares.sg","Azioni Australia":"hierarchy_v1.shares.au"}

nodi = {
    'forex':nodi_forex,
    'Azioni':nodi_titoli,
    'crypto':"hierarchy_v1.crypto_currencies",
    'indici':"hierarchy_v1.indices",
    'comodities':"hierarchy_v1.commodities"
}


class FinancialTools():


    def stoch(self, df, k_period=14, d_period=3):
        
        n_height = df['high'].rolling(k_period).max()
        n_low    = df['low'].rolling(k_period).min()
        K        = (df['close'] - n_low) * 100 / (n_height - n_low)

        # WRITE K&D TO DF
        df['K']  = K.rolling(3).mean()
        df['D']  = df['K'].rolling(d_period).mean()
        
        return df


    def mm(self, df, periodo=10):

        df[f'ma{periodo}'] = df["close"].rolling(periodo).mean()
        
        return df


    def keltner(self, df, kc_lookback=20, multiplier=2, atr_lookback=10):

        tr1    = df['high'] - df['low']
        tr2    = abs(df['high'] - df['close'].shift())
        tr3    = abs(df['low'] - df['close'].shift())
        frames = [tr1, tr2, tr3]
        tr     = pandas.concat(frames, axis = 1, join = 'inner').max(axis = 1)
        atr    = tr.ewm(alpha = 1/atr_lookback).mean()

        # WRITE KELTNER BAND TO DF
        df['kc_middle'] = df['close'].ewm(kc_lookback).mean()
        df['kc_upper']  = df['close'].ewm(kc_lookback).mean() + multiplier * atr
        df['kc_lower']  = df['close'].ewm(kc_lookback).mean() - multiplier * atr

        return df




class Connection():

    def __init__(self):

        self.session = requests.Session()

    def httpRequest(self, method: str, url: str, endpoint: str, payload) -> str:

        """Handle request to Capital.com, made request two time because token after
           ten minute are burned"""

        headers = {
            'X-SECURITY-TOKEN': self.TOKEN,
            'CST': self.CST,
            'Content-Type': 'application/json'}

        response = self.session.request(method, url+endpoint, headers=headers, data=payload)

        if response.status_code != 200:

            self.getToken()
            headers['X-SECURITY-TOKEN'] = self.TOKEN
            headers['CST'] = self.CST
            response = self.session.request(method, url+endpoint, headers=headers, data=payload)

        return response.text

    def getData(self,api_key: str) -> tuple[str, int]:

        """ Take encryption key and timestamp """

        response = self.session.get("https://api-capital.backend-capital.com/api/v1/session/encryptionKey",
                                     headers={"X-CAP-API-KEY": api_key})


        if response.status_code != 200:
            raise RuntimeError(response.json())

        return response.json()["encryptionKey"], response.json()["timeStamp"]

            

    def encryptPassword(self,api_key: str, password: str) -> str:

        """ Encript password with AES256 """

        encryption_key, timestamp = self.getData(api_key)
        data = base64.b64encode(f"{password}|{timestamp}".encode())
        encryption_key = RSA.import_key(base64.b64decode(encryption_key))
        cipher = PKCS1_v1_5.new(encryption_key)

        return base64.b64encode(cipher.encrypt(data)).decode()

    def getToken(self):

        """ Take CST Token and save on instance"""

        en_pass = self.encryptPassword(self.api_key, self.password)
        payload = json.dumps({
            "encryptedPassword": True,
            "identifier": self.user,
            "password": en_pass
            })

        data = self.session.post("https://api-capital.backend-capital.com/api/v1/session",
                                  headers={"X-CAP-API-KEY": self.api_key,'Content-Type': 'application/json'},
                                  data=payload )


        if data.status_code != 200:
            raise RuntimeError(data.json())

        self.CST,self.TOKEN = data.headers['CST'],data.headers['X-SECURITY-TOKEN']
        
        return self.CST,self.TOKEN

    def getSession(self):

        """ Get current session"""

        payload = ''

        data = self.session.get("https://api-capital.backend-capital.com/api/v1/session",
                                    headers={'X-SECURITY-TOKEN': self.TOKEN,
                                             'CST': self.CST,
                                             'Content-Type': 'application/json'
                                            },
                                    data=payload )


        if data.status_code != 200:
            raise RuntimeError(data.json())
        
        return data

    def closeSession(self):

        """ Close current session"""

        payload = ''

        data = self.session.delete("https://api-capital.backend-capital.com/api/v1/session",
                                    headers={'X-SECURITY-TOKEN': self.TOKEN,
                                             'CST': self.CST,
                                             'Content-Type': 'application/json'
                                            },
                                    data=payload )


        if data.status_code != 200:
            raise RuntimeError(data.json())
        
        return data



class Capital(Connection, FinancialTools):

    def __init__(self, user, password, api_key, demo=False, PriceRealTime=False) -> None:

        super().__init__()

        if demo == False:
            self.url = 'https://api-capital.backend-capital.com'
        else:
            self.url = "https://demo-api-capital.backend-capital.com"

        # LOGIN DATA
        self.user     = user
        self.api_key  = api_key
        self.password = password


        # GET CONNECTION TOKEN
        self.CST   = ''
        self.TOKEN = ''
        self.getToken()

        self.marketNode = []
        self.epic = []


    def getHistory(self, from_='2023-01-01T00:00:00', to_='2023-02-10T00:00:01'):

        payload = f'?from={from_}&to={to_}'
        data = self.httpRequest('GET',self.url,'/api/v1/history/transactions',payload)
        
        return data


    def openPositions(self,epic,side,qty,stop=None,profit=None):
        
        payload = json.dumps({
                                "epic": epic,
                                "direction": side,
                                "size": qty,
                                "stopLevel": stop,
                                "profitLevel": profit
                            })

        data = self.httpRequest('POST',self.url,'/api/v1/positions',payload)
        
        return data


    def closePosition(self,deal_ref):

        payload = ''
        data = self.httpRequest('DELETE',self.url,'/api/v1/positions/'+deal_ref,payload)
        
        return data


    def allPosition(self):

        payload = ''
        data = self.httpRequest('GET',self.url,'/api/v1/positions',payload)
        
        return data


    def queryPrice(self, symbol: str, resolution: str) -> json:

        endpoint = '/api/v1/prices/%s'%symbol
        payload = '?resolution=%s&max=400'%resolution

        data = self.httpRequest('GET',self.url+endpoint+payload,'','')
        data = json.loads(data)

        return data

    def marketInfo(self,nodo):

        payload = ''
        data = self.httpRequest('GET',self.url,'/api/v1/marketnavigation/'+nodo,payload)
        data = json.loads(data)

        return data

    def jsonToDF(self, data: json, symbol: str, tf: str):

        values = []

        for timeSerie in data['prices']:
            values.append([symbol+"-"+tf,
                           pandas.to_datetime(timeSerie['snapshotTime']),
                           timeSerie['highPrice']['bid'],
                           timeSerie['lowPrice']['bid'],
                           timeSerie['openPrice']['bid'],
                           timeSerie['closePrice']['bid'],
                           timeSerie['lastTradedVolume']])
        
        df = pandas.DataFrame(values,columns=['symbol','time','high','low','open','close','volume'])
        
        return df


    def selezioneNodi(self,nodo):

        for nodo,endpoint in nodo.items():
            selezione = input(f"vuoi usare {nodo} (y/N): ")

            if selezione.upper() == 'Y' and isinstance(endpoint,dict):
                self.selezioneNodi(endpoint)
            elif selezione.upper() == 'Y' and isinstance(endpoint,str):
                self.marketNode.append(endpoint)

    def selezioneEpic(self):

        self.selezioneNodi(nodi)

        for endpoint in self.marketNode:

            mInfo = self.marketInfo(endpoint)
            print("-"*70)
            print("{:<5} {:<15} {:<15} {:<15}".format("N°","Asset","EPIC","Price real time"))
            print("-"*70)
            try:
                markets = mInfo['markets']
            except Exception as e:
                # Ci sarebbero ulteriori nodi coi top gainers ...
                pass
            for num, market in list(enumerate(markets)):
                name = market['instrumentName']
                epic = market['epic']
                priceRealTime = market['streamingPricesAvailable']
                self.epic.append(epic)
                print("{:<5} {:<15} {:<15} {:<15}".format(num,name[:15],epic,str(priceRealTime)))
                with open("epic.txt","r+") as file:
                    elencoEpic = [line.split('#')[0] for line in file.readlines()]
                    if epic not in elencoEpic:
                        file.write(f"{epic} # {name}\n")




# if __name__ == '__main__':
#     client = Capital('username','password','api_key')
#     data = client.queryPrice('OIL_CRUDE',resolution="HOUR")
#     print(data['prices'][-1])
#     client.selezioneEpic()
#     client.session.close()


    
