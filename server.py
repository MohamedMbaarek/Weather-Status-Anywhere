from flask import Flask
from datetime import timedelta
import views


def create_app():
    app = Flask(__name__)
    app.secret_key = 'dfgthyjukil'
    app.permanent_session_lifetime = timedelta(seconds=10)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.login_page,methods=["GET", "POST"])
    app.add_url_rule("/SignUp", view_func=views.register_page,methods=["GET", "POST"])
    app.add_url_rule("/Home",view_func=views.home_page,methods=["GET","POST"])
    app.add_url_rule("/logout", view_func=views.logout,methods=["POST"])
    app.add_url_rule("/forecast",view_func=views.forecast,methods=["GET","POST"])
    return app



if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT")
    debug = app.config.get("DEBUG")
    app.run(host="127.0.0.1",port=port,debug=debug)
