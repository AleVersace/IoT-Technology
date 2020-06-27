import json
from MyMQTT import *
import requests
import time
import threading
import datetime

class Service(threading.Thread):
	def init(self, catalog, document):
		threading.Thread.__init__(self)
   		self.catalog = catalog
    	self.document = document
    	
    	def run(self):
      		while True:
      			#Ogni minuto aggiorna la registrazione al catalog
        		requests.post(self.catalog + '/services', json.dumps(self.document))
        		time.sleep(60)


def retrieve_broker(catalog):
	#Ottiene le info dal catalog riguardo il broker
	r = {}
	r = json.loads(requests.get(catalog + '/broker').text)
	return r['name'], r['port']

def retrieve_sensors(catalog):
	r = {}
	r = json.loads(requests.get(catalog + '/devices').text)
	#Se non ci sono device viene ritornato None
	if(len(r)==0):
		return None
	#Sceglie il device corretto
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
			print("Il device inserito non esiste!")
	print()
	device = d
	# Get endpoints
	return device['ep']


class weatherThread(threading.Thread):
	def __init__(self,code,lat,lon,client,broker,port,topic):
		self.client=client
		self.topic=topic
		threading.Thread.__init__(self)
		self.myMqttClient=MyMQTT(self.client, broker, port, self)
		self.lastCheckSun=0
		self.lastCheckWeather=0
		self.code=code
		self.lat=lat
		self.lon=lon
		self.exit=0
		self.lastUpdate=0
		#The final values for the 3 config
		self.sun=[240,60,0]
		self.cloud=[60,240,180]
		self.rain=[0,60,240]
		#Starting color
		self.color=[0,0,0]
		self.map = {
			'Snow' : 2,
			'Sleet' : 2,
			'Hail' : 2,
			'Thunderstorm' : 2,
			'Heavy Rain' : 2,
			'Light Rain' : 1,
			'Showers' : 1,
			'Heavy Cloud' : 1,
			'Light Cloud' : 0,
			'Clear' : 0
		}

	def startMQTT(self):
		self.myMqttClient.start()

	def stopMQTT(self):
		self.myMqttClient.stop()


	def run(self):
		while not self.exit:
			#Every three hour check if there are new info about the sun position
			if(time.time()-self.lastCheckSun>10800):
				#Ogni 3 ore esegui una GET all'API per ottenere info sul crepuscolo
				sunInfo=requests.get("https://api.sunrise-sunset.org/json?lat="+self.lat+"&lng="+self.lon)
				sunInfoDict=json.loads(sunInfo.text)
				self.twilightEnd=sunInfoDict["results"]["civil_twilight_end"]
				#Conversione da formato AM/PM usato dell'API
				self.twH = int(datetime.datetime.strptime(self.twilightEnd, "%H:%M:%S PM").hour) + 12
				self.twM = datetime.datetime.strptime(self.twilightEnd, "%H:%M:%S PM").minute
				#Conversione AM/PM e +11 per ottenere l'ora precedente al crepuscolo
				self.startH = int(datetime.datetime.strptime(self.twilightEnd, "%H:%M:%S PM").hour) + 11
				#Valori finali degli orari in formato adeguato per datetime
				self.startFull = datetime.datetime.strptime(str(self.startH)+':'+str(self.twM)+':0', "%H:%M:%S").time()
				self.twilightFull = datetime.datetime.strptime(str(self.twH)+':'+str(self.twM)+':0', "%H:%M:%S").time()
				self.lastCheckSun=time.time()

			#Every one hour check if there are new info about the sun position
			if(time.time()-self.lastCheckWeather>7200):
				year=datetime.datetime.today().year
				month=datetime.datetime.today().month
				day=datetime.datetime.today().day
				#Richiesta GET alla API di metaweather per ottenere info sul meteo
				weatherInfo=requests.get("https://www.metaweather.com/api/location/"+str(self.code)+"/")
				weatherInfoDict=json.loads(weatherInfo.text)
				self.weather=weatherInfoDict["consolidated_weather"][0]["weather_state_name"]
				self.lastCheckWeather=time.time()

			if time.time()-self.lastUpdate > 60:
				self.updateRGB()
				self.lastUpdate=time.time()


	def updateRGB(self):
		now = datetime.datetime.now().time()
		if now >= self.startFull:
			if now <= self.twilightFull:
				#Siamo nel momento di crescita lineare
				if self.map[self.weather] == 0:
					self.color[0]+=int(self.sun[0]/60)
					self.color[1]+=int(self.sun[1]/60)
					self.color[2]+=int(self.sun[2]/60)
				elif self.map[self.weather] == 1:
					self.color[0]+=int(self.cloud[0]/60)
					self.color[1]+=int(self.cloud[1]/60)
					self.color[2]+=int(self.cloud[2]/60)
				else:
					self.color[0]+=int(self.rain[0]/60)
					self.color[1]+=int(self.rain[1]/60)
					self.color[2]+=int(self.rain[2]/60)
				self.rgbFinal = str(self.color[0])+','+str(self.color[1])+','+str(self.color[2])
				self.myMqttClient.myPublish(self.topic, self.rgbFinal)
				print(self.rgbFinal)
			else:
				#Settiamo i valori massimi quando l'orario supera quello del crepuscolo
				print(self.map[self.weather])
				if self.map[self.weather] == 0:
					self.color=self.sun
				elif self.map[self.weather] == 1:
					self.color=self.cloud
				else:
					self.color=self.rain
				self.rgbFinal = str(self.color[0])+','+str(self.color[1])+','+str(self.color[2])
				self.myMqttClient.myPublish(self.topic, self.rgbFinal)
				print(self.rgbFinal)

		#Spegni il led se sono passate le 2
		elif now >= datetime.datetime.strptime('2:0:0', "%H:%M:%S").time() and self.rgbFinal != '0,0,0':
			self.rgbFinal='0,0,0'
			self.myMqttClient.myPublish(self.topic, self.rgbFinal)
			


if __name__ == '__main__':
	#Mapping per adattare la città inserita al formato usato da metaweather
	cityMap={"torino":"torino","milano":"milan","roma":"rome","venezia":"venice","napoli":"naples"}
	catalog = 'http://10.0.0.11:8080'
	print("\n-----------------------------------")
	print("BENVENUTO NEL SERVIZIO SMART LIGHT!")
	print("-----------------------------------\n")


	broker, port = retrieve_broker(catalog)
	endpoints = retrieve_sensors(catalog)


	print("\n----------------------------------------------")
	print("Seleziona la città di riferimento per il meteo\n")
	print("Milano\nNapoli\nRoma\nTorino\nVenezia\n")
	city=str(input("Inserisci scelta: ")).lower()
	print("----------------------------------------------\n")

	if city not in cityMap:
		raise Exception('City not avaiable - please insert a correct value')


	#Get info about the city selected. Get city code, latitude and longitude
	#API used: www.metaweather.com
	result=requests.get("https://www.metaweather.com/api/location/search/?query="+cityMap[city])
	result_json=json.loads(result.text)
	cityCode=result_json[0]["woeid"]
	lat,lon=result_json[0]["latt_long"].split(",")


	d = {}
	d['id'] = 'Smart Light'
	d['ep'] = endpoints
	d['resources'] = list(endpoints.keys())
	#Registrazione del servizio al Catalog
	s = Service(catalog, d)
	s.start()

	thread=weatherThread(cityCode,lat,lon,"Client1",broker,int(port), endpoints["rgb"])
	thread.start()
	thread.startMQTT()