import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://icltghculjdburjhvkwy.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImljbHRnaGN1bGpkYnVyamh2a3d5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2NjEwMjksImV4cCI6MjA4NDIzNzAyOX0.lNafi4ZUdZoJrkTBioybWbOpQ63-4oTPXDYlgjo8Hd0'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// API base URL
export const API_BASE_URL = 'http://localhost:8000'
