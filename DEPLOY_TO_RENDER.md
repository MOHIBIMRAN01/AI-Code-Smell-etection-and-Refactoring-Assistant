# Deploy to Render with SQLite ✅

## Quick Overview
Your project is now configured to deploy on Render with SQLite database. No more Neon quota issues!

---

## Option 1: Using render.yaml (Easiest) ⭐

The `render.yaml` file in your repo automatically configures everything.

### Steps:
1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click "New Service"
   - Select "Web Service"
   - Connect GitHub repo

3. **Render Detects render.yaml**
   - Render automatically reads `render.yaml`
   - Uses Python 3.11
   - Sets DATABASE_URL to SQLite
   - Installs dependencies from `Backend/requirements.txt`

4. **Add Missing Environment Variables**
   - In Render dashboard, go to "Environment"
   - Add your API keys:
     ```
     GEMINI_API_KEY=your-key-here
     OPENAI_API_KEY=your-key-here (if needed)
     ```

5. **Deploy**
   - Click "Create Service"
   - Wait for build to complete
   - Done! ✅

---

## Option 2: Manual Docker Build

If render.yaml doesn't work or you prefer manual setup:

### Steps:
1. **Build locally first**
   ```bash
   docker build -f Backend/Dockerfile -t code-smell .
   docker run -p 8000:8000 -e DATABASE_URL=sqlite:////tmp/app.db code-smell
   ```

2. **Test it**
   ```bash
   curl http://localhost:8000/
   ```

3. **Push to Docker Hub** (optional)
   ```bash
   docker tag code-smell your-dockerhub-username/code-smell
   docker push your-dockerhub-username/code-smell
   ```

4. **Deploy on Render**
   - New Service → Docker
   - Set Database URL: `sqlite:////tmp/app.db`
   - Deploy

---

## Environment Variables Needed

**Required:**
```
DATABASE_URL=sqlite:////tmp/app.db   # Auto-configured in render.yaml
GEMINI_API_KEY=your-api-key
```

**Optional:**
```
OPENAI_API_KEY=your-key
MODEL_PROVIDER=gemini
BACKEND_PORT=8000
ENVIRONMENT=production
FRONTEND_URL=your-frontend-url
```

---

## Important Notes

### SQLite on Render
- ✅ Database stored in `/tmp/app.db`
- ✅ Works instantly, no setup needed
- ⚠️ Data resets when Render restarts (ephemeral filesystem)
- ✅ Perfect for mini projects

### Data Persistence
For your mini project with low traffic, data resets are not a concern because:
- Analysis results are lightweight
- Users don't rely on persistent history
- Easy to re-run analysis if needed

If you later need persistent data, upgrade to:
- Render PostgreSQL Database
- AWS RDS
- Railway

---

## Troubleshooting

### Build Failed: "Can't find requirements.txt"
**Cause:** Render can't find Backend/requirements.txt
**Fix:** Check `render.yaml` buildCommand path

### Error: "database is locked"
**Cause:** SQLite concurrent access
**Fix:** This shouldn't happen on Render (single process). Restart if it occurs.

### Error: "No such table"
**Cause:** Database hasn't initialized
**Fix:** Restart the service - tables auto-create

### Environment variables not working
**Cause:** Variables not set in Render dashboard
**Fix:** Go to Environment tab, add missing variables

---

## File Changes Made

| File | Change | Purpose |
|------|--------|---------|
| `render.yaml` | ✅ NEW | Automatic Render configuration |
| `Backend/Dockerfile` | ✅ UPDATED | SQLite & Backend path fixes |
| `.dockerignore` | ✅ NEW | Optimize Docker build size |
| `Backend/.env` | ✅ EXISTS | Local SQLite configuration |

---

## Deployment Checklist

- [ ] Code committed and pushed to GitHub
- [ ] `render.yaml` in root directory
- [ ] `Backend/Dockerfile` updated
- [ ] API keys added to Render Environment
- [ ] DATABASE_URL set to SQLite
- [ ] Service created and deployed
- [ ] Frontend URL configured in Render
- [ ] Test API endpoint works

---

## Testing After Deployment

Once deployed on Render:

1. **Check service logs**
   - Render dashboard → Logs
   - Should see no database errors

2. **Test API**
   ```bash
   curl https://your-render-url/api/health
   ```

3. **Test with analysis**
   - Use your frontend
   - Submit a code analysis
   - Should work without database errors

---

## Cost on Render

**Free tier includes:**
- ✅ 750 hours/month (one service running 24/7)
- ✅ 0.5GB RAM
- ✅ SQLite (no extra cost)
- ✅ Sufficient for mini project

**No monthly charges for mini project!**

---

## Next Steps

1. **Push your code**
   ```bash
   git push origin main
   ```

2. **Deploy on Render**
   - Go to render.yaml method above
   - Create service

3. **Monitor and test**
   - Check logs for errors
   - Test API endpoint

4. **Share with users**
   - Frontend deployed separately
   - Backend API running on Render

---

## Summary

Your app is now ready for Render deployment with:
- ✅ SQLite database (no external DB needed)
- ✅ Auto-configuration via render.yaml
- ✅ Docker support built-in
- ✅ Zero database costs
- ✅ Perfect for mini projects

**You're all set! 🚀**

