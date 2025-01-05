from flask import Flask
import views


def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/",view_func=views.home_page,methods=["GET","POST"])
    return app



if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT",3000)
    app.run(host="127.0.0.1",port=port)
