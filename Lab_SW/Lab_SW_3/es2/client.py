from simpleSubscriber import *
import requests
import json


def retriveDevices(catalog):
	return json.loads(requests.get(catalog + 'devices/').text)

def register_as_service(catalog, client, topic):
	d = {}
	d['id'] = client
	d['description'] = 'retrive temp'
	d['endpoints'] = topic
	requests.post(catalog + 'services/', d)


def retriveBroker(catalog):
	return json.loads(requests.get(catalog + 'broker/').text)


if __name__ == "__main__":
	catalog = 'http://10.0.0.10:8080/'
	client = 'client1'
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
	sub = MySubscriber(client, topic, broker)
	print("client="+client+" topic="+str(topic)+" broker="+str(broker))
	sub.start()
	while True:
		pass


