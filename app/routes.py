from flask import Flask, Blueprint, render_template, request, redirect, url_for, jsonify, session, send_file, send_from_directory, make_response
from pydantic import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import Users, Item
from .database import SessionLocal, engine, Base
from .schemas import *
import os

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__), 
    'uploads'
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MainView:
    def __init__(self) -> None:
        self.bp = Blueprint('main', __name__, url_prefix='')
    
        self.bp.add_url_rule('/dashboard', 'dashboard', self.dashboard)
        self.bp.add_url_rule('/admin', 'admin', self.admin)
        self.bp.add_url_rule('/crud', 'crud', self.crud)
        self.bp.add_url_rule('/uploads/<name>', 'download_file', self.download_file)

        item = self.Items()

        self.bp.register_blueprint(item.bp)

    def download_file(self, name):
        return send_from_directory(UPLOAD_FOLDER, name)

    def dashboard(self):
        return render_template("dashboard.html")

    def admin(self):
        return render_template("admin.html")
    
    def crud(self):
        return render_template('crud.html')

    class Items:
        def __init__(self) -> None:
            self.db = next(get_db())

            self.bp = Blueprint('items', __name__, url_prefix='/items')

            self.bp.add_url_rule('/', 'list_or_create', self.list_or_create, methods=["GET", "POST"])


        def list_or_create(self):
            if request.method == "POST":
                item_data = request.form
                
                try:
                    item = AddItemSchema(**item_data)
                except ValueError as e:
                    return jsonify({"error": e.errors()}), 400

                image = request.files['image']
                image_path = os.path.join('UPLOAD_FOLDER', 'images', secure_filename(image.filename))
                image.save(image_path)

                item.image = os.path.basename(image_path)

                new_item = Item(**item.model_dump())
                self.db.add(new_item)
                self.db.commit()

            items = self.db.query(Item).all()
            return render_template('items.html', items=items)

class UsersView:
    def __init__(self) -> None:
        self.bp = Blueprint('users', __name__, url_prefix='/users')

        self.bp.add_url_rule('/register', 'register', self.register, methods=["GET", "POST"])
        self.bp.add_url_rule('/login', 'login', self.login, methods=["GET", "POST"])
        self.bp.add_url_rule('/logout', 'logout', self.logout, methods=["GET", "POST"])

        self.db = next(get_db())
    
    def register(self):
        message = ''
        if request.method == 'POST':
            user_data = request.form

            try:
                user = UserRegisterSchema(**user_data)
            except Exception as e:
                return jsonify({"error": e.errors()}), 400
            
            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(user.password)

            # Check if the registering user is the admin
            if user.email == 'admin@gmail.com':
                role = 'admin'
            else:
                role = 'user'

            new_user = Users(name=user.name, email=user.email, password=hashed_password, role=role)
            self.db.add(new_user)
            self.db.commit()
            message = 'You have successfully registered!'
            # Redirect to the appropriate page after successful registration
            if role == 'admin':
                return redirect(url_for('main.admin'))
            else:
                return redirect(url_for('main.dashboard'))
                
        return render_template('register.html', message=message)

    def login(self):
        message = ''
        if request.method == 'POST':
            try:
                user_schema = UserLoginSchema(**request.form)
            except Exception as e:
                return jsonify(e)
            
            user = self.db.query(Users).filter(Users.email == user_schema.email).first()

            if user and check_password_hash(user.password, user_schema.password):
                # Authentication successful, redirect based on user role
                if user.role == 'admin':
                    return redirect(url_for('main.admin'))
                else:
                    return redirect(url_for('main.dashboard'))
            else:
                message = 'Invalid email/password combination'
        return render_template('login.html', message=message)

    def logout(self):
        return "Working on it..."
    