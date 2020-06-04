import cherrypy
import json

class Ex3Site(object):
	exposed=True

	def PUT(self,*uri,**params):
		d=json.loads(cherrypy.request.body.read())
		listValues=d["values"]
		originalUnit=d["originalUnit"]
		targetUnit=d["targetUnit"]
		

		listResults=convertValues(originalUnit,targetUnit,listValues)
				

		r={}

		r["values"]=listValues
		r["originalUnit"]=originalUnit
		r["convertedValues"]=listResults
		r["ConvertedUnit"]=targetUnit

		return(json.dumps(r,indent=4))


def convertValues(originalUnit,targetUnit,listValues):
	listResults=[]
	for i in range(len(listValues)):
		try:
			value=float(listValues[i])
			errorConvertion=0
		except (ValueError, TypeError):
			errorConvertion=1

		if errorConvertion==1:
			raise cherrypy.HTTPError(400,"The temperature must be an integer or a float")

		if originalUnit=='K':
			if targetUnit=='C':
				result=value-273.15
				listResults.append(result)
			elif targetUnit=='F':
				result=(value-273.15)*9/5+32
				listResults.append(result)
			else:
				raise cherrypy.HTTPError(400,"Invalid target unit [C-K-F]")
			
		elif originalUnit=='C':
			if targetUnit=='K':
				result=value+273.15
				listResults.append(result)
			elif targetUnit=='F':
				result=(value*9/5)+32
				listResults.append(result)
			else:
				raise cherrypy.HTTPError(400,"Invalid target unit [C-K-F]")
					
		elif originalUnit=='F':
			if targetUnit=='K':
				result=(value-32)*5/9+273.15
				listResults.append(result)
			elif targetUnit=='C':
				result=(value-32)*5/9
				listResults.append(result)
			else:
				raise cherrypy.HTTPError(400,"Invalid target unit [C-K-F]")
					
		else:
			raise cherrypy.HTTPError(400,"Invalid original unit [C-K-F]")

		return listResults


if __name__=="__main__":
	conf={
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True
		}
	}

	cherrypy.tree.mount(Ex3Site(),'/',conf)
	cherrypy.engine.start()
	cherrypy.engine.block()