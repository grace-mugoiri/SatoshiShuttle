# 🚀 Quick Deployment Guide

## Deploy to Render.com (Recommended - 5 Minutes)

### Step 1: Prepare Your Code
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit - SatoshiShuttle rideshare app"
```

### Step 2: Push to GitHub
```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/SatoshiShuttle.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to https://render.com and sign up
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and deploy both services
5. Your app will be live at: `https://satoshishuttle-frontend.onrender.com`

**That's it!** Your app is now live on the internet! 🎉

---

## Alternative: Deploy to Railway.app

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway
1. Go to https://railway.app and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect and deploy
5. Add environment variables in Railway dashboard:
   - `SECRET_KEY`: Generate a random string
   - `JWT_SECRET`: Generate another random string

---

## Alternative: Deploy Frontend to Vercel + Backend to Railway

### Frontend (Vercel):
```bash
cd frontend
npm install -g vercel
vercel --prod
```

### Backend (Railway):
Same as above, but only deploy the backend.

---

## Environment Variables Needed

For production, set these in your hosting dashboard:

```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
DATABASE_URL=postgresql://... (optional, SQLite works fine for testing)
FLASK_ENV=production
```

---

## Testing Your Deployment

1. Visit your deployed frontend URL
2. Register a new account
3. Create a ride
4. Book a ride with Bitcoin
5. Test the payment QR code

---

## Costs

- **Render.com Free Tier**: Free for both frontend and backend
- **Railway.app**: $5/month credit (enough for small apps)
- **Vercel**: Free for frontend

**Total Cost: $0** for testing and small-scale use!

---

## Need Help?

Check the full `deployment_guide.md` for detailed instructions and troubleshooting.
