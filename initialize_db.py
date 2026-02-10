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
        (3, "COTA", "2026-03-01", "Circuit of the Americas"),
        (4, "Phoenix", "2026-03-08", "Phoenix Raceway"),
        (5, "Las Vegas", "2026-03-15", "Las Vegas Motor Speedway"),
        (6, "Darlington", "2026-03-22", "Darlington Raceway"),
        (7, "Martinsville", "2026-03-29", "Martinsville Speedway"),
        (8, "Bristol", "2026-04-12", "Bristol Motor Speedway"),
        (9, "Kansas", "2026-04-19", "Kansas Speedway"),
        (10, "Talladega", "2026-04-26", "Talladega Superspeedway"),
        (11, "Texas", "2026-05-03", "Texas Motor Speedway"),
        (12, "Watkins Glen", "2026-05-10", "Watkins Glen International"),
        (13, "Coca-Cola 600", "2026-05-24", "Charlotte Motor Speedway"),
        (14, "Nashville", "2026-05-31", "Nashville Superspeedway"),
        (15, "Michigan", "2026-06-07", "Michigan International Speedway"),
        (16, "Pocono", "2026-06-14", "Pocono Raceway"),
        (17, "San Diego", "2026-06-21", "Coronado Street Course"),
        (18, "Sonoma", "2026-06-28", "Sonoma Raceway"),
        (19, "Chicagoland", "2026-07-05", "Chicagoland Speedway"),
        (20, "Atlanta Summer", "2026-07-12", "Atlanta Motor Speedway"),
        (21, "North Wilkesboro", "2026-07-19", "North Wilkesboro Speedway"),
        (22, "Indianapolis", "2026-07-26", "Indianapolis Motor Speedway"),
        (23, "Iowa", "2026-08-09", "Iowa Speedway"),
        (24, "Richmond", "2026-08-15", "Richmond Raceway"),
        (25, "New Hampshire", "2026-08-23", "New Hampshire Motor Speedway"),
        (26, "Daytona Summer", "2026-08-29", "Daytona International Speedway"),
        (27, "Darlington Playoff", "2026-09-06", "Darlington Raceway"),
        (28, "Gateway", "2026-09-13", "World Wide Technology Raceway"),
        (29, "Bristol Night", "2026-09-19", "Bristol Motor Speedway"),
        (30, "Kansas Playoff", "2026-09-27", "Kansas Speedway"),
        (31, "Las Vegas Playoff", "2026-10-04", "Las Vegas Motor Speedway"),
        (32, "Charlotte Oval", "2026-10-11", "Charlotte Motor Speedway"),
        (33, "Phoenix Playoff", "2026-10-18", "Phoenix Raceway"),
        (34, "Talladega Playoff", "2026-10-25", "Talladega Superspeedway"),
        (35, "Martinsville Playoff", "2026-11-01", "Martinsville Speedway"),
        (36, "Homestead Championship", "2026-11-08", "Homestead-Miami Speedway"),
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
