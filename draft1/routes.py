from flask import render_template, redirect, url_for, flash, request, jsonify, abort, session, has_request_context
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Message, Category, Listing, ListingImage, Brand
from app import app, db
from sqlalchemy import func
from datetime import datetime, timezone
import os, re


# View: Home Page
@app.route('/')
def home():
    """Render the home page with categories and listings."""
    categories = Category.query.all()
    listings = Listing.query.limit(20).all()
    return render_template('home.html', categories=categories, listings=listings)


# View: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        # Verify user info
        if user and check_password_hash(user.password, password):
            user.is_active = True
            db.session.commit()
            login_user(user)
            return redirect(url_for('admin_page' if user.is_admin else 'home'))

        flash('Login unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html')


# View: Logout
@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    current_user.is_active = False
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if not re.match("^[a-zA-Z0-9_]{3,20}$", username):
            flash('Username must be 3-20 characters and contain only letters, numbers, or underscores.', 'danger')
            return render_template('register.html')
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html')
        
        # Check for existing email
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please log in.', 'danger')
            return render_template('register.html')
        
          # Check for existing username
        existing_name = User.query.filter_by(username=username).first()
        if existing_name:
            flash('Username already existed. Please try again.', 'danger')
            return render_template('register.html', error_message="Username already in use.")

        # Create and store the user
        new_user = User(username=username, email=email)
        new_user.set_password(password) 
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# View: Profile
@app.route('/profile')
def profile():
    """Render user profile with listings."""
    if current_user.is_authenticated:
        user_listings = Listing.query.filter_by(user_id=current_user.id).all()
        return render_template('profile.html', user=current_user, user_listings=user_listings)

    return redirect(url_for('login'))


# View: Admin Page
@app.route('/admin_page')
@login_required
def admin_page():
    """Render admin dashboard."""
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


# View: Manage Data
@app.route('/manage_data')
@login_required
def manage_data():
    """Render data management view for admins."""
    if not current_user.is_admin:
        abort(403)

    users = User.query.all()
    listings = Listing.query.all()
    return render_template('manage_data.html', users=users, listings=listings)


# View: Delete User
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user."""
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_data'))


# View: Edit Listing
@app.route('/edit/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    """Edit a listing."""
    listing = Listing.query.get_or_404(listing_id)

    # Ensure only the owner 
    if listing.user_id != current_user.id:abort(403)

    if request.method == 'POST':
        # Update listing details
        listing.title = request.form['title']
        listing.description = request.form['description']
        listing.price = request.form['price']
        listing.category_id = request.form['category_id']
        listing.brand_id = int(request.form['brand_id'])
        listing.model = request.form['model']
        listing.year = request.form['year']
        listing.mileage = request.form['mileage']
        listing.fuel_type = request.form['fuel_type']
        listing.transmission = request.form['transmission']
        listing.location = request.form['location']
        listing.contact_number = request.form['contact_number']

        # Handle file uploads
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))
            listing.image_file = image_file

        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_listing.html', listing=listing, categories=Category.query.all())


# View: Delete Listing
@app.route('/delete/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    """Delete a listing."""
    listing = Listing.query.get_or_404(listing_id)

    # Ensure the current user owns the listing or is an admin
    if listing.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted successfully!', 'success')
    return redirect(url_for('profile'))


# View: Update User Admin Status
@app.route('/update_user_admin_status/<int:user_id>', methods=['POST'])
@login_required
def update_user_admin_status(user_id):
    """Update user admin status."""
    if not current_user.is_admin:
        abort(403)  # Only admins can update admin status

    user = User.query.get_or_404(user_id)
    user.is_admin = 'is_admin' in request.form
    db.session.commit()
    flash(f'Admin status for {user.username} updated successfully!', 'success')
    return redirect(url_for('manage_data'))


# View: Update Password
@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    """Update the current user's password."""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    
    #Validate teh new password 
    if len(new_password) < 8:
        flash('New password must be at least 8 characters long.', 'danger')
        return redirect(url_for('profile'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Password updated successfully.', 'success')
    return redirect(url_for('profile'))


@app.route('/update_email', methods=['POST'])
@login_required
def update_email():
    """Update the current user's email."""
    new_email = request.form.get('email')
    
    if not new_email:
        flash('Email cannot be empty.', 'danger')
        return redirect(url_for('profile'))

    # Validate the email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('profile'))

    # Check if the email is already taken
    existing_email = User.query.filter_by(email=new_email).first()
    if existing_email:
        flash('Email already registered. Please try a different email.', 'danger')
        return redirect(url_for('profile'))

    # Update the user's email
    current_user.email = new_email
    db.session.commit()
    flash('Email updated successfully.', 'success')
    return redirect(url_for('profile'))


# View: Update Username
@app.route('/update_username', methods=['POST'])
@login_required
def update_username():
    """Update the current user's username."""
    new_name = request.form.get('username')

    if not new_name:
        flash('Username cannot be empty.', 'danger')
        return redirect(url_for('profile'))

    # Validate username format
    if not re.match("^[a-zA-Z0-9_]{3,20}$", new_name):
        flash('Username must be 3-20 characters long and contain only letters, numbers, or underscores.', 'danger')
        return redirect(url_for('profile'))

    # Check for existing username
    existing_name = User.query.filter_by(username=new_name).first()
    if existing_name:
        flash('Username already exists. Please try again.', 'danger')
        return redirect(url_for('profile'))

    # Update the user's username
    current_user.username = new_name
    try:
        db.session.commit()
        flash('Username updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()  # Roll back in case of error
        flash('An error occurred while updating your username. Please try again.', 'danger')

    return redirect(url_for('profile'))


# View: Sell Listing
@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    """Create a new listing."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category_id'])

        # Additional fields
        brand_id = int(request.form['brand_id'])
        model = request.form['model']
        year = int(request.form['year'])
        mileage = int(request.form['mileage'])
        fuel_type = request.form['fuel_type']
        transmission = request.form['transmission']
        location = request.form['location']
        contact_number = request.form['contact_number']

        # Process main image
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
            model=model,
            brand_id=brand_id,
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

                listing_image = ListingImage(listing_id=new_listing.id, image_file=image_filename)
                db.session.add(listing_image)

        db.session.commit()
        flash('Your listing has been posted!', 'success')
        return redirect(url_for('home'))

    categories = Category.query.all()
    brands = Brand.query.all()
    return render_template('sell.html', categories=categories, brands=brands)


# View: Category Listings
@app.route('/category/<int:category_id>')
def category(category_id):
    """View listings by category."""
    category = Category.query.get_or_404(category_id)
    listings = Listing.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    return render_template('home.html', categories=categories, listings=listings)


# View: Brand Listings
@app.route('/brand/<int:brand_id>')
def brand(brand_id):
    """View listings by brand."""
    brand = Brand.query.get_or_404(brand_id)
    listings = Listing.query.filter_by(brand_id=brand_id).all()
    brands = Brand.query.all()
    return render_template('home.html', brands=brands, listings=listings)


# Context Processor: Load Brands
@app.context_processor
def load_brands():
    """Inject brands into templates."""
    brands = Brand.query.all()
    return dict(brands=brands)


# Context Processor: Load Categories
@app.context_processor
def load_categories():
    """Inject categories into templates."""
    categories = Category.query.all()
    return dict(categories=categories)


# View: Listing Details
@app.route('/listing/<int:listing_id>')
def listing_details(listing_id):
    """View details of a specific listing."""
    listing = Listing.query.get_or_404(listing_id)
    
    if current_user.is_authenticated and current_user.is_admin:
        # Render admin-specific details page
        return render_template('admin_details.html', listing=listing)
    
    # Render general details page for non-admin users
    return render_template('details.html', listing=listing)


# View: Search Listings
@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for listings."""
    query = request.args.get('query', '').strip()
    results = []

    if query:
        results = Listing.query.filter(
            Listing.title.ilike(f'%{query}%') |
            Listing.description.ilike(f'%{query}%') |
            Listing.location.ilike(f'%{query}%')
        ).all()

    return render_template('search.html', query=query, results=results)


# View: Toggle Favorite
@app.route('/favorites/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    """Toggle favorite status of a listing."""
    item_id = request.json.get('item_id')
    item = Listing.query.get(item_id)

    if not item:
        return jsonify({'error': 'Item not found'}), 404

    if item in current_user.favorites:
        current_user.favorites.remove(item)
        db.session.commit()
        return jsonify({'message': 'Item removed from favorites', 'favorited': False}), 200
    else:
        current_user.favorites.append(item)
        db.session.commit()
        return jsonify({'message': 'Item added to favorites', 'favorited': True}), 200


# View: Favorites Page
@app.route('/favorites', methods=['GET'])
@login_required
def favorites_page():
    """View favorite listings."""
    favorites = current_user.favorites.all()
    return render_template('favorites.html', favorites=favorites)


# API: Get All Messages
@app.route('/api/messages', methods=['GET'])
@login_required
def messages():
    """Get received and sent messages."""
    received_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()

    return jsonify({
        'received_messages': [
            {
                'id': msg.id,
                'sender': msg.sender.username,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'parent_id': msg.parent_id
            } for msg in received_messages
        ],
        'sent_messages': [
            {
                'id': msg.id,
                'recipient': msg.recipient.username,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            } for msg in sent_messages
        ]
    })


# API: Reply to a Message
@app.route('/api/messages/reply', methods=['POST'])
@login_required
def reply_to_message():
    """
    API endpoint to reply to an existing message.
    
    Returns a success message or an error response.
    """
    data = request.json
    parent_message_id = data.get('message_id')
    content = data.get('content')

    # Validation
    if not parent_message_id or not content:
        return jsonify({'error': 'Parent message ID and content are required.'}), 400

    parent_message = Message.query.get(parent_message_id)
    if not parent_message:
        return jsonify({'error': 'Parent message not found.'}), 404

    # Check that the current user is the intended recipient of the parent message
    if parent_message.recipient_id != current_user.id:
        return jsonify({'error': 'You can only reply to messages sent to you.'}), 403

    # Save the reply
    try:
        reply = Message(
            sender_id=current_user.id,
            recipient_id=parent_message.sender_id,
            content=content,
            parent_id=parent_message_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(reply)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reply sent successfully!'})
    except Exception as e:
        app.logger.error(f"Error saving reply: {e}")
        return jsonify({'error': 'Failed to send reply.'}), 500


# API: Send a New Message
@app.route('/api/messages/send', methods=['POST'])
@login_required
def send_message():
    """
    API endpoint to send a new message to a recipient.
    """
    data = request.json
    recipient_username = data.get('recipient')
    content = data.get('content')

    if not recipient_username or not content:
        app.logger.error("Missing recipient or content.")
        return jsonify({'error': 'Recipient and content are required.'}), 400

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        app.logger.error(f"Recipient '{recipient_username}' not found.")
        return jsonify({'error': 'User not found.'}), 404

    if recipient.id == current_user.id:
        app.logger.error("User attempted to send message to themselves.")
        return jsonify({'error': 'You cannot send a message to yourself.'}), 400

    try:
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(message)
        db.session.commit()
        app.logger.info(f"Message sent successfully: {message}")
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving message: {e}")
        return jsonify({'error': 'Failed to send message.'}), 500


# View: Render Messages Page
@app.route('/messages')
@login_required
def messages_view():
    """
    Render the messages page for the logged-in user.
    
    Returns the messages.html template.
    """
    return render_template('messages.html')
