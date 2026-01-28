import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import streamlit as st

def get_connection_string():
    """Get database connection string from Streamlit secrets or environment"""
    if hasattr(st, 'secrets') and 'database' in st.secrets:
        return st.secrets['database']['connection_string']
    return os.environ.get('DATABASE_URL', '')

def get_connection():
    """Get database connection"""
    conn = psycopg2.connect(get_connection_string(), cursor_factory=RealDictCursor)
    return conn


def init_db():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            is_admin INTEGER DEFAULT 0,
            paid INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Races table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS races (
            id SERIAL PRIMARY KEY,
            race_number INTEGER UNIQUE NOT NULL,
            race_name TEXT NOT NULL,
            race_date TEXT NOT NULL,
            track TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS picks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            race_id INTEGER NOT NULL,
            driver_name TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (race_id) REFERENCES races(id),
            UNIQUE(user_id, race_id)
        )
    ''')
    
    # Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            race_id INTEGER NOT NULL,
            driver_name TEXT NOT NULL,
            finish_position INTEGER NOT NULL,
            points INTEGER NOT NULL,
            FOREIGN KEY (race_id) REFERENCES races(id),
            UNIQUE(race_id, driver_name)
        )
    ''')
    
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str, email: str, is_admin: bool = False) -> bool:
    """Create a new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, password_hash, email, is_admin) VALUES (%s, %s, %s, %s)',
            (username, password_hash, email, 1 if is_admin else 0)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


def verify_user(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials and return user data"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute(
        'SELECT id, username, email, is_admin FROM users WHERE username = %s AND password_hash = %s',
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None


def get_all_races() -> List[Dict]:
    """Get all races ordered by race number"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM races ORDER BY race_number')
    races = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return races


def get_next_race() -> Optional[Dict]:
    """Get the next incomplete race"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM races WHERE is_completed = 0 ORDER BY race_number LIMIT 1'
    )
    race = cursor.fetchone()
    conn.close()
    return dict(race) if race else None


def get_race_by_id(race_id: int) -> Optional[Dict]:
    """Get race by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM races WHERE id = %s', (race_id,))
    race = cursor.fetchone()
    conn.close()
    return dict(race) if race else None


def create_race(race_number: int, race_name: str, race_date: str, track: str) -> bool:
    """Create a new race"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO races (race_number, race_name, race_date, track) VALUES (%s, %s, %s, %s)',
            (race_number, race_name, race_date, track)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating race: {e}")
        return False


def make_pick(user_id: int, race_id: int, driver_name: str) -> Tuple[bool, str]:
    """Make a pick for a race. Returns (success, message)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if driver has already been used by this user
    cursor.execute('''
        SELECT COUNT(*) as count FROM picks 
        WHERE user_id = %s AND driver_name = %s
    ''', (user_id, driver_name))
    
    result = cursor.fetchone()
    count = result['count']
    if count > 0:
        conn.close()
        return False, f"You have already used {driver_name} in a previous race!"
    
    # Check if race is still open
    cursor.execute('SELECT is_completed FROM races WHERE id = %s', (race_id,))
    race = cursor.fetchone()
    if not race:
        conn.close()
        return False, "Race not found"
    
    if race['is_completed']:
        conn.close()
        return False, "This race is already completed"
    
    # Make the pick (INSERT or UPDATE)
    try:
        cursor.execute('''
            INSERT INTO picks (user_id, race_id, driver_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, race_id) 
            DO UPDATE SET driver_name = EXCLUDED.driver_name
        ''', (user_id, race_id, driver_name))
        conn.commit()
        conn.close()
        return True, "Pick saved successfully!"
    except Exception as e:
        conn.close()
        return False, f"Error saving pick: {str(e)}"


def get_user_picks(user_id: int) -> List[Dict]:
    """Get all picks for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, r.race_name, r.race_date, r.is_completed, r.race_number
        FROM picks p
        JOIN races r ON p.race_id = r.id
        WHERE p.user_id = %s
        ORDER BY r.race_number
    ''', (user_id,))
    picks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return picks


def get_user_pick_for_race(user_id: int, race_id: int) -> Optional[Dict]:
    """Get user's pick for a specific race"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM picks WHERE user_id = %s AND race_id = %s',
        (user_id, race_id)
    )
    pick = cursor.fetchone()
    conn.close()
    return dict(pick) if pick else None


def get_used_drivers(user_id: int) -> List[str]:
    """Get list of drivers already used by a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT driver_name FROM picks WHERE user_id = %s',
        (user_id,)
    )
    drivers = [row['driver_name'] for row in cursor.fetchall()]
    conn.close()
    return drivers


def enter_race_results(race_id: int, results: List[Dict[str, any]]) -> bool:
    """Enter results for a race. Results should be list of {driver_name, finish_position, points}"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Delete existing results for this race
        cursor.execute('DELETE FROM results WHERE race_id = %s', (race_id,))
        
        # Insert new results
        for result in results:
            cursor.execute(
                'INSERT INTO results (race_id, driver_name, finish_position, points) VALUES (%s, %s, %s, %s)',
                (race_id, result['driver_name'], result['finish_position'], result['points'])
            )
        
        # Update picks with points
        for result in results:
            cursor.execute('''
                UPDATE picks 
                SET points = %s 
                WHERE race_id = %s AND driver_name = %s
            ''', (result['points'], race_id, result['driver_name']))
        
        # Mark race as completed
        cursor.execute('UPDATE races SET is_completed = 1 WHERE id = %s', (race_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error entering results: {e}")
        return False


def get_leaderboard() -> List[Dict]:
    """Get current leaderboard with total points"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            u.id,
            u.username,
            COALESCE(SUM(p.points), 0) as total_points,
            COUNT(p.id) as picks_made
        FROM users u
        LEFT JOIN picks p ON u.id = p.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        ORDER BY total_points DESC, u.username
    ''')
    leaderboard = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return leaderboard


def get_race_results(race_id: int) -> List[Dict]:
    """Get results for a specific race"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM results 
        WHERE race_id = %s 
        ORDER BY finish_position
    ''', (race_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_all_picks_for_race(race_id: int) -> List[Dict]:
    """Get all users' picks for a specific race"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, p.driver_name, p.points, r.is_completed
        FROM picks p
        JOIN users u ON p.user_id = u.id
        JOIN races r ON p.race_id = r.id
        WHERE p.race_id = %s AND u.is_admin = 0
        ORDER BY u.username
    ''', (race_id,))
    picks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return picks


def get_all_users() -> List[Dict]:
    """Get all non-admin users with their details"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, paid, created_at
        FROM users
        WHERE is_admin = 0
        ORDER BY username
    ''')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def update_user_payment_status(user_id: int, paid: bool) -> bool:
    """Update user's payment status"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET paid = %s WHERE id = %s',
            (1 if paid else 0, user_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating payment status: {e}")
        return False


def get_users_without_pick(race_id: int) -> List[Dict]:
    """Get all users who haven't made a pick for a specific race"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username
        FROM users u
        WHERE u.is_admin = 0
        AND u.id NOT IN (
            SELECT user_id FROM picks WHERE race_id = %s
        )
    ''', (race_id,))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def auto_assign_picks(race_id: int, available_drivers: List[str]) -> Tuple[int, List[str]]:
    """Automatically assign random picks to users who haven't picked yet
    Returns: (number of picks assigned, list of errors)"""
    import random
    
    users_without_picks = get_users_without_pick(race_id)
    assigned_count = 0
    errors = []
    
    for user in users_without_picks:
        user_id = user['id']
        username = user['username']
        
        # Get drivers this user has already used
        used_drivers = get_used_drivers(user_id)
        
        # Find available drivers (not used by this user)
        user_available = [d for d in available_drivers if d not in used_drivers]
        
        if user_available:
            # Randomly select a driver
            selected_driver = random.choice(user_available)
            
            # Make the pick
            success, message = make_pick(user_id, race_id, selected_driver)
            if success:
                assigned_count += 1
            else:
                errors.append(f"{username}: {message}")
        else:
            errors.append(f"{username}: No available drivers left")
    
    return assigned_count, errors
