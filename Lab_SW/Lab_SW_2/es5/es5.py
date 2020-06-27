import cherrypy
import json
import threading
import time
import simpleSubscriber

threadLock=threading.Lock()
threadLock_RW=threading.Lock()

# Thread to eliminate services and devices if time exceeded
class Check_Expiration_t(threading.Thread):

	def run(self):
		while True:
			threadLock_RW.acquire()
			result=readJson()
			devices=result['devices']
			services=result['services']
			t=time.time()

			for service in services:
				if t-service['t'] > 20:
					services.remove(service)
			for device in devices:
				if t-device['t'] > 20:
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
		return str(result['broker'])

class Devices(object):
	exposed = True
	def GET(self, *uri, **params):
		result=readJson()
		return retrive_byId('devices', params, result)

	def POST(self, *uri, **params):
		input_text=json.loads(cherrypy.request.body.read())
		threadLock_RW.acquire()
		result=readJson()
		input_text['t'] = time.time()

		for device in result['devices']:
			if device['id'] == input_text['id']:
				result['devices'].remove(device)

		result['devices'].append(input_text)
		writeJson(result)
		threadLock_RW.release()

class Users(object):
	exposed = True
	def GET(self, *uri, **params):
		result=readJson()
		return retrive_byId('users', params, result)

	def POST(self, *uri, **params):
		input_text=json.loads(cherrypy.request.body.read())
		threadLock_RW.acquire()
		result=readJson()

		for user in result['users']:
			if user['id'] == input_text['id']:
				result['users'].remove(user)

		result['users'].append(input_text)
		writeJson(result)
		threadLock_RW.release()

class Services(object):
	exposed = True
	def GET(self, *uri, **params):
		result=readJson()
		return retrive_byId('services', params, result)

	def POST(self, *uri, **params):
		input_text=json.loads(cherrypy.request.body.read())
		threadLock_RW.acquire()
		result=readJson()
		input_text['t'] = time.time()

		for service in result['services']:
			if service['id'] == input_text['id']:
				result['services'].remove(service)

		result['services'].append(input_text)
		writeJson(result)
		threadLock_RW.release()

def readJson():
	threadLock.acquire()
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

# Search for things in json file
def retrive_byId(obj, params, json_text):
	if len(params) == 1:    # Search for a specific device by id
		for l in (json_text[obj]):
			if l['id'] == params['id']:
				return json.dumps(l)
	elif len(params) == 0:  # Search for all 
		return str(json_text[obj])
	else:
		raise cherrypy.HTTPError(400, "Not a valid input")
	  
if __name__=="__main__":
	conf={
		'/':
		{
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True
		}
	}
	t=Check_Expiration_t()
	t.start()
	sub=simpleSubscriber.MySubscriber('Catalog', '/tiot/13/catalog', 'test.mosquitto.org')
	
	cherrypy.tree.mount(Broker(),'/broker', conf)
	cherrypy.tree.mount(Devices(),'/devices', conf)
	cherrypy.tree.mount(Services(),'/services', conf)
	cherrypy.tree.mount(Users(),'/users', conf)
	cherrypy.engine.start()
	sub.start()
	cherrypy.engine.block()


