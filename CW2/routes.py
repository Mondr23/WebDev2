from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import app, db
from models import User, Car, Message, Category, Listing
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g
from models import Category
from flask import abort

@app.route('/')
def home():
    categories = Category.query.all()
    listings = Listing.query.limit(12).all()  # Fetch the first 12 listings
    return render_template('home.html', categories=categories, listings=listings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        # Check if username already exists (optional)
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Hash password and create new user
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    else:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_page():
    if not current_user.is_admin:
        abort(403)  # Forbid access if not an admin
    users = User.query.all()  # Example: Fetch all users
    listings = Listing.query.all()  # Example: Fetch all listings
    return render_template('admin.html', users=users, listings=listings)


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])
        image = request.files['image']
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        new_listing = Listing(
            title=title,
            description=description,
            price=price,
            category_id=category_id,
            user_id=current_user.id,
            image_file=image_filename
        )
        db.session.add(new_listing)
        db.session.commit()
        flash('Your listing has been posted!', 'success')
        return redirect(url_for('home'))

    categories = Category.query.all()
    return render_template('sell.html', categories=categories)


@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    listings = Listing.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    return render_template('home.html', categories=categories, listings=listings)

@app.route('/listing/<int:listing_id>')
def listing_details(listing_id):
    # Query the listing by its ID
    listing = Listing.query.get_or_404(listing_id)
    return render_template('details.html', listing=listing)

@app.before_request
def load_categories():
    g.categories = Category.query.all()

@app.route('/messages')
@login_required
def messages():
    received_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', received_messages=received_messages, sent_messages=sent_messages)

@app.route('/messages/send', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method == 'POST':
        recipient_username = request.form['recipient']
        content = request.form['content']
        
        recipient = User.query.filter_by(username=recipient_username).first()
        if not recipient:
            flash('User not found.', 'danger')
            return redirect(url_for('send_message'))
        
        if recipient.id == current_user.id:
            flash('You cannot send a message to yourself.', 'danger')
            return redirect(url_for('send_message'))

        message = Message(sender_id=current_user.id, recipient_id=recipient.id, content=content)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))

    return render_template('send_message.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query', '').strip()
    results = []

    if query:
        # Perform the search
        results = Listing.query.filter(
            Listing.title.ilike(f'%{query}%') | 
            Listing.description.ilike(f'%{query}%')
        ).all()

    return render_template('search.html', query=query, results=results)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))