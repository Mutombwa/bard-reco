# Deployment Environment Variables

## Required Environment Variables

Both Render and Vercel deployments need these Supabase credentials:

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase API key (anon/public key)

## How to Add in Render Dashboard:
1. Go to https://dashboard.render.com
2. Select your `bard-reco` service
3. Go to **Environment** tab
4. Add the environment variables (already configured)

## How to Add in Vercel Dashboard:
1. Go to your Vercel project settings
2. Navigate to **Settings** → **Environment Variables**
3. Add:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
4. Redeploy for changes to take effect

## Note:
- The app works with or without Supabase (falls back to local file storage)
- Supabase enables persistent authentication across deployments
- Without Supabase, authentication uses temporary local storage
