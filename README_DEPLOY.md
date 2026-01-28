# Quick Deploy Guide

## Deploy to Streamlit Cloud (5 minutes)

### Step 1: Push to GitHub
```bash
cd /home/dmeredith/cfb/NASCAR
git init
git add .
git commit -m "NASCAR 36 for 36 Contest App"
```

Create a new repo at https://github.com/new, then:
```bash
git remote add origin https://github.com/YOUR_USERNAME/nascar-contest.git
git push -u origin main
```

### Step 2: Deploy
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set **Main file path**: `app.py`
6. Click "Deploy"

### Step 3: Initialize
1. Wait for deployment (2-3 minutes)
2. Visit your app URL
3. Create admin account immediately
4. Add races via admin panel

### ⚠️ Critical Warning

**Streamlit Cloud resets the database every ~7 days!**

You MUST either:
- Download database backups regularly, OR
- Use a cloud database (see DEPLOYMENT.md)

For a real contest, use a cloud database service.

## Your App Will Be Live At:
`https://YOUR_USERNAME-nascar-contest.streamlit.app`

## Next Steps
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Set up database backups
- Test all features before launching contest
