import requests
import json
import time
from MyMQTT import *
import math
import threading


checkPresenceDevice=1

#Simula il loop() di arduino e controlla che il device sia ancora connesso
class Routine(threading.Thread):
	def __init__(self,client):
		threading.Thread.__init__(self)
		self.client=client
		
		
	def run(self):
		global checkPresenceDevice
		lastCheckDevice=0
		timeDevice=0
		while checkPresenceDevice==1:
			if (time.time() - self.client.timeStartMovement) > self.client.PIR_timeout:
				self.client.PIR_presence = 0
			
			if (self.client.SOUND_presence == 1 or self.client.PIR_presence == 1):
				self.client.presence = 1

			else:
				self.client.presence = 0


			if(time.time() - lastCheckDevice >5):
				#Ogni 5 secondi controlla se il nostro device è ancora registrato al catalog
				r = {}
				r = json.loads(requests.get(catalog + '/devices').text)
				lastCheckDevice=time.time()
				for d in r:
					if deviceName == str(d['id']):
						checkPresenceDevice=1
						timeDevice=time.time()
						break

				if time.time()-timeDevice > 10:
					#Se dopo 10 secondi non c'è il device setta a zero la variabile
					checkPresenceDevice=0
				
				
			

class Client():
	def __init__(self, client, broker, port, endpoints):
		self.client = client
		self.ep = endpoints
		self.broker = broker
		self.port = port
		self.myMqttClient = MyMQTT(self.client, self.broker, self.port, self)
		self.temp = 0
		#Valori di base dei set points
		self.FTEMP_MIN = [15.0, 20.0]
		self.FTEMP_MAX = [30.0, 25.0]
		self.LTEMP_MIN = [10.0, 15.0]
		self.LTEMP_MAX = [15.0, 20.0]
		self.presence = 0
		self.timeStartMovement = 0
		self.PIR_timeout = 1800  # 30 minutes in seconds
		self.PIR_presence = 0

		self.SOUND_presence = 0
		self.min_n_events = 5
		self.vetSounds = [0 for l in range(self.min_n_events-1)]
		self.startFlag = 0
		self.SOUND_interval = 600    # 10 minutes in seconds
		self.SOUND_timeout = 3600    # 1h in seconds
		self.lastTime=0
		self.lastTimeSensor=0
		self.sel=0
		self.thread=""

	def start(self):
		print("Gli attuali i range di temperatura sono settati ai seguenti valori:")
		print("Presenza -> Ventola: ["+str(self.FTEMP_MIN[1])+" - "+str(self.FTEMP_MAX[1])+"]    Led: ["+str(self.LTEMP_MIN[1])+" - "+str(self.LTEMP_MAX[1])+"]")
		print("Assenza  -> Ventola: ["+str(self.FTEMP_MIN[0])+" - "+str(self.FTEMP_MAX[0])+"]    Led: ["+str(self.LTEMP_MIN[0])+" - "+str(self.LTEMP_MAX[0])+"]")
		#Inizializzazione MQTT
		self.myMqttClient.start()
		self.myMqttClient.mySubscribe(str(endpoints['tmp']))
		self.myMqttClient.mySubscribe(str(endpoints['mov']))
		self.myMqttClient.mySubscribe(str(endpoints['nos']))
		self.thread=Routine(self)
		self.thread.start()

	def stop(self):
		self.myMqttClient.stop()
		self.thread.join()

	def notify(self, topic, payload):
		p={}
		p = json.loads(payload)

		if topic == self.ep['mov']:   #Message PIR every time a movement is detected
			if p['e'][0]['v'] == 1:
				self.PIR_presence = 1
				self.timeStartMovement = time.time()


		elif topic == self.ep['nos']:
			if p['e'][0]['v'] == 1:
				checkPresenceSOUND(int(p['e'][0]['v']), self)

		if(time.time()-self.lastTimeSensor>5):
			#Ogni 5 secondi leggi i valori di temperatura e esegui i calcoli
			if topic == self.ep['tmp']:
				self.temp = actualTemp(p['e'][0]['v'])
				self.perc_AC, m1 = regulate_fan_or_led(self.ep['fan'], self.FTEMP_MIN[self.presence], self.FTEMP_MAX[self.presence], self.temp, self.ep)
				self.perc_HT, m2 = regulate_fan_or_led(self.ep['led'], self.LTEMP_MAX[self.presence], self.LTEMP_MIN[self.presence], self.temp, self.ep)
				#Pubblicazione valori di attuazione agli endpoints ottenuti
				self.myMqttClient.myPublish(str(self.ep['fan']), m1)
				self.myMqttClient.myPublish(str(self.ep['led']), m2)
				self.lastTimeSensor=time.time()
		
		if(time.time()-self.lastTime>7):
			#Ogni 7 secondi aggiorna valori del display
			#2 possibili schermate si alternano
			if(self.sel==0):
				mp = 'T:{} Pres:{}  AC:{}% HT:{}%'.format(round(self.temp, 2), self.presence, int(self.perc_AC), int(self.perc_HT))
				self.myMqttClient.myPublish(str(self.ep['lcd']), mp)
				self.sel=1;
				self.lastTime=time.time()
			else:
				ms = 'AC m:{} M:{}HT m:{} M:{}'.format(self.FTEMP_MIN[self.presence],self.FTEMP_MAX[self.presence], self.LTEMP_MIN[self.presence],self.LTEMP_MAX[self.presence])
				self.myMqttClient.myPublish(str(self.ep['lcd']), ms)
				self.sel=0;
				self.lastTime=time.time()
				
			
			
	#Cambi i valori dei set points a seconda di presenza/assenza
	def setPoints(self, obj,status, MIN, MAX):
		if (obj.lower() == 'fan'):
			if status.lower() == 'presence':
				self.FTEMP_MIN[1] = MIN
				self.FTEMP_MAX[1] = MAX
			elif status.lower() == 'absence':
				self.FTEMP_MIN[0] = MIN
				self.FTEMP_MAX[0] = MAX
			else:
				print("Invalid Input pres/abs.\n")
		elif obj.lower() == 'led':
			if status.lower() == 'presence':
				self.LTEMP_MIN[1] = MIN
				self.LTEMP_MAX[1] = MAX
			elif status.lower() == 'absence':
				self.LTEMP_MIN[0] = MIN
				self.LTEMP_MAX[0] = MAX
			else:
				print("Invalid Input pres/abs.\n")
		else:
			print("Invalid Input.\n")
			

#Ottieni info sul broker	
def retrieve_broker(catalog):
	r = {}
	r = json.loads(requests.get(catalog + '/broker').text)
	return r['name'], r['port']

def retrieve_sensors(catalog):
	r = {}
	r = json.loads(requests.get(catalog + '/devices').text)
	#Nessun device nel catalog
	if(len(r)==0):
		return None, None
	# Choose correct device
	found_device = 0
	print("-----LISTA DEI DEVICES-----")
	while not found_device and len(r)>0:
		for device in r:
			print(str(device['id']))
		device = str(input("\nScegli il device: "))

		for d in r:
			if device == str(d['id']):
				found_device = 1
				break
		
		if found_device == 0:
			#Se nome inserito non è presente
			print("Selected device not found.")
	print()
	device = d
	# Get endpoints
	return device['ep'],device['id']


# Calculate temp using sensor
def actualTemp(temp): # Temp is a dict
	B = 4275
	R0 = 100000
	Vcc = 1023.0
	T0 = 298.0
	temp = float(temp) # Voltage Value
	R = (Vcc / temp - 1) * R0
	x=math.log(R/R0)
	T = 1/((x/B) + (1.0/T0))
	Tfin = T - 273.15
	return Tfin


# Regula velocità fan o colore led a seconda della temp
def regulate_fan_or_led(topic, MIN, MAX, temp, ep):
	MAX_SPEED = 255
	d = 0
	# Calculate values
	if ((temp >= MIN and temp <= MAX and topic == ep['fan']) or (temp <= MIN and temp >= MAX and topic == ep['led'])):
		value = int(MAX_SPEED / (MAX - MIN) * (temp - MIN))
		d = value
		return int(100 * value / 255), str(d)
	#Valori di saturazione
	elif ((topic == ep['fan'] and temp < MIN) or (topic == ep['led'] and temp > MIN)):
		d = 0
		return 0, str(d)
	else:
		d = MAX_SPEED
		return 100, str(d)

# shift list l by n left side 
def rotate(l, n):
	return l[n:] + l[:n]

# Controlla se ci sono abbastanza rumori per segnalare la presenza
#Algoritmo uguale a quello scritto in Arduino. Basato su un vettore che shifta
def checkPresenceSOUND(status_sound, client):
		now = time.time()
		if status_sound == 1:
			first = client.vetSounds[0]
			client.vetSounds = rotate(client.vetSounds, 1)
			client.vetSounds[client.min_n_events - 2] = now
			if (now - first < client.SOUND_interval and client.SOUND_counter > client.min_n_events - 2):
				client.SOUND_presence = 1
				startFlag = time.time()
			else:
				client.SOUND_counter += 1
			
		if (time.time() - startFlag > client.SOUND_timeout and client.SOUND_presence == 1):
			client.SOUND_presence = 0



if __name__ == "__main__":
	catalog = 'http://10.0.0.10:8080'
	print("\n--------------------------------------")
	print("Benvenuto nel Remote Smart Controller!")
	print("--------------------------------------\n")

	while True:
		#Ottiene le info sul broker al quale chiede successivamente la lista dei device
		broker, port = retrieve_broker(catalog)
		endpoints,deviceName = retrieve_sensors(catalog)

		#Se non ci sono device il programma viene chiuso
		if(endpoints==None and deviceName==None):
			print("\n---------------------------------------------------")
			print("Errore - attualemente non ci sono devices connessi!")
			print("Il programma verrà chiuso")
			print("---------------------------------------------------\n")
			break

		#Avvio del client che gestisce MQTT
		sub1 = Client('client1', broker, int(port), endpoints)
		sub1.start()
		d = {}
		d['id'] = 'Remote Smart Controller'
		d['ep'] = endpoints
		d['resources'] = list(endpoints.keys())
		
		#CheckPresenceDevice diventa 0 se l'attuale device si disconnette
		#Una nuova procedura di scelta del device verrebbe avviata
		while checkPresenceDevice == 1:
			requests.post(catalog + '/services', json.dumps(d))
			time.sleep(5)
			#Permette cambio dei set point manualmente
			obj = str(input("\n\nModifica i setpoints:\nLed/Fan: \n"))
			status = str(input("absence/presence: \n"))
			MIN = int(input("Imposta temp minima: "))
			MAX = int(input("Imposta temp massima: "))
			sub1.setPoints(obj, status, MIN, MAX)

		sub1.stop()

