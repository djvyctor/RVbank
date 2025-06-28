from database import *
from auxiliarys import *
from routes import *
from flask import Flask

data = DatabaseModules()
general_config = AuxiliaryFunctions()
web_routes = RoutesWeb()


@web_routes.app.route("/",methods=['GET','POST'])
def login():
    web_routes.login_sets(request.method)

    return render_template("login.html")

@web_routes.app.route("/register")
def register():
    return render_template("register.html")


@web_routes.app.route("/main")
def main():
    pass
web_routes.main()

