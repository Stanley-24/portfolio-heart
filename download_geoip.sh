#!/bin/bash
# Script to download GeoLite2-City.mmdb and print the env variable
# 
# SETUP INSTRUCTIONS:
# 1. Get your free MaxMind license key from: https://www.maxmind.com/en/geolite2/signup
# 2. Set the environment variable: export MAXMIND_LICENSE_KEY=your_license_key_here
# 3. Run this script: bash download_geoip.sh

set -e

# Get license key from environment variable
LICENSE_KEY="${MAXMIND_LICENSE_KEY}"
if [ -z "$LICENSE_KEY" ]; then
    echo "❌ Error: MAXMIND_LICENSE_KEY environment variable is not set"
    echo ""
    echo "📋 SETUP INSTRUCTIONS:"
    echo "1. Get your free MaxMind license key from: https://www.maxmind.com/en/geolite2/signup"
    echo "2. Set the environment variable:"
    echo "   export MAXMIND_LICENSE_KEY=your_license_key_here"
    echo "3. Run this script again: bash download_geoip.sh"
    echo ""
    echo "🔧 For production (Render/Heroku/etc):"
    echo "   Add MAXMIND_LICENSE_KEY to your environment variables"
    exit 1
fi

GEOIP_DIR="$(pwd)/GeoIP"
MMDB_PATH="$GEOIP_DIR/GeoLite2-City.mmdb"

mkdir -p "$GEOIP_DIR"
echo "📥 Downloading GeoLite2-City.mmdb to $MMDB_PATH ..."

# Download and extract - macOS compatible approach
curl -L "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=$LICENSE_KEY&suffix=tar.gz" \
  | tar -xz -C "$GEOIP_DIR" --strip-components=1

# Find and move the mmdb file
find "$GEOIP_DIR" -name "GeoLite2-City.mmdb" -exec mv {} "$MMDB_PATH" \;

echo ""
echo "✅ Download complete!"
echo ""
echo "📝 Add this line to your .env file:"
echo "GEOIP_DATABASE_PATH=$MMDB_PATH"
echo ""
echo "🌐 For production, set these environment variables:"
echo "   GEOIP_DATABASE_PATH=$MMDB_PATH"
echo "   MAXMIND_LICENSE_KEY=$LICENSE_KEY" 