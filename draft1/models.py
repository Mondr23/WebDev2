from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Many-to-Many Relationship Table
user_favorites = db.Table(
    'user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cars = db.relationship('Car', backref='owner', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)

    # Relationship to Listings (items posted by the user)
    listings = db.relationship('Listing', back_populates='owner', lazy=True)

    # Relationship to Favorited Listings
    favorites = db.relationship('Listing', secondary=user_favorites, backref='favorited_by', lazy='dynamic')

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(50), nullable=True, default='default.jpg') 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    model = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    mileage = db.Column(db.Integer, nullable=True)  
    fuel_type = db.Column(db.String(50), nullable=True)
    transmission = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)

    # Relationships
    owner = db.relationship('User', back_populates='listings')
    category = db.relationship('Category', back_populates='listings')
    images = db.relationship('ListingImage', back_populates='listing', cascade='all, delete-orphan')
    brand = db.relationship('Brand', back_populates='listings')  # Relationship with the Brand model

class ListingImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    image_file = db.Column(db.String(255), nullable=False)

    # Relationship back to the listing
    listing = db.relationship('Listing', back_populates='images')

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship to Listing
    listings = db.relationship('Listing', back_populates='category')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    parent = db.relationship('Message', remote_side=[id], backref='replies')


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

      # Relationship to Listing
    listings = db.relationship('Listing', back_populates='brand')




