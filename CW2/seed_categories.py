from app import app, db
from models import Category

# List of categories to seed
categories = [
    'Cars',
    'Animals',
    'Properties',
    'Electronics',
    'Clothing',
    'Furniture',
    'Books',
    'Sports',
    'Tools',
    'Toys',
    'Appliances',
    'Music',
    'Art',
    'Health & Beauty',
    'Collectibles',
    'Gaming',
    'Office Supplies',
    'Garden & Outdoor'
]

# Seed categories into the database
with app.app_context():
    for name in categories:
        # Check if the category already exists
        existing_category = Category.query.filter_by(name=name).first()
        if not existing_category:
            # Add new category
            category = Category(name=name)
            db.session.add(category)
    db.session.commit()
    print("Categories have been successfully seeded!")
