import requests

# Traduzione in richieste da mandare al server per recuperare informazioni
class Api():

    def __init__(self):
        self.__api = 'http://127.0.0.1:8080/'

    def broker(self):
        apiL = self.__api + 'broker/'
        req(apiL)

    def devices(self):
        apiL = self.__api + 'devices/'
        req(apiL)

    def device(self):
        id = str(input("Inserisci l'id del device"))
        apiL = self.__api + 'devices/?id={}'.format(id)
        req(apiL)

    def users(self):
        apiL = self.__api + 'users/'
        req(apiL)
    
    def user(self):
        id = str(input("Inserisci l'id dello user"))
        apiL = self.__api + 'users/?id={}'.format(id)
        req(apiL)

    def services(self):
        apiL = self.__api + 'services/'
        req(apiL)

    def service(self):
        id = str(input("Inserisci l'id del servizio"))
        apiL = self.__api + 'services/?id={}'.format(id)
        req(apiL)


def req(url):
    r = requests.get(url)
    print(r.text)