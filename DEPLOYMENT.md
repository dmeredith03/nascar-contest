# Deploying NASCAR 36 for 36 to Streamlit Cloud

## Quick Start

### Option 1: Deploy to Streamlit Cloud (Recommended for Testing)

1. **Create a GitHub Repository**
   ```bash
   cd NASCAR
   git init
   git add .
   git commit -m "Initial commit - NASCAR 36 for 36 Contest"
   ```

2. **Push to GitHub**
   - Create a new repository on GitHub (https://github.com/new)
   - Follow the instructions to push your local repository:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/nascar-contest.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `app.py`
   - Click "Deploy"

4. **Initialize the Database**
   - Once deployed, you'll need to run the initialization
   - The database will be created automatically on first run
   - **Important**: Create admin account immediately after first deployment

## Important Considerations

### ⚠️ Database Persistence Issue

**Streamlit Cloud uses ephemeral storage**, meaning:
- The SQLite database will be **reset every time the app restarts** (every ~7 days or on redeployment)
- All user data, picks, and results will be lost on restart

### Solutions for Production Use

**Option A: Regular Backups (Quick Fix)**
- Download the database regularly via admin panel
- Keep backups on your local machine
- Re-upload when app restarts

**Option B: Use Cloud Database (Recommended for Production)**
- Migrate to PostgreSQL, MySQL, or MongoDB
- Use services like:
  - Neon (serverless Postgres - free tier available)
  - PlanetScale (MySQL - free tier available)
  - MongoDB Atlas (free tier available)
  - Supabase (Postgres - free tier available)

**Option C: Use Streamlit Secrets for Initialization**
- Store initialization data in Streamlit secrets
- Auto-recreate basic setup on restart

## For Production Deployment

If you want a permanent solution for actual contest use:

### Recommended: Use Neon Postgres (Free)

1. **Sign up at https://neon.tech**

2. **Update database.py** to use PostgreSQL instead of SQLite

3. **Add connection string to Streamlit secrets**:
   - In Streamlit Cloud dashboard → Settings → Secrets
   - Add:
   ```toml
   [database]
   connection_string = "postgresql://user:pass@host/dbname"
   ```

### Alternative: Self-Host

Host on a VPS with persistent storage:
- DigitalOcean ($6/month)
- Linode ($5/month)  
- AWS EC2 (free tier for 1 year)

## Testing Deployment

After deploying:
1. Visit your app URL
2. Create admin account (username: admin)
3. Log in and add races
4. Test user signup and pick functionality
5. **Backup your database immediately**

## Maintenance

- **Weekly**: Download database backup
- **Before each race**: Verify race is added
- **After each race**: Enter results promptly
- **Monitor**: Check app logs for errors in Streamlit Cloud dashboard

## Support

For issues:
- Check Streamlit Cloud logs
- Verify all dependencies in requirements.txt
- Ensure database permissions are correct

---

**For a real contest with money involved, strongly recommend using a cloud database service instead of SQLite on Streamlit Cloud!**
