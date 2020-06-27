import cherrypy
import json
import threading
import time

#Doppia lock
threadLock=threading.Lock()
threadLock_RW=threading.Lock()

class Check_Expiration_t(threading.Thread):
	def run(self):
		while True:
			threadLock_RW.acquire()
			result=readJson()
			devices=result['devices']
			services=result['services']
			t=time.time()
			#Cancella servizi e device che non hanno aggiornato il timestamp
			for service in services:
				if t-service['t'] >120:
					services.remove(service)
			for device in devices:
				if t-device['t'] > 120:
					devices.remove(device)
				
			result['devices']=devices
			result['services']=services
			writeJson(result)
			threadLock_RW.release()
			time.sleep(10)


class Broker(object):
	exposed=True
	counter=5

	def GET(self, *uri, **params):
		result=readJson()
		if len(uri)==0:
			#Se non ci sono elementi nell'uri ritorna la lista intera
			return json.dumps(result['broker'])
		else:
			#se ci sono elementi nell'uri ritorna la porta o il nome (utile per i servizi)
			if uri[0]=="name":
				return result['broker']['name']
			elif uri[0]=="port":
				return result['broker']['port']
			else:
				raise cherrypy.HTTPError(400, "Not a valid uri")

class Devices(object):
	exposed = True
	def GET(self, *uri, **params):
		result=readJson()
		return json.dumps(retrive_byId('devices', params, result))

	def POST(self, *uri, **params):
		#Informazioni mandate nel body
		x=cherrypy.request.body.read()
		input_text=json.loads(x)
		threadLock_RW.acquire()
		result=readJson()
		#Aggiunta manuale di time e risorse
		input_text['resources']=list(input_text['ep'].keys())
		input_text['t'] = time.time()

		#Rimuoviamo gli elementi da aggiornare in quanto verranno riaggiunti con le info complete
		for device in result['devices']:
			if device['id']==input_text['id']:
				result['devices'].remove(device)

		
		result['devices'].append(input_text)
		writeJson(result)
		threadLock_RW.release()

class Users(object):
	exposed = True
	def GET(self, *uri, **params):
		result=readJson()
		return json.dumps(retrive_byId('users', params, result))

	def POST(self, *uri, **params):
		input_text=json.loads(cherrypy.request.body.read())
		threadLock_RW.acquire()
		result=readJson()
		#Rimuoviamo gli elementi da aggiornare in quanto verranno riaggiunti con le info complete
		for user in result['users']:
			if user['id']==input_text['id']:
				result['users'].remove(user)

		result['users'].append(input_text)
		writeJson(result)
		threadLock_RW.release()

class Services(object):
	exposed = True
	def GET(self, *uri, **params):
		result=readJson()
		return json.dumps(retrive_byId('services', params, result))

	def POST(self, *uri, **params):
		input_text=json.loads(cherrypy.request.body.read())
		threadLock_RW.acquire()
		result=readJson()
		input_text['t'] = time.time()
		#Rimuoviamo gli elementi da aggiornare in quanto verranno riaggiunti con le info complete
		for service in result['services']:
			if str(service['id'])==str(input_text['id']):
				result['services'].remove(service)
		result['services'].append(input_text)
		writeJson(result)
		threadLock_RW.release()

def readJson():
	threadLock.acquire()
	#Evita che più readers si accavallino
	text=json.load(open("information.json"))
	threadLock.release()
	return text

def writeJson(text):
	text_json=json.dumps(text)
	threadLock.acquire()
	file_output=open("information.json",'w')
	file_output.write(text_json)
	file_output.close()
	threadLock.release()


def retrive_byId(obj, params, json_text):
	if len(params) == 1:    # Cerca un id specifico
		for l in (json_text[obj]):
			if l['id'] == params['id']:
				return json.dumps(l)
	elif len(params) == 0:  # Cerca tutti
		return json_text[obj]
	else:
		raise cherrypy.HTTPError(400, "Not a valid input")

if __name__=="__main__":
	t=Check_Expiration_t()
	t.start()
	
	conf={
		'/':
		{
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True
		}
	}

	cherrypy.tree.mount(Broker(),'/broker/',conf)
	cherrypy.tree.mount(Devices(),'/devices/',conf)
	cherrypy.tree.mount(Services(),'/services/',conf)
	cherrypy.tree.mount(Users(),'/users/',conf)
	#Esponiamo le varie classi su path specifici
	cherrypy.config.update({'server.socket_host':'10.0.0.11'})
	cherrypy.config.update({'server.socket_port':8080})
	cherrypy.engine.start()
	cherrypy.engine.block()
	t.join()

