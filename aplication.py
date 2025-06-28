from database import *
from auxiliarys import *
from routes import *
from flask import Flask

data = DatabaseModules()
general_config = AuxiliaryFunctions()
web_routes = RoutesWeb()


@web_routes.app.route("/",methods=['GET','POST'])
def login():
    return web_routes.login_sets(request.method)




@web_routes.app.route("/register",methods=['GET','POST'])
def register():
    return web_routes.register_sets(request.method)
    
@web_routes.app.route("/main")
def main():
    return web_routes.main_sets()
    
web_routes.main()


