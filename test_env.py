#!/usr/bin/env python3
"""
Test script to verify .env file is being read correctly
Run this before starting the main app to debug environment variable issues
"""

import os
from dotenv import load_dotenv

print("="*60)
print("Testing .env file loading...")
print("="*60)

# Load environment variables
load_dotenv()

# Check all possible variable names
possible_vars = {
    'B2_APPLICATION_KEY_ID': 'Application Key ID',
    'B2_KEY_ID': 'Key ID (alternative)',
    'B2_ACCESS_KEY_ID': 'Access Key ID (alternative)',
    'B2_APPLICATION_KEY': 'Application Key',
    'B2_SECRET_KEY': 'Secret Key (alternative)',
    'B2_APPLICATION_SECRET': 'Application Secret (alternative)',
    'B2_ENDPOINT_URL': 'Endpoint URL',
    'B2_BUCKET_NAME': 'Bucket Name',
}

print("\nChecking environment variables:")
print("-" * 60)

found_vars = {}
for var_name, description in possible_vars.items():
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if 'KEY' in var_name:
            if len(value) > 10:
                masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
            else:
                masked = '*' * len(value)
            print(f"✓ {var_name:30} = {masked:50} (length: {len(value)})")
        else:
            print(f"✓ {var_name:30} = {value}")
        found_vars[var_name] = value
    else:
        print(f"✗ {var_name:30} = NOT SET")

print("-" * 60)

# Determine which variables will be used
print("\nVariables that will be used:")
print("-" * 60)

key_id = found_vars.get('B2_APPLICATION_KEY_ID') or found_vars.get('B2_KEY_ID') or found_vars.get('B2_ACCESS_KEY_ID')
secret_key = found_vars.get('B2_APPLICATION_KEY') or found_vars.get('B2_SECRET_KEY') or found_vars.get('B2_APPLICATION_SECRET')
endpoint = found_vars.get('B2_ENDPOINT_URL', '')
bucket = found_vars.get('B2_BUCKET_NAME', 'mybucket')

if key_id:
    print(f"✓ Application Key ID: {key_id[:5]}...{key_id[-5:]} (length: {len(key_id)})")
    if len(key_id) < 20:
        print(f"  ⚠️  WARNING: Key ID seems too short! Expected ~25 characters")
else:
    print("✗ Application Key ID: NOT FOUND")

if secret_key:
    masked = secret_key[:5] + '*' * (len(secret_key) - 10) + secret_key[-5:] if len(secret_key) > 10 else '*' * len(secret_key)
    print(f"✓ Application Key: {masked} (length: {len(secret_key)})")
    if len(secret_key) < 20:
        print(f"  ⚠️  WARNING: Secret key seems too short! Expected ~40+ characters")
else:
    print("✗ Application Key: NOT FOUND")

if endpoint:
    if not endpoint.startswith(('http://', 'https://')):
        endpoint = f'https://{endpoint}'
    print(f"✓ Endpoint URL: {endpoint}")
else:
    print("✗ Endpoint URL: NOT FOUND")

print(f"✓ Bucket Name: {bucket}")

print("-" * 60)

# Validation
print("\nValidation:")
print("-" * 60)

errors = []
if not key_id:
    errors.append("❌ B2_APPLICATION_KEY_ID is missing")
    print("❌ B2_APPLICATION_KEY_ID is missing")
else:
    print("✓ B2_APPLICATION_KEY_ID is set")

if not secret_key:
    errors.append("❌ B2_APPLICATION_KEY is missing")
    print("❌ B2_APPLICATION_KEY is missing")
else:
    print("✓ B2_APPLICATION_KEY is set")

if not endpoint:
    errors.append("❌ B2_ENDPOINT_URL is missing")
    print("❌ B2_ENDPOINT_URL is missing")
else:
    print("✓ B2_ENDPOINT_URL is set")

print("-" * 60)

if errors:
    print("\n❌ ERRORS FOUND! Please fix your .env file.")
    print("\nYour .env file should contain:")
    print("B2_APPLICATION_KEY_ID=your_key_id_here")
    print("B2_APPLICATION_KEY=your_secret_key_here")
    print("B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com")
    print("B2_BUCKET_NAME=your_bucket_name")
    print("\nMake sure:")
    print("  - No quotes around values")
    print("  - No extra spaces")
    print("  - Variable names match exactly (case-sensitive)")
else:
    print("\n✓ All required variables are set!")
    print("\nYou can now run: python app.py")

print("="*60)




