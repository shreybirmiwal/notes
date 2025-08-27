import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://pycjkqmdyenoiqlowghj.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5Y2prcW1keWVub2lxbG93Z2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzMzAwMTUsImV4cCI6MjA3MTkwNjAxNX0.Ra1eQjm_Fkh_JzcZW2kpuqgmRM7KCHEy8alDFP1_oek';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
