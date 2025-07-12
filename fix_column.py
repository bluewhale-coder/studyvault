from app import app, db
from sqlalchemy import text

with app.app_context():
    # Add 'public_id' column to 'gallery' table
    with db.engine.connect() as conn:
        conn.execute(text('ALTER TABLE gallery ADD COLUMN public_id VARCHAR(100)'))
    print("Column 'public_id' added successfully.")