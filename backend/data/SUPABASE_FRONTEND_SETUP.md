# Supabase Authentication Setup

## Frontend Integration

Use `@supabase/supabase-js` in your frontend:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://your-project-ref.supabase.co',
  'your-anon-key'
)

// Sign in with Google
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'http://localhost:5173/auth/callback'
  }
})

// Get session
const { data: { session } } = await supabase.auth.getSession()

// Use session token in API calls
fetch('http://localhost:3001/api/generate-plan', {
  headers: {
    'Authorization': `Bearer ${session.access_token}`
  }
})
```

## API Endpoints

### Public Endpoints
- `POST /api/auth/google` - Authenticate with Google ID token
- `GET /api/health` - Health check

### Protected Endpoints (require Bearer token)
- `GET /api/auth/user` - Get current user
- `POST /api/auth/signout` - Sign out
- `POST /api/generate-plan` - Generate financial plan
- `POST /api/refine-plan` - Refine plan with chat
