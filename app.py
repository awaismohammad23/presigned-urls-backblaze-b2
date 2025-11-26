from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Debug: Print all B2-related environment variables (for troubleshooting)
print("\n" + "="*60)
print("DEBUG: Checking environment variables...")
print("="*60)
for key, value in os.environ.items():
    if key.startswith('B2_'):
        # Mask sensitive values but show length
        if 'KEY' in key and value:
            masked = value[:5] + '*' * (len(value) - 10) + value[-5:] if len(value) > 10 else '*' * len(value)
            print(f"  {key} = {masked} (length: {len(value)})")
        else:
            print(f"  {key} = {value}")
print("="*60 + "\n")

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize B2 S3 client
session = boto3.session.Session()

# Get and validate environment variables (strip whitespace)
def get_env(key, default=None):
    """Get environment variable and strip whitespace"""
    value = os.getenv(key, default)
    if value is None:
        return default
    # Strip whitespace and remove quotes if present
    value = value.strip().strip('"').strip("'")
    return value if value else default

# Get endpoint URL and ensure it has https:// prefix
endpoint_url = get_env('B2_ENDPOINT_URL', '')
if endpoint_url and not endpoint_url.startswith(('http://', 'https://')):
    endpoint_url = f'https://{endpoint_url}'

# Get credentials and validate they exist
# Try multiple possible variable names for flexibility
aws_access_key_id = get_env('B2_APPLICATION_KEY_ID') or get_env('B2_KEY_ID') or get_env('B2_ACCESS_KEY_ID')
aws_secret_access_key = get_env('B2_APPLICATION_KEY') or get_env('B2_SECRET_KEY') or get_env('B2_APPLICATION_SECRET')
bucket_name = get_env('B2_BUCKET_NAME', 'mybucket')

# Validate required credentials
if not aws_access_key_id:
    raise ValueError("B2_APPLICATION_KEY_ID is required in .env file. Check that the variable name matches exactly.")
if not aws_secret_access_key:
    raise ValueError("B2_APPLICATION_KEY is required in .env file. Check that the variable name matches exactly.")
if not endpoint_url:
    raise ValueError("B2_ENDPOINT_URL is required in .env file. Check that the variable name matches exactly.")

# Validate key formats (Backblaze B2 keys have specific formats)
if aws_access_key_id:
    if len(aws_access_key_id) < 20:
        print(f"\n{'='*70}")
        print(f"⚠️  CRITICAL WARNING: B2_APPLICATION_KEY_ID is too short ({len(aws_access_key_id)} chars).")
        print(f"{'='*70}")
        print(f"   Current value: {aws_access_key_id}")
        print(f"   This appears to be an OLD or INCOMPLETE key.")
        print(f"\n   For S3-compatible API, you need a regular 'Application Key' that:")
        print(f"   - Is approximately 20-25 characters long")
        print(f"   - Example: 0050428f1a906270000000001 (25 chars)")
        print(f"\n   IMPORTANT: Make sure you've updated your .env file with the NEW keyID!")
        print(f"   Your new key should have:")
        print(f"   - keyID: 0050428f1a906270000000001 (or similar, ~25 chars)")
        print(f"   - applicationKey: K005rH1B5kjFA6QgKtyAbzl1F80qMeY (starts with 'K')")
        print(f"\n   Update your .env file:")
        print(f"   B2_APPLICATION_KEY_ID=0050428f1a906270000000001")
        print(f"   B2_APPLICATION_KEY=K005rH1B5kjFA6QgKtyAbzl1F80qMeY")
        print(f"{'='*70}\n")
    elif len(aws_access_key_id) >= 20:
        print(f"✓ B2_APPLICATION_KEY_ID looks correct: {aws_access_key_id[:10]}... (length: {len(aws_access_key_id)})")
if aws_secret_access_key and len(aws_secret_access_key) < 20:
    print(f"⚠️  Warning: B2_APPLICATION_KEY seems too short ({len(aws_secret_access_key)} chars). Expected ~40+ characters.")

# Debug: Print first few characters of keys (for verification, not full keys)
print(f"✓ Loaded B2_APPLICATION_KEY_ID: {aws_access_key_id[:10]}... (length: {len(aws_access_key_id)})" if aws_access_key_id else "✗ B2_APPLICATION_KEY_ID not found")
print(f"✓ Loaded B2_APPLICATION_KEY: {'*' * min(len(aws_secret_access_key), 20)}... (length: {len(aws_secret_access_key)})" if aws_secret_access_key else "✗ B2_APPLICATION_KEY not found")
print(f"✓ Loaded B2_ENDPOINT_URL: {endpoint_url}")
print(f"✓ Loaded B2_BUCKET_NAME: {bucket_name}")

s3_client = session.client(
    service_name='s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url
)

BUCKET_NAME = bucket_name


def generate_presigned_download_url(bucket_name, file_name, expiration=3600):
    """Generate a pre-signed URL for downloading a file"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        raise Exception(f"Error generating download URL: {str(e)}")


def generate_presigned_upload_url(bucket_name, file_name, expiration=3600):
    """Generate a pre-signed URL for uploading a file"""
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        raise Exception(f"Error generating upload URL: {str(e)}")


@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('static', 'index.html')


@app.route('/styles.css')
def styles():
    """Serve CSS file"""
    return send_from_directory('static', 'styles.css')


@app.route('/script.js')
def script():
    """Serve JavaScript file"""
    return send_from_directory('static', 'script.js')


@app.route('/api/generate-download-url', methods=['POST'])
def generate_download_url():
    """Generate a pre-signed URL for downloading a file"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        expiration = data.get('expiration', 3600)  # Default 1 hour
        
        if not file_name:
            return jsonify({'error': 'file_name is required'}), 400
        
        url = generate_presigned_download_url(BUCKET_NAME, file_name, expiration)
        
        return jsonify({
            'success': True,
            'url': url,
            'file_name': file_name,
            'expiration_seconds': expiration,
            'expires_at': datetime.now().timestamp() + expiration
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-upload-url', methods=['POST'])
def generate_upload_url():
    """Generate a pre-signed URL for uploading a file"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        expiration = data.get('expiration', 3600)  # Default 1 hour
        
        if not file_name:
            return jsonify({'error': 'file_name is required'}), 400
        
        url = generate_presigned_upload_url(BUCKET_NAME, file_name, expiration)
        
        return jsonify({
            'success': True,
            'url': url,
            'file_name': file_name,
            'expiration_seconds': expiration,
            'expires_at': datetime.now().timestamp() + expiration
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/list-files', methods=['GET'])
def list_files():
    """List files in the bucket"""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        return jsonify({
            'success': True,
            'files': files
        })
    except Exception as e:
        error_details = {
            'error': str(e),
            'error_type': type(e).__name__,
            'debug_info': {
                'key_id_length': len(aws_access_key_id) if aws_access_key_id else 0,
                'key_id_preview': aws_access_key_id[:5] + '...' + aws_access_key_id[-5:] if aws_access_key_id and len(aws_access_key_id) > 10 else 'N/A',
                'endpoint': endpoint_url,
                'bucket': BUCKET_NAME
            }
        }
        print(f"\n❌ Error in list_files: {error_details}\n")
        return jsonify(error_details), 500


@app.route('/api/check-config', methods=['GET'])
def check_config():
    """Check configuration status (for debugging)"""
    config_status = {
        'B2_APPLICATION_KEY_ID': '✓ Set' if aws_access_key_id else '✗ Missing',
        'B2_APPLICATION_KEY': '✓ Set' if aws_secret_access_key else '✗ Missing',
        'B2_ENDPOINT_URL': endpoint_url if endpoint_url else '✗ Missing',
        'B2_BUCKET_NAME': bucket_name if bucket_name else '✗ Missing',
        'key_id_length': len(aws_access_key_id) if aws_access_key_id else 0,
        'key_length': len(aws_secret_access_key) if aws_secret_access_key else 0,
        'key_id_preview': aws_access_key_id[:10] + '...' if aws_access_key_id else 'Not set',
        'endpoint_preview': endpoint_url if endpoint_url else 'Not set',
    }
    
    # Try to test the connection
    try:
        # Simple test: try to list buckets or head bucket
        s3_client.head_bucket(Bucket=bucket_name)
        config_status['connection_test'] = '✓ Success'
    except Exception as e:
        config_status['connection_test'] = f'✗ Failed: {str(e)}'
        config_status['error_details'] = {
            'error_type': type(e).__name__,
            'error_message': str(e)
        }
    
    return jsonify(config_status)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, port=port)

