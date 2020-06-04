import cherrypy
import os

class Freeboard():

    exposed = True
    def GET(self, *uri):
        return open('freeboard/index.html')

    def POST(self, *uri, **params):
        file = 'freeboard/dashboard/dashboard.json'
        f = open(file, "w")
        f.write(params['json_string'])
        f.close()
        return



if __name__=='__main__':
    
    conf = {
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on' : True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/css':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './freeboard/css'
        },
        '/js':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './freeboard/js'
        },
        '/img':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './freeboard/img'
        },
        '/plugins':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './freeboard/plugins'
        }
    }

    cherrypy.tree.mount(Freeboard(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
