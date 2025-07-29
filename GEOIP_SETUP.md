# GeoIP Database Setup Guide

This guide explains how to set up the GeoIP database for geographic analytics.

## 🚀 Quick Setup

### 1. Get MaxMind License Key
1. Go to [MaxMind GeoLite2 Sign Up](https://www.maxmind.com/en/geolite2/signup)
2. Create a free account
3. Get your license key from your account dashboard

### 2. Local Development
```bash
# Set your license key
export MAXMIND_LICENSE_KEY=your_license_key_here

# Download the database
bash download_geoip.sh

# Add to your .env file
echo "GEOIP_DATABASE_PATH=/path/to/your/project/GeoIP/GeoLite2-City.mmdb" >> .env
```

### 3. Production (Render/Heroku/etc)
Add these environment variables to your production platform:

```
MAXMIND_LICENSE_KEY=your_license_key_here
GEOIP_DATABASE_PATH=/opt/render/project/src/GeoIP/GeoLite2-City.mmdb
```

## 📁 File Structure
```
backend/
├── GeoIP/                    # Created by download script
│   └── GeoLite2-City.mmdb   # GeoIP database file
├── download_geoip.sh         # Download script
└── .env                      # Environment variables
```

## 🔧 How It Works
- The `download_geoip.sh` script downloads the latest GeoIP database
- Your backend uses this database to resolve IP addresses to countries/cities
- Geographic analytics show visitor locations in your admin dashboard

## 🛡️ Security Notes
- Never commit your MaxMind license key to version control
- The license key is stored in environment variables only
- The GeoIP database file is excluded from git (too large) 