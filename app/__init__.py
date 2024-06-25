from flask import Flask

def create_app():
    app = Flask(__name__)
    with app.app_context():
        from .routes import UsersView, MainView

        main = MainView()
        view = UsersView()

        app.register_blueprint(view.bp)
        app.register_blueprint(main.bp)
        
    return app
