# Deployment Guide

## Environment Variables Configuration

### Required Environment Variables for Production

When deploying to Render (or any production environment), make sure to set the following environment variables:

#### Core Settings
```
FRONTEND_URL=https://your-frontend-domain.com
ENVIRONMENT=production
```

#### API Keys (at least one provider required)
```
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

#### Model Configuration
```
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
```

#### Database (if using external PostgreSQL)
```
DATABASE_URL=postgresql://username:password@hostname/dbname?sslmode=require
```

#### Optional Settings
```
REPO_CLONE_TTL_MINUTES=30
REPO_CLEANUP_INTERVAL_SECONDS=60
MAX_FILES_TO_ANALYZE=200
REQUEST_TIMEOUT_SECONDS=120
```

---

## Setting Environment Variables in Render

1. Go to your Render dashboard
2. Select your web service
3. Navigate to **Environment** tab
4. Click **Add Environment Variable**
5. Add each variable from the list above

### Critical for CORS to Work:

**You MUST set `FRONTEND_URL`** to your frontend's production URL:

```
FRONTEND_URL=https://your-frontend-app.vercel.app
```

or

```
FRONTEND_URL=https://your-frontend-app.netlify.app
```

### Example for Render Deployment:

If your frontend is hosted at `https://code-smell-detector.vercel.app`, set:

```
FRONTEND_URL=https://code-smell-detector.vercel.app
ENVIRONMENT=production
OPENAI_API_KEY=sk-proj-...your-key...
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
```

---

## CORS Configuration

The backend automatically configures CORS based on the `FRONTEND_URL` environment variable:

- **Development** (`ENVIRONMENT=development`): Allows all origins (*)
- **Production** (`ENVIRONMENT=production`): Only allows:
  - `http://localhost:3000` (for local testing)
  - `http://127.0.0.1:3000` (for local testing)
  - The URL specified in `FRONTEND_URL` (your production frontend)

---

## Verifying Deployment

After setting environment variables and deploying:

1. Check the logs for startup messages
2. Verify no CORS errors in browser console
3. Test API health endpoint: `GET https://your-backend.onrender.com/api/health`
4. Test from frontend to ensure cross-origin requests work

---

## Troubleshooting

### CORS 400 Bad Request on OPTIONS

**Cause**: `FRONTEND_URL` not set or doesn't match your frontend domain

**Solution**: 
1. Set `FRONTEND_URL` in Render environment variables
2. Ensure the URL matches exactly (including https://)
3. Redeploy the service

### Application Won't Start

**Cause**: Missing required environment variables (API keys)

**Solution**: 
1. Set at least one AI provider API key (OPENAI_API_KEY or GEMINI_API_KEY)
2. Check logs for specific error messages
3. Verify DATABASE_URL format if using external PostgreSQL

### Git-Related Errors

**Cause**: Git not installed in container

**Solution**: Already fixed in Dockerfile - git is now installed during build

---

## Local Development

For local development, copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env` with your local settings:

```
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
OPENAI_API_KEY=your-key-here
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
```
