import cherrypy
import json

class Ex1Site(object):
	exposed=True

	def GET(self,*uri,**params):
		if len(params)!=3:
			raise cherrypy.HTTPError(400,"The uri is not satisfied [/value/originalUnit/targetUnit]")

		
		originalUnit=params["originalUnit"]
		targetUnit=params["targetUnit"]

		try:
			value=float(params["value"])
			errorConversion=0
		except (ValueError, TypeError):
			errorConversion=1

		if errorConversion==1:
			raise cherrypy.HTTPError(400,"The temperature must be an integer or a float")

		result=convertValue(originalUnit,targetUnit,value)


		d={}

		d["Original value"]=value
		d["Original unit"]=originalUnit
		d["Converted value"]=round(result,2)
		d["Converted unit"]=targetUnit

		return(json.dumps(d,indent=4))



def convertValue(originalUnit,targetUnit,value):
	if originalUnit=='K':
		if targetUnit=='C':
			result=value-273.15
		elif targetUnit=='F':
			result=(value-273.15)*9/5+32
		else:
			raise cherrypy.HTTPError(404,"Target unit not found [C-K-F]")
	elif originalUnit=='C':
		if targetUnit=='K':
			result=value+273.15
		elif targetUnit=='F':
			result=(value*9/5)+32
		else:
			raise cherrypy.HTTPError(404,"Target unit not found [C-K-F]")
	elif originalUnit=='F':
		if targetUnit=='K':
			result=(value-32)*5/9+273.15
		elif targetUnit=='C':
			result=(value-32)*5/9
		else:
			raise cherrypy.HTTPError(404,"Target unit not found [C-K-F]")
	else:
		raise cherrypy.HTTPError(404,"Original unit not found [C-K-F]")

	return result

class Log():
	logs = []
	exposed = True
	def GET(self, *uri, **params):
		r=json.dumps(self.logs)
		return r

	def POST(self, **params):
		d = cherrypy.request.body.read()
		j=json.loads(d)
		self.logs.append(j)

if __name__=="__main__":
	conf = {
	'/':{
		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
		'tools.sessions.on':True
		}
	}
	cherrypy.tree.mount(Ex1Site(),'/converter',conf)
	cherrypy.tree.mount(Log(), '/log', conf)
	cherrypy.config.update({'server.socket_host':'0.0.0.0'})
	cherrypy.config.update({'server.socket_port':8080})
	cherrypy.engine.start()
	cherrypy.engine.block()