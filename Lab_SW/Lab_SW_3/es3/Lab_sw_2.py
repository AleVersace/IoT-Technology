import cherrypy
import json
import threading
import time

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

            for service in services:
                if t-service['t'] > 60:
                    services.remove(service)
            for device in devices:
                if t-device['t'] > 60:
                    devices.remove(device)
                
            result['devices']=devices
            result['services']=services
            writeJson(result)
            threadLock_RW.release()
            time.sleep(20)


class Broker(object):
    exposed=True
    counter=5

    def GET(self, *uri, **params):
        result=readJson()
        return json.dumps(result['broker'])

class Devices(object):
    exposed = True
    def GET(self, *uri, **params):
        result=readJson()
        return json.dumps(retrive_byId('devices', params, result))

    def POST(self, *uri, **params):
        input_text=json.loads(cherrypy.request.body.read())
        threadLock_RW.acquire()
        result=readJson()
        input_text['t'] = time.time()

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
        for service in result['services']:
            if str(service['id'])==str(input_text['id']):
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

def retrive_byId(obj, params, json_text):
    if len(params) == 1:    # Search for a specific device by id
        for l in (json_text[obj]):
            if l['id'] == params['id']:
                return json.dumps(l)
    elif len(params) == 0:  # Search for all
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
    cherrypy.config.update({'server.socket_host':'localhost'})
    cherrypy.config.update({'server.socket_port':8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
    t.join()

