from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
from werkzeug.utils import secure_filename
import subprocess
from flask_login import login_required, LoginManager
import zipfile
import shutil
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cairocoders-ednalan'
# SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///momo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(255), index=True)
    role = db.Column(db.String(50), index=True)

class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    minimum_qty = db.Column(db.Integer, nullable=False)
    max_qty = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)

class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)


@app.route("/")
def welcome():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']
        user_exists = Users.query.filter_by(email=email).first() is not None
        if user_exists:
            message = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  # Using 're' module here
            message = 'Invalid email address'
        elif not fullname or not password or not email:
            message = 'Please fill out the form!'
        else:
            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(password)
            # Check if the registering user is the admin
            if email == 'admin@gmail.com':
                role = 'admin'
            else:
                role = 'user'
            new_user = Users(name=fullname, email=email, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            message = 'You have successfully registered!'
            # Redirect to the appropriate page after successful registration
            if role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Authentication successful, redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            message = 'Invalid email/password combination'
    return render_template('login.html', message=message)

@app.route('/admin')
def admin():
    users = Users.query.all()  # Fetch all users from the database
    return render_template('admin.html', users=users)  # Pass users to the template

@app.route('/dashboard')
def dashboard():
    # Logic for the dashboard route
    return render_template('dashboard.html')


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the entire session data
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))  # Redirect to another page after logout

# Define a function to check if a user is logged in
def is_logged_in():
    return 'user_id' in session and 'user_role' in session

# Define a decorator to restrict access to authenticated users
def login_required(f):
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/crud')
def crud():
    return render_template('crud.html')

@app.route('/insert', methods=['POST'])
def insert_data():
    name = request.form['name']
    price = request.form['price']
    qty = request.form['qty']
    minimum_qty = request.form['minimum_qty']
    max_qty = request.form['max_qty']
    print(f"Received form data: Name: {name}, Price: {price}, Quantity: {qty}, Min Qty: {minimum_qty}, Max Qty: {max_qty}")

    image = request.files['image']
    # Save the image to the appropriate directory
    image_path = 'uploads/images/' + secure_filename(image.filename)
    image.save(image_path)

    # Create a new item object with the provided data
    new_item = Item(name=name, price=price, qty=qty, minimum_qty=minimum_qty, max_qty=max_qty, image=image_path)

    # Add the new item to the database session and commit changes
    db.session.add(new_item)
    db.session.commit()

    return 'Data inserted successfully!'

@app.route('/user')
def user():
    users = Users.query.all()  # Fetch all users from the database
    return render_template('user.html', users=users)  # Pass users to the template


@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')  # Retrieve the user ID from the form data
    user = Users.query.get(user_id)  # Retrieve the user by ID
    if user:
        db.session.delete(user)  # Delete the user from the database
        db.session.commit()  # Commit the changes

    # Redirect back to the admin page after deleting the user
    return redirect(url_for('user'))



# Route to generate the page displaying data from the item table
@app.route('/items')
def display_items():
    items = Item.query.all()
    return render_template('items.html', items=items)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
def update_item_form(item_id):
    item = Item.query.get(item_id)
    if request.method == 'POST':
        # Logic to update item based on form submission
        item.name = request.form['name']
        item.price = request.form['price']
        item.qty = request.form['qty']
        item.minimum_qty = request.form['minimum_qty']
        item.max_qty = request.form['max_qty']
        db.session.commit()
        return redirect(url_for('admin'))  # Redirect to admin page after updating item
    return render_template('update_item_form.html', item=item)

@app.route('/delete-item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        return jsonify({'message': 'Item not found'}), 404


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    new_contact = Contact(name=name, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully!'})

@app.route('/order')
def order():
    items = Item.query.all()
    return render_template('order.html', items=items)

@app.route('/payment/<int:item_id>', methods=['GET', 'POST'])
def payment(item_id):
    if request.method == 'GET':
        item = Item.query.get(item_id)
        if item:
            return render_template('payment.html', product_name=item.name, quantity=item.qty, max_quantity=item.max_qty, min_quantity=item.minimum_qty)
        else:
            return 'Item not found', 404
    elif request.method == 'POST':
        # Get the quantity ordered from the form
        ordered_quantity = int(request.form['ordered_quantity'])
        
        # Get the item from the database
        item = Item.query.get(item_id)
        if item:
            # Check if there is enough stock for the order
            if item.qty >= ordered_quantity:
                # Subtract the ordered quantity from the stock quantity in the database
                item.qty -= ordered_quantity
                db.session.commit()
                return redirect(url_for('dashboard'))  # Redirect to dashboard or a confirmation page
            else:
                return 'Insufficient stock', 400  # Return an error if there is not enough stock
        else:
            return 'Item not found', 404

@app.route('/contact-messages')
def display_contact_messages():
    messages = Contact.query.all()  # Fetch all contact messages from the database
    return render_template('contact_messages.html', messages=messages)

@app.route('/backup2')
def backup2():
    # Logic for the backup route
    return render_template('backup2.html')

# Backup route
@app.route('/backup', methods=['POST'])
def backup():
    # Create a backup of the SQLite database
    backup_path = 'backup.db'
    shutil.copy('momo.db', backup_path)
    
    # Zip the backup file
    with zipfile.ZipFile('backup.zip', 'w') as zipf:
        zipf.write(backup_path)
    
    # Remove the backup file
    os.remove(backup_path)
    
    # Create a response object with the backup file
    response = make_response(send_file('backup.zip', as_attachment=True, mimetype='application/zip'))
    
    # Set the Content-Disposition header to attachment and provide a filename for the download
    response.headers['Content-Disposition'] = f'attachment; filename="backup.zip"'

    # Return the response object
    return response

# Restore route
@app.route('/restore', methods=['POST'])
def restore():
    # Get the uploaded restore file
    restore_file = request.files['restore_file']
    
    # Save the uploaded restore file
    restore_file.save('restore.zip')
    
    # Extract the restore file
    with zipfile.ZipFile('restore.zip', 'r') as zipf:
        zipf.extractall()
    
    # Remove the restore zip file
    os.remove('restore.zip')
    
    # Replace the current database with the restored database
    os.remove('momo.db')
    shutil.copy('restore.db', 'momo.db')
    
    # Remove the restored database file
    os.remove('restore.db')
    
    # Return a success message
    return 'Database restored successfully!'





if __name__ == '__main__':
    app.run(debug=True)
