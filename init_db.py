import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Debug: Print the DATABASE_URL (remove this after testing)
print(f"DATABASE_URL: {DATABASE_URL[:50]}..." if DATABASE_URL else "DATABASE_URL not found!")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file!")
    print("Make sure your .env file contains:")
    print("DATABASE_URL=postgresql://signup_family_tree_user:...")
    exit(1)

try:
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("Creating tables...")

    # Create users table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_uuid TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_pic BYTEA,
        about_me TEXT,
        datetime_created TIMESTAMP NOT NULL DEFAULT NOW()
        is_admin INTEGER
    );
    ''')
    print("✅ Users table created")

    # Create posts table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        post_uuid TEXT PRIMARY KEY,
        author_uuid TEXT NOT NULL,
        text_content TEXT NOT NULL,
        tag1 TEXT,
        tag2 TEXT,
        tag3 TEXT,
        tag4 TEXT,
        tag5 TEXT,
        location TEXT,
        datetime TEXT,
        image BYTEA
    );
    ''')
    print("✅ Posts table created")

    # Create comments table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        comment_uuid TEXT PRIMARY KEY,
        parent_post_uuid TEXT NOT NULL,
        author_uuid TEXT NOT NULL,
        text_content TEXT NOT NULL,
        datetime TEXT NOT NULL
    );
    ''')
    print("✅ Comments table created")

    # Create indexes
    cur.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_uuid);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(parent_post_uuid);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_uuid);')
    print("✅ Indexes created")

    conn.commit()
    cur.close()
    conn.close()

    print("\n🎉 PostgreSQL database setup completed successfully!")
    print("You can now run your Flask app with USE_POSTGRESQL=true")

except psycopg2.OperationalError as e:
    print(f"❌ Connection Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check that your DATABASE_URL is correct in .env")
    print("2. Verify the database is accessible from your network")
    print("3. Make sure the database exists on Render")

except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()