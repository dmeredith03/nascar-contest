"""
Initialize the NASCAR 36 for 36 Contest database with sample data
"""
import database as db

def initialize_contest():
    """Set up the database with initial races and admin user"""
    print("Initializing NASCAR 36 for 36 Contest...")
    
    # Initialize database
    db.init_db()
    print("✓ Database tables created")
    
    # Create admin user (change password after first login!)
    if db.create_user("admin", "admin123", "admin@nascar36.com", is_admin=True):
        print("✓ Admin user created (username: admin, password: admin123)")
        print("  ⚠️  IMPORTANT: Change the admin password after first login!")
    else:
        print("  Admin user already exists")
    
    # Sample NASCAR Cup Series 2026 races
    races_2026 = [
        (1, "Daytona 500", "2026-02-15", "Daytona International Speedway"),
        (2, "Atlanta", "2026-02-22", "Atlanta Motor Speedway"),
        (3, "Las Vegas", "2026-03-01", "Las Vegas Motor Speedway"),
        (4, "Phoenix", "2026-03-08", "Phoenix Raceway"),
        (5, "Bristol", "2026-03-15", "Bristol Motor Speedway"),
        (6, "COTA", "2026-03-22", "Circuit of the Americas"),
        (7, "Richmond", "2026-03-29", "Richmond Raceway"),
        (8, "Martinsville", "2026-04-05", "Martinsville Speedway"),
        (9, "Texas", "2026-04-12", "Texas Motor Speedway"),
        (10, "Talladega", "2026-04-19", "Talladega Superspeedway"),
        (11, "Dover", "2026-04-26", "Dover Motor Speedway"),
        (12, "Kansas", "2026-05-03", "Kansas Speedway"),
        (13, "Darlington", "2026-05-10", "Darlington Raceway"),
        (14, "Charlotte All-Star", "2026-05-17", "Charlotte Motor Speedway"),
        (15, "Coca-Cola 600", "2026-05-24", "Charlotte Motor Speedway"),
        (16, "Gateway", "2026-05-31", "World Wide Technology Raceway"),
        (17, "Sonoma", "2026-06-07", "Sonoma Raceway"),
        (18, "Iowa", "2026-06-14", "Iowa Speedway"),
        (19, "New Hampshire", "2026-06-21", "New Hampshire Motor Speedway"),
        (20, "Nashville", "2026-06-28", "Nashville Superspeedway"),
        (21, "Chicago Street", "2026-07-05", "Chicago Street Course"),
        (22, "Pocono", "2026-07-12", "Pocono Raceway"),
        (23, "Indianapolis", "2026-07-19", "Indianapolis Motor Speedway"),
        (24, "Richmond Night", "2026-08-02", "Richmond Raceway"),
        (25, "Michigan", "2026-08-09", "Michigan International Speedway"),
        (26, "Daytona Summer", "2026-08-23", "Daytona International Speedway"),
        (27, "Darlington Playoff", "2026-08-30", "Darlington Raceway"),
        (28, "Atlanta Playoff", "2026-09-06", "Atlanta Motor Speedway"),
        (29, "Watkins Glen", "2026-09-13", "Watkins Glen International"),
        (30, "Bristol Night Playoff", "2026-09-20", "Bristol Motor Speedway"),
        (31, "Kansas Playoff", "2026-09-27", "Kansas Speedway"),
        (32, "Talladega Playoff", "2026-10-04", "Talladega Superspeedway"),
        (33, "Charlotte Roval", "2026-10-11", "Charlotte Motor Speedway ROVAL"),
        (34, "Las Vegas Playoff", "2026-10-18", "Las Vegas Motor Speedway"),
        (35, "Martinsville Playoff", "2026-11-01", "Martinsville Speedway"),
        (36, "Phoenix Championship", "2026-11-08", "Phoenix Raceway"),
    ]
    
    races_added = 0
    for race_number, race_name, race_date, track in races_2026:
        if db.create_race(race_number, race_name, race_date, track):
            races_added += 1
    
    print(f"✓ Added {races_added} races to the schedule")
    
    print("\n" + "="*60)
    print("Setup complete! 🏁")
    print("="*60)
    print("\nTo start the application, run:")
    print("  streamlit run app.py")
    print("\nAdmin Login:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  Remember to change the admin password!")
    print("="*60)

if __name__ == "__main__":
    initialize_contest()
