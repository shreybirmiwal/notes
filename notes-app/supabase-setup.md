# Supabase Setup Guide

## Fix for "Bucket not found" Error

You need to create the storage bucket in your Supabase dashboard. Follow these steps:

### 1. Create Storage Bucket

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `pycjkqmdyenoiqlowghj`
3. Click on **Storage** in the left sidebar
4. Click **"Create a new bucket"** button
5. Fill in the details:
   - **Name**: `notes` (exactly this name)
   - **Public bucket**: ✅ Check this box
   - **File size limit**: Leave default (50MB)
6. Click **"Create bucket"**

### 2. Create Database Table

1. Click on **SQL Editor** in the left sidebar
2. Click **"New query"**
3. Paste and run this SQL:

```sql
-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
  id SERIAL PRIMARY KEY,
  class_id TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  tags TEXT,
  file_path TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create todos table
CREATE TABLE IF NOT EXISTS todos (
  id SERIAL PRIMARY KEY,
  class_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  due_date DATE,
  priority TEXT CHECK (priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE todos ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations
CREATE POLICY "Allow all operations on notes" ON notes FOR ALL USING (true);
CREATE POLICY "Allow all operations on todos" ON todos FOR ALL USING (true);
```

4. Click **"Run"** to execute the query

### 3. Set Storage Policies

1. Go back to **Storage** → **Policies**
2. Click on the `notes` bucket
3. Click **"New Policy"**
4. Add these policies one by one:

**Policy 1 - Allow public read access:**
- Policy name: `Allow public read access`
- Allowed operation: `SELECT`
- Policy definition: `bucket_id = 'notes'`

**Policy 2 - Allow public uploads:**
- Policy name: `Allow public uploads`
- Allowed operation: `INSERT`
- Policy definition: `bucket_id = 'notes'`

### 4. Test the Setup

After completing the above steps:
1. Refresh your app
2. Try uploading a PDF file
3. It should work without the "Bucket not found" error

## Troubleshooting

If you still get errors:
1. Make sure the bucket name is exactly `notes` (lowercase)
2. Make sure the bucket is marked as "Public"
3. Check that the storage policies are applied
4. Try refreshing the page after setup
