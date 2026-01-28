# NASCAR 36 for 36 Contest

A one-and-done style NASCAR contest where participants pick one driver for each of the 36 Cup Series races. Each driver can only be picked once throughout the season!

## Features

- 🏁 **One-and-Done Format**: Pick 36 different drivers across 36 races
- 👥 **User Authentication**: Secure login and registration system
- 📊 **Live Leaderboard**: Track standings throughout the season
- 🏎️ **Easy Pick Management**: Simple interface to make and view picks
- ⚙️ **Admin Panel**: Manage races and enter results
- 📈 **Points Tracking**: Automatic point calculation and leaderboard updates

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Navigate to the NASCAR directory:
```bash
cd NASCAR
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python initialize_db.py
```

### Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Default Admin Access

- **Username**: admin
- **Password**: admin123

⚠️ **IMPORTANT**: Change the admin password immediately after first login!

## How It Works

### For Participants

1. **Sign Up**: Create an account with username, email, and password
2. **Make Picks**: Each week, pick one driver for the upcoming race
3. **One-and-Done Rule**: You cannot pick the same driver twice!
4. **Track Progress**: View your picks, points, and leaderboard position
5. **Compete**: Accumulate points throughout the season to win

### For Admins

1. **Manage Races**: Add or modify race information
2. **Enter Results**: Input race results to calculate points
3. **Points System**: 
   - 1st place: 40 points
   - 2nd place: 35 points
   - 3rd place: 34 points
   - And so on...

## Points System

The contest uses total points earned per race, which includes:
- **Stage Points**: Points earned during Stage 1 and Stage 2
- **Finish Position Points**: Points based on final finishing position
- **Bonus Points**: Any playoff/other bonus points

Admins calculate and enter the total points for each driver after the race.

### Uploading Results

Admins can upload race results via CSV file:
1. Go to Admin Panel → Enter Results
2. Select the race
3. Upload a CSV file with columns: `driver_name`, `total_points`
4. Preview the results (drivers automatically ranked by points)
5. Click "Submit Results from CSV"

The system will automatically assign finishing positions based on total points (highest points = 1st place).

See [sample_race_results.csv](sample_race_results.csv) for an example format.

## Files

- `app.py`: Main Streamlit application
- `database.py`: Database operations and models
- `initialize_db.py`: Database initialization script
- `requirements.txt`: Python dependencies
- `nascar_contest.db`: SQLite database (created after initialization)
- `sample_race_results.csv`: Example CSV template for uploading race results

## Database Location

The SQLite database is stored in the same directory as the application:
- **Path**: `NASCAR/nascar_contest.db`
- **Type**: SQLite3 database file
- **Access**: Can be viewed with any SQLite browser or the `sqlite3` command-line tool

To view the database:
```bash
# Using sqlite3 command line
sqlite3 nascar_contest.db

# Example queries:
# .tables                  - Show all tables
# SELECT * FROM users;     - View all users
# SELECT * FROM races;     - View all races
# SELECT * FROM picks;     - View all picks
```

## Contest Rules

1. **36 Races, 36 Drivers**: Pick exactly one driver per race, all must be different
2. **No Reuse**: Once you pick a driver, they're locked for the season
3. **Deadline**: Picks must be made before the race is marked complete
4. **Points**: Awarded based on finishing position
5. **Winner**: Highest total points after 36 races wins!

## Tips for Players

- 🎯 **Strategy Matters**: Save top drivers for important races
- 📅 **Plan Ahead**: Look at the full schedule to optimize picks
- 🏟️ **Track Specialties**: Consider driver performance at specific tracks
- ⏰ **Don't Forget**: Make picks before each race!

## Customization

You can customize:
- Driver lists in `app.py` (show_picks_page function)
- Points system in `app.py` (show_admin_page function)
- Race schedule in `initialize_db.py`
- UI theme and styling in `app.py`

## Support

For issues or questions, contact your contest administrator.

## License

This project is open source and available for personal use.

---

**Good luck and enjoy the season! 🏁🏆**
