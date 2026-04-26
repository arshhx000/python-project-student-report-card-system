# 🚀 Vercel Deployment Guide

## Project Structure

```
your-project/
├── api/
│   └── index.py           ← Flask app (from app.py)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── teacher_dashboard.html
│   ├── student_dashboard.html
│   ├── welcome.html       ← New welcome page
│   ├── add_student.html
│   ├── manage_marks.html
│   ├── grades.html
│   ├── report_card.html
│   ├── attendance.html
│   ├── remarks.html
│   ├── class_topper.html
│   ├── fail_list.html
│   └── search_student.html
├── database.py            ← Database functions
├── requirements.txt       ← Python dependencies
├── vercel.json           ← Vercel configuration ✅
├── .vercelignore         ← Deployment ignore rules ✅
├── .gitignore           ← Git ignore rules ✅
├── README.md            ← Project documentation
└── mainnn.html          ← Old welcome (can be deleted)
```

## What Changed

### 1. **Moved `app.py` → `api/index.py`** ✅
   - Vercel serverless functions require Flask app in `api/index.py`
   - Updated template folder path: `template_folder='../templates'`
   - Added path handling for imports

### 2. **Updated `vercel.json`** ✅
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api/index.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "api/index.py"
       }
     ]
   }
   ```

### 3. **Created `welcome.html`** ✅
   - Better landing page with updated features
   - Located in `templates/welcome.html`
   - Link to login page

### 4. **Added `.vercelignore`** ✅
   - Excludes unnecessary files from deployment
   - Reduces deployment size

### 5. **Added `.gitignore`** ✅
   - Prevents committing database and cache files
   - Follows Python best practices

## Deployment Steps

### On Local Machine

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test locally (with old structure):**
   ```bash
   python app.py
   ```
   Access at `http://localhost:5001`

### On Vercel

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Restructure for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to https://vercel.com/new
   - Select your GitHub repository
   - Click "Deploy"
   - Vercel automatically reads `vercel.json`

3. **Vercel will:**
   - Build using `api/index.py`
   - Serve templates from `templates/` folder
   - Set environment variables
   - Deploy automatically

## Important Notes

### Database Handling
- SQLite database (`database.db`) is created on first run
- On serverless (Vercel), database needs persistent storage
- **Solution**: Use environment variable to store in `/tmp` or use cloud database

### Session Storage
- Flask sessions are stored in-memory by default
- On serverless, this may lose session data between requests
- **Solution**: Implement session persistence (Redis, database, etc.)

### File Paths
- `api/index.py` uses `template_folder='../templates'`
- All imports work correctly with path handling

## Testing Before Deployment

1. **Verify the structure:**
   ```bash
   ls api/          # Should show: index.py
   ls templates/    # Should show all .html files
   cat vercel.json  # Should show correct routes
   ```

2. **Check for errors:**
   - Open `api/index.py`
   - Check for any import errors
   - Verify database.py is importable

3. **Test locally with Vercel CLI:**
   ```bash
   npm i -g vercel
   vercel dev
   ```

## Environment Variables (Optional)

Create `.env.local` for local testing:
```
FLASK_ENV=development
DATABASE_URL=sqlite:///./database.db
```

In Vercel dashboard, add Environment Variables:
- Settings → Environment Variables
- Add any production-specific variables

## Troubleshooting

### "Module not found: database"
- Ensure `sys.path.insert(0, os.path.dirname(...))` is at top of `api/index.py`
- Check that `database.py` is in project root

### "Templates not found"
- Verify Flask app: `Flask(__name__, template_folder='../templates')`
- Check templates are in `templates/` folder

### Database not persisting
- Vercel doesn't support persistent file storage
- Consider migrating to:
  - PostgreSQL on Vercel
  - MongoDB Atlas
  - AWS RDS

## Next Steps

1. ✅ Project structure reorganized
2. ✅ vercel.json configured
3. ⏳ Test locally: `vercel dev`
4. ⏳ Deploy to Vercel
5. ⏳ Test production deployment
6. ⏳ Set up database backup strategy

---

**Ready to Deploy!** Your project is now structured for Vercel serverless deployment. 🚀
