# 🚀 Deploy to Streamlit Community Cloud

## Quick Deploy (5 minutes)

### Prerequisites
- A GitHub account
- This repository pushed to GitHub

### Deployment Steps

1. **Push this repository to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud configuration"
   git push origin main
   ```

2. **Go to Streamlit Community Cloud**
   - Visit: https://share.streamlit.io/
   - Click "Sign in" with your GitHub account
   - Authorize Streamlit to access your repositories

3. **Deploy Your App**
   - Click "New app" button
   - Select:
     - **Repository**: `Srijan-Baniyal/Personal-Risk-Radar`
     - **Branch**: `main`
     - **Main file path**: `main.py`
   - Click "Deploy!"

4. **Wait for Deployment**
   - Initial deployment takes 2-5 minutes
   - Streamlit will install dependencies and start your app
   - Once complete, you'll get a public URL like:
     `https://[your-app-name].streamlit.app/`

## Your App Will Be Live At

After deployment, your app will be accessible at a public URL:
- **Format**: `https://personal-risk-radar-[hash].streamlit.app/`
- **Custom domain**: You can set a custom name in the app settings

## Features on Streamlit Cloud

✅ **Free hosting** for public repositories  
✅ **Automatic redeployment** when you push to GitHub  
✅ **HTTPS enabled** by default  
✅ **Resource monitoring** in the dashboard  
✅ **Easy sharing** with a public URL  

## Monitoring Your App

- **App Dashboard**: https://share.streamlit.io/
- View logs, resource usage, and visitor analytics
- Restart or stop your app anytime
- Update settings and environment variables

## Important Notes

1. **Database Persistence**: The app uses SQLite, which will reset on redeployment. For production, consider using:
   - Streamlit's built-in file storage (limited)
   - External database (PostgreSQL, MySQL)
   - Cloud storage solutions

2. **Resource Limits**: Free tier includes:
   - 1 GB RAM
   - Limited CPU
   - Community support

3. **Custom Domain**: Available on Team/Enterprise plans

## Troubleshooting

If deployment fails:
- Check the logs in the Streamlit Cloud dashboard
- Ensure all dependencies are in `requirements.txt` or `pyproject.toml`
- Verify `main.py` is in the root directory
- Check that there are no syntax errors

## Alternative: Using Docker

If you prefer containerized deployment, use the Docker image:
```bash
docker run -d -p 8501:8501 ghcr.io/srijan-baniyal/personal-risk-radar:latest
```

## Support

- **Streamlit Docs**: https://docs.streamlit.io/
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: https://github.com/Srijan-Baniyal/Personal-Risk-Radar/issues
