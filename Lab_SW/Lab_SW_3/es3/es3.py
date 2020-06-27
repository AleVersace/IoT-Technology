from simplePublisher import *
import requests
import json


def retriveDevices(catalog):
    return json.loads(requests.get(catalog + 'devices/').text)

def register_as_service(catalog, client, topic):
    d = {}
    d['id'] = client
    d['description'] = 'retrive temp'
    d['end-points'] = topic
    requests.post(catalog + 'services/', d)


def retriveBroker(catalog):
    return json.loads(requests.get(catalog + 'broker/').text)


if __name__ == "__main__":
    catalog = 'http://127.0.0.1:8080/'
    client = 'Publisher1'
    broker = retriveBroker(catalog)
    devices= retriveDevices(catalog)
    for device in devices:
        print("id: {}".format(json.dumps(device["id"])))

    # Trova device dato l'id altrimenti richiedi di nuovo l'id
    trovato = 0
    while not trovato:
        idD = str(input('Seleziona id device: '))
        for device in devices:
            if str(device['id']) == idD:
                trovato = 1
                break
        if trovato == 1:
            deviceFound = device
        else:
            print('Id fornito non trovato')

    print(deviceFound['resources'])
    res = str(input('Inserisci risorsa: '))
    topic = device['endpoints'][res]
    broker = broker['name']

    # Sub and registration as service
    register_as_service(catalog, client, topic)
    pub = MyPublisher(client, broker)
    pub.start()

    while True:
        message = ('{"command":"on"}')
        pub.myPublish(topic, message)     
        time.sleep(5)




