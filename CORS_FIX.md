# CORS Configuration Fix

## 🎯 Problem

Backend was not working for model training and prediction when deployed on Railway and accessed from Streamlit Cloud.

**Root Cause**: Incorrect CORS configuration using wildcard patterns in `allow_origins`.

---

## ❌ What Was Wrong

### Previous Configuration (INCORRECT):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.streamlit.app",      # ❌ DOESN'T WORK!
        "https://*.streamlitapp.com",   # ❌ DOESN'T WORK!
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Why It Didn't Work:

FastAPI's `allow_origins` parameter **does NOT support wildcards** like `*`.

When you write `"https://*.streamlit.app"`, FastAPI treats it as an **exact string match**, not a pattern. So it only allows requests from a domain literally named `"https://*.streamlit.app"`, which doesn't exist.

**Result**: All requests from Streamlit Cloud (e.g., `https://your-app.streamlit.app`) were **blocked by CORS**.

---

## ✅ Solution

### New Configuration (CORRECT):

```python
# Configure CORS for production and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",      # Local development
        "http://127.0.0.1:8501",      # Local development
    ],
    allow_origin_regex=r"https://.*\.streamlit\.app|https://.*\.streamlitapp\.com",  # Streamlit Cloud
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### What Changed:

1. **Removed wildcard patterns** from `allow_origins`
2. **Added `allow_origin_regex`** parameter with regex pattern
3. **Kept localhost** in `allow_origins` for local development

### How It Works:

**`allow_origins`**: Exact string matching
- `"http://localhost:8501"` → Matches exactly `http://localhost:8501`
- `"http://127.0.0.1:8501"` → Matches exactly `http://127.0.0.1:8501`

**`allow_origin_regex`**: Regular expression matching
- `r"https://.*\.streamlit\.app"` → Matches any subdomain of `streamlit.app`
  - ✅ `https://your-app.streamlit.app`
  - ✅ `https://my-hospital-app.streamlit.app`
  - ✅ `https://test-123.streamlit.app`
- `r"https://.*\.streamlitapp\.com"` → Matches any subdomain of `streamlitapp.com` (old domain)
  - ✅ `https://your-app.streamlitapp.com`

**Combined with `|` (OR operator)**:
- Matches either `.streamlit.app` OR `.streamlitapp.com`

---

## 🔍 Regex Pattern Explanation

### Pattern: `r"https://.*\.streamlit\.app|https://.*\.streamlitapp\.com"`

**Breaking it down:**

```regex
https://          # Literal "https://"
.*                # Any characters (subdomain)
\.                # Literal dot (escaped)
streamlit\.app    # Literal "streamlit.app"
|                 # OR
https://          # Literal "https://"
.*                # Any characters (subdomain)
\.                # Literal dot (escaped)
streamlitapp\.com # Literal "streamlitapp.com"
```

**Examples that match:**
- ✅ `https://my-app.streamlit.app`
- ✅ `https://test-123.streamlit.app`
- ✅ `https://hospital-analytics.streamlit.app`
- ✅ `https://old-app.streamlitapp.com`

**Examples that DON'T match:**
- ❌ `http://my-app.streamlit.app` (http, not https)
- ❌ `https://streamlit.app` (no subdomain)
- ❌ `https://my-app.example.com` (different domain)

---

## 🧪 Testing

### Test Locally:

1. **Start backend**:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start frontend**:
   ```bash
   streamlit run frontend/app.py
   ```

3. **Test prediction**:
   - Go to Patient Risk Analysis
   - Fill in form
   - Click "Predict Risk"
   - Should work ✅

### Test on Deployment:

1. **Deploy backend** to Railway
2. **Deploy frontend** to Streamlit Cloud
3. **Add backend URL** to Streamlit secrets:
   ```toml
   API_URL = "https://your-backend.railway.app"
   ```
4. **Test prediction** on deployed app
5. Should work ✅

---

## 🔧 Alternative Configurations

### Option 1: Allow All Origins (NOT RECOMMENDED for production)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Pros**: Works everywhere
**Cons**: Security risk, can't use credentials

### Option 2: Specific Domains Only

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://my-specific-app.streamlit.app",  # Your specific app
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Pros**: Most secure
**Cons**: Must update for each new deployment

### Option 3: Multiple Regex Patterns (RECOMMENDED)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_origin_regex=r"https://.*\.streamlit\.app|https://.*\.streamlitapp\.com|https://.*\.railway\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Pros**: Flexible, secure, works with multiple platforms
**Cons**: Slightly more complex

---

## 📝 Best Practices

### For Development:

```python
import os

# Determine environment
ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "development":
    # Allow localhost only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production: Allow Streamlit Cloud
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ],
        allow_origin_regex=r"https://.*\.streamlit\.app|https://.*\.streamlitapp\.com",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### For Production:

✅ **DO**:
- Use `allow_origin_regex` for wildcard domains
- Keep `allow_origins` for exact matches (localhost)
- Use HTTPS in production
- Enable `allow_credentials` if needed
- Test CORS configuration before deploying

❌ **DON'T**:
- Use wildcards in `allow_origins` (doesn't work)
- Use `allow_origins=["*"]` in production
- Forget to escape dots in regex (use `\.` not `.`)
- Mix up `allow_origins` and `allow_origin_regex`

---

## 🐛 Troubleshooting

### Issue: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Symptoms**:
- Frontend shows connection errors
- Browser console shows CORS errors
- Backend logs show requests but no response

**Solution**:
1. Check backend CORS configuration
2. Verify `allow_origin_regex` pattern is correct
3. Test regex pattern: https://regex101.com/
4. Restart backend after changes

### Issue: "CORS policy: The value of the 'Access-Control-Allow-Credentials' header"

**Symptoms**:
- CORS error mentioning credentials
- Requests fail even with correct origin

**Solution**:
1. Ensure `allow_credentials=True` in CORS config
2. Don't use `allow_origins=["*"]` with credentials
3. Use specific origins or regex instead

### Issue: Localhost works but deployment doesn't

**Symptoms**:
- Works locally
- Fails on Streamlit Cloud

**Solution**:
1. Check if using `allow_origin_regex` (not `allow_origins` with wildcards)
2. Verify regex pattern matches your Streamlit URL
3. Check backend logs for CORS errors
4. Test with browser dev tools (Network tab)

---

## 🔍 Debugging CORS

### Check Browser Console:

1. Open browser dev tools (F12)
2. Go to Console tab
3. Look for CORS errors:
   ```
   Access to fetch at 'https://backend.railway.app/predict' 
   from origin 'https://your-app.streamlit.app' has been 
   blocked by CORS policy
   ```

### Check Backend Logs:

1. Railway: View logs in dashboard
2. Local: Check terminal output
3. Look for:
   - Request received
   - CORS headers sent
   - Response status

### Test with cURL:

```bash
curl -X POST https://your-backend.railway.app/predict \
  -H "Origin: https://your-app.streamlit.app" \
  -H "Content-Type: application/json" \
  -d '{"age": 65, ...}' \
  -v
```

Look for `Access-Control-Allow-Origin` header in response.

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Updated `backend/main.py` with correct CORS config
- [ ] Removed wildcard patterns from `allow_origins`
- [ ] Added `allow_origin_regex` with proper regex
- [ ] Tested locally (localhost)
- [ ] Committed and pushed changes
- [ ] Deployed backend to Railway
- [ ] Tested on Streamlit Cloud
- [ ] Verified predictions work
- [ ] Verified model training works
- [ ] No CORS errors in browser console

---

## 📚 References

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Regex Testing Tool](https://regex101.com/)

---

## 🎉 Summary

**Problem**: Wildcard patterns in `allow_origins` don't work

**Solution**: Use `allow_origin_regex` with regex pattern

**Before**:
```python
allow_origins=["https://*.streamlit.app"]  # ❌ Doesn't work
```

**After**:
```python
allow_origin_regex=r"https://.*\.streamlit\.app"  # ✅ Works!
```

**Result**: Backend now accepts requests from Streamlit Cloud! 🎉

---

**Your CORS configuration is now fixed and will work on deployment!** 🚀
