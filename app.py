import streamlit as st
import database as db
from datetime import datetime
import pandas as pd
import io

# Page config
st.set_page_config(
    page_title="NASCAR 36 for 36 Contest",
    page_icon="🏁",
    layout="wide"
)

# Initialize database
db.init_db()

# Auto-create admin user on first run if it doesn't exist
try:
    if not db.verify_user("admin", "admin123"):
        db.create_user("admin", "admin123", "admin@nascar36.com", is_admin=True)
except:
    pass

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'


def show_login_page():
    """Display login/signup page"""
    st.title("🏁 NASCAR 36 for 36 Contest")
    st.markdown("### One and Done - Pick 36 Different Drivers for 36 Races")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = 'home'
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        st.subheader("Create Account")
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            new_password_confirm = st.text_input("Confirm Password", type="password")
            signup = st.form_submit_button("Sign Up")
            
            if signup:
                if not all([new_username, new_email, new_password, new_password_confirm]):
                    st.warning("Please fill in all fields")
                elif new_password != new_password_confirm:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if db.create_user(new_username, new_password, new_email):
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username or email already exists")


def show_home_page():
    """Display home page with navigation"""
    st.title("🏁 NASCAR 36 for 36 Contest")
    st.markdown(f"Welcome, **{st.session_state.user['username']}**!")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        if st.button("🏠 Home", width='stretch'):
            st.session_state.page = 'home'
        if st.button("🏎️ Make Picks", width='stretch'):
            st.session_state.page = 'picks'
        if st.button("📊 Leaderboard", width='stretch'):
            st.session_state.page = 'leaderboard'
        if st.button("📋 My Picks", width='stretch'):
            st.session_state.page = 'my_picks'
        if st.button("👥 All Picks", width='stretch'):
            st.session_state.page = 'all_picks'
        if st.button("📖 Rules", width='stretch'):
            st.session_state.page = 'rules'
        
        if st.session_state.user['is_admin']:
            st.divider()
            st.header("Admin")
            if st.button("⚙️ Admin Panel", width='stretch'):
                st.session_state.page = 'admin'
        
        st.divider()
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content based on selected page
    if st.session_state.page == 'home':
        show_dashboard()
    elif st.session_state.page == 'picks':
        show_picks_page()
    elif st.session_state.page == 'leaderboard':
        show_leaderboard_page()
    elif st.session_state.page == 'my_picks':
        show_my_picks_page()
    elif st.session_state.page == 'all_picks':
        show_all_picks_page()
    elif st.session_state.page == 'rules':
        show_rules_page()
    elif st.session_state.page == 'admin' and st.session_state.user['is_admin']:
        show_admin_page()


def show_dashboard():
    """Display dashboard with contest overview"""
    st.header("Contest Overview")
    
    col1, col2, col3 = st.columns(3)
    
    # Get stats
    races = db.get_all_races()
    completed_races = [r for r in races if r['is_completed']]
    next_race = db.get_next_race()
    user_picks = db.get_user_picks(st.session_state.user['id'])
    
    with col1:
        st.metric("Total Races", len(races))
    with col2:
        st.metric("Completed Races", len(completed_races))
    with col3:
        st.metric("Your Picks Made", len(user_picks))
    
    st.divider()
    
    # Next race info
    if next_race:
        st.subheader("📍 Next Race")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{next_race['race_name']}**")
            st.markdown(f"🏟️ {next_race['track']}")
            st.markdown(f"📅 {next_race['race_date']}")
        with col2:
            user_pick = db.get_user_pick_for_race(st.session_state.user['id'], next_race['id'])
            if user_pick:
                st.success(f"✅ Your pick: {user_pick['driver_name']}")
            else:
                st.warning("⚠️ No pick yet")
                if st.button("Make Pick Now"):
                    st.session_state.page = 'picks'
                    st.rerun()
    else:
        st.info("No upcoming races. Check with admin.")
    
    st.divider()
    
    # Quick leaderboard
    st.subheader("🏆 Top 5 Leaderboard")
    leaderboard = db.get_leaderboard()[:5]
    if leaderboard:
        df = pd.DataFrame(leaderboard)
        df['rank'] = range(1, len(df) + 1)
        df = df[['rank', 'username', 'total_points', 'picks_made']]
        df.columns = ['Rank', 'Username', 'Total Points', 'Picks Made']
        st.dataframe(df, hide_index=True, width='stretch')
    else:
        st.info("No standings yet")


def show_picks_page():
    """Display picks interface"""
    st.header("🏎️ Make Your Picks")
    
    # Get next race
    next_race = db.get_next_race()
    
    if not next_race:
        st.warning("No upcoming races available for picks")
        return
    
    st.subheader(f"Race {next_race['race_number']}: {next_race['race_name']}")
    st.markdown(f"**Track:** {next_race['track']}")
    st.markdown(f"**Date:** {next_race['race_date']}")
    
    # Auto-assign picks on race day for users who haven't picked
    from datetime import datetime, date
    try:
        race_date = datetime.strptime(next_race['race_date'], '%Y-%m-%d').date()
        today = date.today()
        
        # If it's race day or later, auto-assign picks for users who haven't picked
        if today >= race_date:
            # Only run once per session to avoid repeated assignments
            session_key = f"auto_assigned_race_{next_race['id']}"
            if session_key not in st.session_state:
                # Get all drivers list
                all_drivers = [
                    "Kyle Larson", "Chase Elliott", "Tyler Reddick", "Christopher Bell",
                    "William Byron", "Denny Hamlin", "Kyle Busch", "Martin Truex Jr.",
                    "Ross Chastain", "Ryan Blaney", "Joey Logano", "Brad Keselowski",
                    "Chris Buescher", "Bubba Wallace", "Alex Bowman", "Daniel Suarez",
                    "Austin Cindric", "Chase Briscoe", "AJ Allmendinger", "Michael McDowell",
                    "Ricky Stenhouse Jr.", "Ty Gibbs", "Todd Gilliland", "Corey LaJoie",
                    "Erik Jones", "Justin Haley", "Noah Gragson", "Zane Smith",
                    "Carson Hocevar", "Ryan Preece", "Harrison Burton", "Josh Berry",
                    "Kaz Grala", "Ty Dillon", "John Hunter Nemechek", "Austin Dillon"
                ]
                
                assigned_count, errors = db.auto_assign_picks(next_race['id'], all_drivers)
                
                if assigned_count > 0:
                    st.info(f"🎲 Auto-assigned {assigned_count} random pick(s) to users who didn't pick before race day")
                
                if errors:
                    with st.expander("⚠️ Auto-assignment issues"):
                        for error in errors:
                            st.warning(error)
                
                st.session_state[session_key] = True
    except Exception as e:
        pass  # Silently handle date parsing errors
    
    # Get used drivers
    used_drivers = db.get_used_drivers(st.session_state.user['id'])
    
    if used_drivers:
        st.warning(f"⚠️ You have already used {len(used_drivers)} drivers. You cannot pick them again!")
        with st.expander("View Used Drivers"):
            st.write(", ".join(sorted(used_drivers)))
    
    # Check if user already made a pick
    existing_pick = db.get_user_pick_for_race(st.session_state.user['id'], next_race['id'])
    
    if existing_pick:
        st.success(f"✅ Current pick: **{existing_pick['driver_name']}**")
        st.info("You can change your pick until race day")
    
    # Driver selection
    st.divider()
    st.subheader("Select Your Driver")
    
    # Common NASCAR drivers (you can expand this list)
    all_drivers = [
        "Kyle Larson", "Chase Elliott", "Tyler Reddick", "Christopher Bell",
        "William Byron", "Denny Hamlin", "Kyle Busch", "Martin Truex Jr.",
        "Ross Chastain", "Ryan Blaney", "Joey Logano", "Brad Keselowski",
        "Chris Buescher", "Bubba Wallace", "Alex Bowman", "Daniel Suarez",
        "Austin Cindric", "Chase Briscoe", "AJ Allmendinger", "Michael McDowell",
        "Ricky Stenhouse Jr.", "Ty Gibbs", "Todd Gilliland", "Corey LaJoie",
        "Erik Jones", "Justin Haley", "Noah Gragson", "Zane Smith",
        "Carson Hocevar", "Ryan Preece", "Harrison Burton", "Josh Berry",
        "Kaz Grala", "Ty Dillon", "John Hunter Nemechek", "Austin Dillon"
    ]
    
    # Filter out used drivers
    available_drivers = [d for d in all_drivers if d not in used_drivers]
    available_drivers.sort()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if available_drivers:
            selected_driver = st.selectbox(
                "Choose a driver",
                [""] + available_drivers,
                index=0 if not existing_pick else (available_drivers.index(existing_pick['driver_name']) + 1 if existing_pick['driver_name'] in available_drivers else 0)
            )
        else:
            st.error("You have used all available drivers!")
            selected_driver = None
    
    with col2:
        st.metric("Available", len(available_drivers))
    
    # Submit pick
    if selected_driver:
        if st.button("🏁 Submit Pick", type="primary", width='stretch'):
            success, message = db.make_pick(
                st.session_state.user['id'],
                next_race['id'],
                selected_driver
            )
            if success:
                st.success(message)
                st.balloons()
                st.rerun()
            else:
                st.error(message)


def show_leaderboard_page():
    """Display full leaderboard"""
    st.header("🏆 Leaderboard")
    
    leaderboard = db.get_leaderboard()
    
    if leaderboard:
        df = pd.DataFrame(leaderboard)
        df['rank'] = range(1, len(df) + 1)
        
        # Highlight current user
        df['is_current_user'] = df['username'] == st.session_state.user['username']
        
        # Display
        st.dataframe(
            df[['rank', 'username', 'total_points', 'picks_made']],
            column_config={
                'rank': 'Rank',
                'username': 'Username',
                'total_points': st.column_config.NumberColumn('Total Points', format="%d"),
                'picks_made': st.column_config.NumberColumn('Picks Made', format="%d")
            },
            hide_index=True,
            width='stretch'
        )
        
        # User's position
        user_position = next((i+1 for i, entry in enumerate(leaderboard) if entry['username'] == st.session_state.user['username']), None)
        if user_position:
            st.info(f"Your current position: **#{user_position}** out of {len(leaderboard)}")
    else:
        st.info("No standings yet")


def show_my_picks_page():
    """Display user's pick history"""
    st.header("📋 My Picks")
    
    picks = db.get_user_picks(st.session_state.user['id'])
    
    if picks:
        df = pd.DataFrame(picks)
        df['status'] = df['is_completed'].apply(lambda x: '✅ Complete' if x else '⏳ Pending')
        
        display_df = df[['race_number', 'race_name', 'race_date', 'driver_name', 'points', 'status']]
        display_df.columns = ['Race #', 'Race Name', 'Date', 'Driver', 'Points', 'Status']
        
        st.dataframe(display_df, hide_index=True, width='stretch')
        
        # Summary
        total_points = df['points'].sum()
        completed_picks = df[df['is_completed'] == 1].shape[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Points", int(total_points))
        with col2:
            st.metric("Completed Races", completed_picks)
        with col3:
            st.metric("Pending Picks", len(picks) - completed_picks)
    else:
        st.info("You haven't made any picks yet!")


def show_all_picks_page():
    """Display all users' picks for races"""
    st.header("👥 All Picks by Race")
    
    from datetime import datetime, date
    
    races = db.get_all_races()
    
    if not races:
        st.info("No races available yet")
        return
    
    # Filter to show only races that have reached race day or are completed
    today = date.today()
    available_races = []
    for race in races:
        try:
            race_date = datetime.strptime(race['race_date'], '%Y-%m-%d').date()
            if today >= race_date or race['is_completed']:
                available_races.append(race)
        except:
            # If date parsing fails, include the race
            available_races.append(race)
    
    if not available_races:
        st.info("No race picks are available to view yet. Picks become visible on race day.")
        return
    
    race_options = {f"Race {r['race_number']}: {r['race_name']} ({r['race_date']})": r for r in available_races}
    
    selected_race_name = st.selectbox("Select a race to view picks", list(race_options.keys()))
    selected_race = race_options[selected_race_name]
    
    st.divider()
    
    # Race details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Track:** {selected_race['track']}")
    with col2:
        st.markdown(f"**Date:** {selected_race['race_date']}")
    with col3:
        status = "✅ Completed" if selected_race['is_completed'] else "⏳ Upcoming"
        st.markdown(f"**Status:** {status}")
    
    st.divider()
    
    # Get all picks for this race
    all_picks = db.get_all_picks_for_race(selected_race['id'])
    
    if all_picks:
        st.subheader(f"Picks ({len(all_picks)} participants)")
        
        df = pd.DataFrame(all_picks)
        
        # Sort by points if race is completed, otherwise by username
        if selected_race['is_completed']:
            df = df.sort_values('points', ascending=False)
            display_df = df[['username', 'driver_name', 'points']]
            display_df.columns = ['Username', 'Driver Pick', 'Points Earned']
        else:
            df = df.sort_values('username')
            display_df = df[['username', 'driver_name']]
            display_df.columns = ['Username', 'Driver Pick']
        
        st.dataframe(display_df, hide_index=True, width='stretch')
        
        # Show summary stats
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Most Popular Picks")
            driver_counts = df['driver_name'].value_counts().head(5)
            if not driver_counts.empty:
                for driver, count in driver_counts.items():
                    st.write(f"🏎️ **{driver}**: {count} pick(s)")
            else:
                st.info("No picks yet")
        
        with col2:
            if selected_race['is_completed']:
                st.subheader("Top Scorers This Race")
                top_scorers = df.nlargest(5, 'points')[['username', 'driver_name', 'points']]
                for idx, row in top_scorers.iterrows():
                    st.write(f"🏆 **{row['username']}** - {row['driver_name']} ({int(row['points'])} pts)")
    else:
        st.info("No picks have been made for this race yet")


def show_rules_page():
    """Display contest rules"""
    st.header("📖 Contest Rules")
    
    st.markdown("""
    ## NASCAR 36 for 36 - One and Done Contest
    
    ### Format
    
    - 36 Cup Series races
    - Pick one driver per race
    - Each driver can only be used once all season
    - No re-use of drivers under any circumstances
    
    ---
    
    ### Points System
    
    You receive the total points your selected driver earns in the race. Points are awarded as follows:
    
    **Race Finish Points (2026):**
    
    | Place | Points | Place | Points | Place | Points | Place | Points |
    |-------|--------|-------|--------|-------|--------|-------|--------|
    | 1st   | 55     | 11th  | 26     | 21st  | 16     | 31st  | 6      |
    | 2nd   | 35     | 12th  | 25     | 22nd  | 15     | 32nd  | 5      |
    | 3rd   | 34     | 13th  | 24     | 23rd  | 14     | 33rd  | 4      |
    | 4th   | 33     | 14th  | 23     | 24th  | 13     | 34th  | 3      |
    | 5th   | 32     | 15th  | 22     | 25th  | 12     | 35th  | 2      |
    | 6th   | 31     | 16th  | 21     | 26th  | 11     | 36th  | 1      |
    | 7th   | 30     | 17th  | 20     | 27th  | 10     | 37th  | 1      |
    | 8th   | 29     | 18th  | 19     | 28th  | 9      | 38th  | 1      |
    | 9th   | 28     | 19th  | 18     | 29th  | 8      | 39th  | 1      |
    | 10th  | 27     | 20th  | 17     | 30th  | 7      | 40th  | 1      |
    
    **Stage Points (Stages 1 & 2):**
    
    Top 10 finishers in each stage: 1st = 10, 2nd = 9, 3rd = 8, 4th = 7, 5th = 6, 6th = 5, 7th = 4, 8th = 3, 9th = 2, 10th = 1
    
    **Fastest Lap Bonus:**
    
    1 point to the driver who records the fastest single lap (once a car enters the garage, it's no longer eligible)
    
    **Maximum Points:** Win both stages + win race + fastest lap = 10 + 10 + 55 + 1 = 76 points
    
    ---
    
    ### Picking Deadline
    
    Picks must be submitted by 12:00 AM (midnight) on race day. After this time:
    - Picks are locked and cannot be changed
    - Users who have not picked will be auto-assigned a random available driver
    - No late picks are accepted once the race has started
    
    ---
    
    ### Scoring and Standings
    
    - Total points accumulated across all 36 races determines the winner
    - Tiebreaker: Number of 1st place finishes
    - Leaderboard updates after each race
    
    ---
    
    ### Strategy Tips
    
    **Track Types:**
    - Superspeedways (Daytona, Talladega, Atlanta): Unpredictable, anyone can win
    - Road Courses: Specialists like Allmendinger, van Gisbergen often excel
    - Short Tracks (Bristol, Martinsville): High-contact, technical driving matters
    - Intermediates (1.5-mile ovals): Where elite drivers typically dominate
    
    **Resources:**
    - Use tools like LapRaptor to analyze driver performance by track type
    - Review historical results at specific tracks before making picks
    - Plan your season strategy before the first race
    
    **Common Mistakes to Avoid:**
    - Using top drivers too early in the season
    - Not accounting for track-specific performance
    - Failing to save specialists for their best tracks
    
    🏁 Good luck.
    """)


def show_admin_page():
    """Display admin panel"""
    st.header("⚙️ Admin Panel")
    
    tab1, tab2, tab3 = st.tabs(["Manage Races", "Enter Results", "Manage Entries"])
    
    with tab1:
        st.subheader("Add New Race")
        with st.form("add_race_form"):
            col1, col2 = st.columns(2)
            with col1:
                race_number = st.number_input("Race Number", min_value=1, max_value=36, value=1)
                race_name = st.text_input("Race Name")
            with col2:
                race_date = st.date_input("Race Date")
                track = st.text_input("Track")
            
            if st.form_submit_button("Add Race"):
                if race_name and track:
                    if db.create_race(race_number, race_name, str(race_date), track):
                        st.success("Race added!")
                        st.rerun()
                    else:
                        st.error("Race number already exists")
                else:
                    st.warning("Please fill all fields")
        
        st.divider()
        st.subheader("All Races")
        races = db.get_all_races()
        if races:
            df = pd.DataFrame(races)
            df['status'] = df['is_completed'].apply(lambda x: '✅ Complete' if x else '⏳ Upcoming')
            display_df = df[['race_number', 'race_name', 'race_date', 'track', 'status']]
            display_df.columns = ['Race #', 'Race Name', 'Date', 'Track', 'Status']
            st.dataframe(display_df, hide_index=True, width='stretch')
    
    with tab2:
        st.subheader("Enter Race Results")
        
        races = db.get_all_races()
        incomplete_races = [r for r in races if not r['is_completed']]
        
        if incomplete_races:
            race_options = {f"Race {r['race_number']}: {r['race_name']}": r['id'] for r in incomplete_races}
            selected_race_name = st.selectbox("Select Race", list(race_options.keys()))
            selected_race_id = race_options[selected_race_name]
            
            # NASCAR Points System (including stage points)
            st.info("📊 Upload a CSV file with columns: driver_name, total_points")
            st.caption("Total points should include stage points + finish position points")
            
            # CSV Upload option
            st.divider()
            st.subheader("Option 1: Upload CSV File")
            
            uploaded_file = st.file_uploader(
                "Upload race results CSV", 
                type=['csv'],
                help="CSV should have columns: driver_name, total_points"
            )
            
            if uploaded_file is not None:
                try:
                    # Read the CSV
                    df_results = pd.read_csv(uploaded_file)
                    
                    # Validate required columns
                    required_cols = ['driver_name', 'total_points']
                    if not all(col in df_results.columns for col in required_cols):
                        st.error(f"CSV must contain columns: {', '.join(required_cols)}")
                    else:
                        # Sort by points descending to assign finishing positions
                        df_results = df_results.sort_values('total_points', ascending=False).reset_index(drop=True)
                        df_results['finish_position'] = range(1, len(df_results) + 1)
                        
                        # Preview the data
                        st.write("Preview of uploaded results:")
                        preview_df = df_results[['finish_position', 'driver_name', 'total_points']].copy()
                        preview_df.columns = ['Finish Position', 'Driver', 'Total Points']
                        st.dataframe(preview_df.head(20), width='stretch')
                        
                        st.info(f"Total drivers in file: {len(df_results)}")
                        
                        if st.button("✅ Submit Results from CSV", type="primary", width='stretch'):
                            # Prepare results
                            results = []
                            for _, row in df_results.iterrows():
                                results.append({
                                    'driver_name': str(row['driver_name']).strip(),
                                    'finish_position': int(row['finish_position']),
                                    'points': int(row['total_points'])
                                })
                            
                            if db.enter_race_results(selected_race_id, results):
                                st.success("Results entered successfully!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("Error entering results")
                
                except Exception as e:
                    st.error(f"Error processing CSV: {str(e)}")
            
            # Manual entry option
            st.divider()
            st.subheader("Option 2: Manual Entry")
            st.caption("Enter top 10 finishers manually with their total points")
            
            with st.form("results_form"):
                results = []
                
                st.write("Enter driver name and total points (including stage points)")
                cols = st.columns([3, 2])  # Name column wider than points
                
                with cols[0]:
                    st.markdown("**Driver Name**")
                with cols[1]:
                    st.markdown("**Total Points**")
                
                drivers_data = []
                for i in range(10):  # Top 10 finishers
                    cols = st.columns([3, 2])
                    with cols[0]:
                        driver = st.text_input(f"Driver {i+1}", key=f"driver_{i}", label_visibility="collapsed")
                    with cols[1]:
                        points = st.number_input(f"Points {i+1}", min_value=0, value=0, key=f"points_{i}", label_visibility="collapsed")
                    
                    if driver and points > 0:
                        drivers_data.append({
                            'driver_name': driver.strip(),
                            'total_points': points
                        })
                
                if st.form_submit_button("Submit Manual Results"):
                    if drivers_data:
                        # Sort by points to determine finish positions
                        drivers_data.sort(key=lambda x: x['total_points'], reverse=True)
                        
                        results = []
                        for idx, driver_info in enumerate(drivers_data):
                            results.append({
                                'driver_name': driver_info['driver_name'],
                                'finish_position': idx + 1,
                                'points': driver_info['total_points']
                            })
                        
                        if db.enter_race_results(selected_race_id, results):
                            st.success("Results entered successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Error entering results")
                    else:
                        st.warning("Please enter at least one driver with points")
        else:
            st.info("No incomplete races available")
    
    with tab3:
        st.subheader("👥 Manage Entries")
        
        users = db.get_all_users()
        
        if users:
            st.info(f"Total participants: {len(users)}")
            
            # Summary stats
            paid_count = sum(1 for u in users if u['paid'])
            unpaid_count = len(users) - paid_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entries", len(users))
            with col2:
                st.metric("✅ Paid", paid_count)
            with col3:
                st.metric("⏳ Unpaid", unpaid_count)
            
            st.divider()
            
            # Display users with payment checkboxes
            st.subheader("Participant List")
            
            # Create a dataframe for display
            df = pd.DataFrame(users)
            df['joined'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
            
            # Interactive payment management
            for idx, user in enumerate(users):
                col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
                
                with col1:
                    st.text(f"👤 {user['username']}")
                
                with col2:
                    st.text(f"📧 {user['email']}")
                
                with col3:
                    st.text(f"📅 {user['joined']}")
                
                with col4:
                    # Payment checkbox
                    paid_status = st.checkbox(
                        "Paid",
                        value=bool(user['paid']),
                        key=f"paid_{user['id']}",
                        label_visibility="visible"
                    )
                    
                    # Update if changed
                    if paid_status != bool(user['paid']):
                        if db.update_user_payment_status(user['id'], paid_status):
                            st.rerun()
                
                if idx < len(users) - 1:
                    st.divider()
            
            # Export option
            st.divider()
            st.subheader("📥 Export Data")
            
            # Create export dataframe
            export_df = pd.DataFrame(users)
            export_df['paid_status'] = export_df['paid'].apply(lambda x: 'Yes' if x else 'No')
            export_df = export_df[['username', 'email', 'paid_status', 'created_at']]
            export_df.columns = ['Username', 'Email', 'Paid', 'Join Date']
            
            # Convert to CSV
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📄 Download Participant List (CSV)",
                data=csv,
                file_name=f"nascar_participants_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
            )
        else:
            st.info("No participants yet")


# Main app logic
def main():
    if st.session_state.user is None:
        show_login_page()
    else:
        show_home_page()


if __name__ == "__main__":
    main()
