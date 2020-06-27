import random
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly
import plotly.graph_objs as go
from collections import deque
import json
from MyMQTT import *
import time
import datetime
import math
import dash_html_components as html

#Thread che rinnova ogni minuto la registrazione al Catalog del servizio
class Service(threading.Thread):
	def init(self, catalog, document):
		threading.Thread.__init__(self)
   		self.catalog = catalog
    	self.document = document
    	

    	def run(self):
      		while True:
        		requests.post(self.catalog + '/services', json.dumps(self.document))
        		time.sleep(60)


def actualTime():
	today=datetime.datetime.today()
	#Ottenere in formato adeguato l'orario attuale
	minute=int("{0:0=2d}".format(datetime.datetime.now().minute))
	hour=int("{0:0=2d}".format(datetime.datetime.now().hour))
	sec=int("{0:0=2d}".format(datetime.datetime.now().second))
	complete=str(hour)+":"+str(minute)+":"+str(sec)
	return str(complete)

#Definizione delle liste che contengono i valori dell'asse x e y
X = deque()
X.append(actualTime())
Y = deque()
Y.append(17)

#CSS esterno
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
	html.H1(children='Temperature', id='first'),
	#Aggiornamento ogni 30 secondi
	dcc.Interval(id='timer', interval=30000),
	html.Div(id='dummy'),
	dcc.Graph(
			id='graph',
			animate = False,
		)
])

#Funzione di callback chiamata dalla libreria
@app.callback(output=Output('graph', 'figure'),
			  inputs=[Input('timer', 'n_intervals')])
def update_graph(n_clicks):
	#Aggiungiamo sulle x l'orario attuale
	X.append(actualTime())
	data = plotly.graph_objs.Scatter(
			x=list(X),
			y=list(Y),
			name='Scatter',
			mode= 'lines+markers'
			)
	
	return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[X[0],max(X)]),
												yaxis=dict(range=[min(Y)-3,max(Y)+3]),)}



def retrieve_broker(catalog):
	r = {}
	r = json.loads(requests.get(catalog + '/broker').text)
	return r['name'], r['port']

def retrieve_sensors(catalog):
	r = {}
	r = json.loads(requests.get(catalog + '/devices').text)
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
			print("Selected device not found.")
	print()
	device = d
	# Get endpoints
	return device['ep'],device['id']



# Calcula temp usando sensore
def actualTemp(temp): # Temp è un dict
	B = 4275
	R0 = 100000
	Vcc = 1023.0
	T0 = 298.0
	temp = float(temp)
	R = (Vcc / temp - 1) * R0
	x=math.log(R/R0)
	T = 1/((x/B) + (1.0/T0))
	Tfin = T - 273.15
	return Tfin

#Classe che gestiste MQTT
class Client():
	def __init__(self, client, broker, port, endpoints):
		self.client = client
		self.ep = endpoints
		self.broker = broker
		self.port = port
		self.myMqttClient = MyMQTT(self.client, self.broker, self.port, self)
		self.lastTimeSensor = 0

	def start(self):
		self.myMqttClient.start()
		self.myMqttClient.mySubscribe(self.ep["tmp"])

	def stop(self):
		self.myMqttClient.stop()

	def notify(self, topic, payload):
		p={}
		p = json.loads(payload)
		#Ottiene ogni 30 secondi un nuovo valore di temperatura
		if(time.time()-self.lastTimeSensor > 30):
			if topic == self.ep['tmp']:
				self.temp = actualTemp(p['e'][0]['v'])
				self.lastTimeSensor=time.time()
				Y.append(self.temp)




if __name__ == '__main__':
	catalog = 'http://10.0.0.11:8080'
	print("\n-----------------------------------")
	print("BENVENUTO NELL'INTERFACCIA GRAFICA!")
	print("-----------------------------------\n")

	broker, port = retrieve_broker(catalog)
	endpoints, deviceName = retrieve_sensors(catalog)


	time.sleep(1)
	print("\n-----------------------------------------------------------------------------------------")
	print("Per accedere al pannello con i grafici, inserisci http://127.0.0.1:8050 in un browser web")
	print("-----------------------------------------------------------------------------------------\n")
	time.sleep(3)
	sub1 = Client('client1', broker, int(port), endpoints)
	sub1.start()
	d = {}
	d['id'] = 'Remote Smart Controller'
	d['ep'] = endpoints
	d['resources'] = list(endpoints.keys())
	
	#Avvio del thread che aggiorna le registrazioni al catalog
	s = Service(catalog, d)
	s.start()


	#Avvio del server per plotly
	app.run_server(debug=False)

