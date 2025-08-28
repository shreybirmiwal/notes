# Deployment Guide for Notes App

This React TypeScript application can be deployed to various platforms. Here are the recommended deployment options:

## 🚀 Quick Deploy Options

### 1. Vercel (Recommended)
- **Pros**: Fast, automatic deployments, great for React apps
- **Steps**:
  1. Install Vercel CLI: `npm i -g vercel`
  2. Run: `vercel` in the project directory
  3. Set environment variables in Vercel dashboard:
     - `REACT_APP_SUPABASE_URL`
     - `REACT_APP_SUPABASE_ANON_KEY`

### 2. Netlify
- **Pros**: Free tier, easy setup
- **Steps**:
  1. Connect your GitHub repository to Netlify
  2. Set build command: `npm run build`
  3. Set publish directory: `build`
  4. Add environment variables in Netlify dashboard

### 3. GitHub Pages
- **Pros**: Free, integrated with GitHub
- **Steps**:
  1. Add `"homepage": "https://yourusername.github.io/notes"` to package.json
  2. Install gh-pages: `npm install --save-dev gh-pages`
  3. Add scripts to package.json:
     ```json
     "predeploy": "npm run build",
     "deploy": "gh-pages -d build"
     ```
  4. Run: `npm run deploy`

## 🔧 Environment Variables

Make sure to set these environment variables in your deployment platform:

```
REACT_APP_SUPABASE_URL=https://pycjkqmdyenoiqlowghj.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## 📦 Build Commands

- **Development**: `npm start`
- **Production Build**: `npm run build`
- **Test**: `npm test`

## 🔒 Security Notes

- Environment variables are properly configured
- Supabase credentials are no longer hardcoded
- `.env.local` is gitignored to prevent credential exposure

## 🐛 Troubleshooting

If you encounter build issues:
1. Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
2. Check environment variables are set correctly
3. Ensure all dependencies are in package.json
