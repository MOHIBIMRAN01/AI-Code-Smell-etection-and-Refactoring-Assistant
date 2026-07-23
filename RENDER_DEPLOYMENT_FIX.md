# Fix Render Deployment - Switch to SQLite

## Problem
Your Render deployment is still using the old Neon PostgreSQL database, which has exceeded its quota.

Error shown:
```
Your project has exceeded the data transfer quota. Upgrade your plan to increase limits.
```

## Solution
Update your Render environment variables to use SQLite instead of Neon.

---

## Step-by-Step Fix

### 1. Go to Render Dashboard
Visit: https://dashboard.render.com

### 2. Select Your Service
- Click on your deployed service
- Find the name matching your project

### 3. Go to Environment Variables
- Click on "Environment" tab in the left sidebar
- Look for environment variables section

### 4. Update DATABASE_URL
**OLD (Neon PostgreSQL):**
```
DATABASE_URL=postgresql://username:password@neon-hostname.neon.tech/dbname?sslmode=require
```

**NEW (SQLite):**
```
DATABASE_URL=sqlite:////tmp/app.db
```

⚠️ **Important for Render (Ephemeral Filesystem):**
```
DATABASE_URL=sqlite:////tmp/app.db
```

### 5. Save and Deploy
- Click "Save" button
- Trigger a redeploy:
  - Option A: Push new commit to GitHub (auto-redeploys)
  - Option B: Click "Manual Deploy" > "Deploy latest commit"

### 6. Wait for Deployment
- Watch the build logs
- Should complete without database errors now

---

## Why This Works

**SQLite with Render:**
- ✅ No external database service
- ✅ Database file stored locally
- ⚠️ Data persists only during service runtime
- ⚠️ Gets reset when Render instance restarts (ephemeral filesystem)

**For a mini project, this is fine because:**
- Low data volume
- No sensitive data that needs persistence
- Easy to reset and rebuild

---

## If You Need Persistent Data

If you want data to persist across Render restarts, you'll need to:

**Option A: Use Render PostgreSQL Database**
- Create a new PostgreSQL database on Render (free tier available)
- Update DATABASE_URL to new Render PostgreSQL connection

**Option B: Use Another Cloud Database**
- AWS RDS
- Railway
- PlanetScale (MySQL)

---

## Verify It Worked

After deployment:
1. Check Render deployment logs - should start without database errors
2. Visit your API endpoint - should respond

---

## Your Current Setup

**Backend Code:**
- ✅ Already supports SQLite
- ✅ Falls back gracefully if database fails

**Configuration:**
- `.env.example` = SQLite
- `settings.py` = Optimized for mini project
- `database.py` = SQLite-compatible

---

## Summary

| Step | Action |
|------|--------|
| 1 | Go to Render dashboard |
| 2 | Select your service |
| 3 | Update DATABASE_URL to `sqlite:////tmp/app.db` |
| 4 | Deploy |
| 5 | Done! |

Your app will now use SQLite and won't hit Neon quota limits anymore.

