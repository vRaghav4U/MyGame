# Deploy Flask App to Vercel

## Step-by-Step Guide

### 1. Prepare Your Files
- Add `vercel.json` configuration file
- Add `api/index.py` for serverless deployment
- Ensure `requirements.txt` is present

### 2. GitHub Setup
1. Create a new repository on GitHub
2. Upload all your project files including:
   - All Python files (app.py, main.py, models.py)
   - routes/ folder
   - services/ folder
   - static/ folder (with images)
   - templates/ folder
   - game.html
   - requirements.txt
   - vercel.json
   - api/index.py

### 3. Vercel Deployment
1. Go to https://vercel.com
2. Sign up with your GitHub account
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will auto-detect it's a Python project
6. Configure environment variables:
   - `SESSION_SECRET` = any random string (e.g., "your-secret-key-123")
   - `DATABASE_URL` = your PostgreSQL connection string

### 4. Database Options for Vercel
Since Vercel doesn't provide PostgreSQL, you can use:
- **Supabase** (free PostgreSQL): https://supabase.com
- **PlanetScale** (free MySQL): https://planetscale.com
- **Neon** (free PostgreSQL): https://neon.tech

### 5. Get Database URL
For Supabase (recommended):
1. Create account at supabase.com
2. Create new project
3. Go to Settings > Database
4. Copy connection string (starts with postgresql://)
5. Add as DATABASE_URL environment variable in Vercel

### 6. Deploy
- Click "Deploy" in Vercel
- Your app will be live at: `https://your-app.vercel.app`
- Game URL: `https://your-app.vercel.app/game`

### 7. Custom Domain (Optional)
1. Buy domain from any registrar
2. Add domain in Vercel project settings
3. Update DNS records as instructed
4. SSL certificate added automatically

## Important Notes
- Vercel uses serverless functions, so database connections are stateless
- Static files (images, CSS, JS) are served automatically
- Your Raghav image will be available at the same URL structure

## Troubleshooting
- If deployment fails, check the build logs in Vercel dashboard
- Make sure all file paths are correct and case-sensitive
- Verify environment variables are set correctly