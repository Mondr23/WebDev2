from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import app, db
from models import User, Message, Category, Listing, user_favorites,  ListingImage
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g
from models import Category
from flask import abort
from flask import request, jsonify
from flask_login import logout_user, current_user, login_required
from sqlalchemy import func

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
        user.is_active = True
        db.session.commit()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:  # Redirect admins to admin dashboard
                return redirect(url_for('admin_page'))
            return redirect(url_for('home'))  # Redirect non-admins to home
        flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='scrypt')  # Use scrypt
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


@app.route('/admin_page')
@login_required
def admin_page():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    # Total statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    total_listings = Listing.query.count()
    active_users = User.query.filter_by(is_active=True).count()

    # Listings by category
    category_data = db.session.query(
        Category.name, func.count(Listing.id)
    ).join(Listing).group_by(Category.name).all()
    category_labels = [category[0] for category in category_data]
    category_counts = [category[1] for category in category_data]

    # Listings by location
    location_data = db.session.query(
        Listing.location, func.count(Listing.id)
    ).group_by(Listing.location).all()
    location_labels = [location[0] for location in location_data]
    location_counts = [location[1] for location in location_data]

    return render_template(
        'admin.html',
        total_users=total_users,
        admin_users=admin_users,
        total_listings=total_listings,
        active_users=active_users,
        category_labels=category_labels,
        category_counts=category_counts,
        location_labels=location_labels,
        location_counts=location_counts
    )


@app.route('/manage_data')
@login_required
def manage_data():
    if not current_user.is_admin:
        abort(403)  # Restrict access to admins only

    # Fetch data for users and listings
    users = User.query.all()
    listings = Listing.query.all()

    return render_template('manage_data.html', users=users, listings=listings)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_data'))

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_data'))

@app.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(listing_id)
    if request.method == 'POST':
        listing.title = request.form.get('title')
        listing.price = request.form.get('price')
        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('manage_data'))

    return render_template('edit_listing.html', listing=listing)


@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    if not current_user.is_admin:
        abort(403)

    listing = Listing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted successfully!', 'success')
    return redirect(url_for('manage_data'))


from werkzeug.utils import secure_filename
import os

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])

        # Additional fields
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        mileage = int(request.form['mileage'])
        fuel_type = request.form['fuel_type']
        transmission = request.form['transmission']
        location = request.form['location']
        contact_number = request.form['contact_number']

        # Process main image (optional)
        image = request.files['image']
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

        # Create new listing
        new_listing = Listing(
            title=title,
            description=description,
            price=price,
            category_id=category_id,
            user_id=current_user.id,
            image_file=image_filename,
            make=make,
            model=model,
            year=year,
            mileage=mileage,
            fuel_type=fuel_type,
            transmission=transmission,
            location=location,
            contact_number=contact_number
        )
        db.session.add(new_listing)
        db.session.commit()

        # Handle multiple images
        images = request.files.getlist('images')
        for image in images:
            if image.filename:
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)

                # Save each image to the database
                listing_image = ListingImage(listing_id=new_listing.id, image_file=image_filename)
                db.session.add(listing_image)

        db.session.commit()
        flash('Your listing has been posted with images!', 'success')
        return redirect(url_for('home'))

    # Pass categories to the template
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

@app.route('/favorites/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    item_id = request.json.get('item_id')
    item = Listing.query.get(item_id)  # Assuming Listing is your item model
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    # Add or remove the favorite
    if item in current_user.favorites:
        current_user.favorites.remove(item)
        db.session.commit()
        return jsonify({'message': 'Item removed from favorites', 'favorited': False}), 200
    else:
        current_user.favorites.append(item)
        db.session.commit()
        return jsonify({'message': 'Item added to favorites', 'favorited': True}), 200

@app.route('/favorites', methods=['GET'])
@login_required
def favorites_page():
    # Fetch all favorite items for the current user
    favorites = current_user.favorites.all()  # Using lazy='dynamic' allows this query
    return render_template('favorites.html', favorites=favorites)

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:  # Ensure a user is logged in
        current_user.is_active = False  # Mark user as inactive
        db.session.commit()
    logout_user()  # Log out the user
    return redirect(url_for('home'))
