import cherrypy
import json

class Ex2Site(object):
	exposed=True
	def GET(self,*uri,**params):
		if len(uri)!=3:
			raise cherrypy.HTTPError(400,"The uri is not satisfied [/value/originalUnit/targetUnit]")

		try:
			value=float(uri[0])
			errorConvertion=0
		except (ValueError, TypeError):
			errorConvertion=1

		if errorConvertion==1:
			raise cherrypy.HTTPError(400,"The temperature must be an integer or a float")

		originalUnit=uri[1]
		targetUnit=uri[2]

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


if __name__=="__main__":
	conf={
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True
		}
	}
	cherrypy.tree.mount(Ex2Site(),'/converter',conf)
	cherrypy.engine.start()
	cherrypy.engine.block()