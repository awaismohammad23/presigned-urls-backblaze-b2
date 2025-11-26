from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
from botocore.config import Config
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Debug output for env vars
print("\n" + "="*60)
print("Checking environment variables...")
print("="*60)
for key, value in os.environ.items():
    if key.startswith('B2_'):
        if 'KEY' in key and value:
            masked = value[:5] + '*' * (len(value) - 10) + value[-5:] if len(value) > 10 else '*' * len(value)
            print(f"  {key} = {masked} (length: {len(value)})")
        else:
            print(f"  {key} = {value}")
print("="*60 + "\n")

app = Flask(__name__, static_folder='static', static_url_path='')
# Enable CORS for all routes and allow credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Initialize B2 S3 client
session = boto3.session.Session()

# Helper to get env vars and clean them up
def get_env(key, default=None):
    value = os.getenv(key, default)
    if value is None:
        return default
    # strip whitespace and quotes
    value = value.strip().strip('"').strip("'")
    return value if value else default

# Get endpoint and add https if missing
endpoint_url = get_env('B2_ENDPOINT_URL', '')
if endpoint_url and not endpoint_url.startswith(('http://', 'https://')):
    endpoint_url = f'https://{endpoint_url}'

# Extract region from endpoint URL for boto3
# Format: s3.us-east-005.backblazeb2.com -> us-east-005
region_name = 'us-east-005'  # default
if 'us-east-005' in endpoint_url:
    region_name = 'us-east-005'
elif 'us-west-' in endpoint_url:
    # Extract region from URL like s3.us-west-000.backblazeb2.com
    parts = endpoint_url.split('.')
    if len(parts) >= 2:
        region_part = parts[1]  # us-west-000
        region_name = region_part

# Get credentials - try a few different variable name formats
aws_access_key_id = get_env('B2_APPLICATION_KEY_ID') or get_env('B2_KEY_ID') or get_env('B2_ACCESS_KEY_ID')
aws_secret_access_key = get_env('B2_APPLICATION_KEY') or get_env('B2_SECRET_KEY') or get_env('B2_APPLICATION_SECRET')
bucket_name = get_env('B2_BUCKET_NAME', 'mybucket')

# Make sure we have the required credentials
if not aws_access_key_id:
    raise ValueError("B2_APPLICATION_KEY_ID is required in .env file")
if not aws_secret_access_key:
    raise ValueError("B2_APPLICATION_KEY is required in .env file")
if not endpoint_url:
    raise ValueError("B2_ENDPOINT_URL is required in .env file")

# Check key formats
if aws_access_key_id:
    if len(aws_access_key_id) < 20:
        print(f"\n{'='*70}")
        print(f"WARNING: B2_APPLICATION_KEY_ID is too short ({len(aws_access_key_id)} chars)")
        print(f"{'='*70}")
        print(f"Current value: {aws_access_key_id}")
        print(f"This looks like an old or incomplete key.")
        print(f"\nFor S3-compatible API, you need a regular Application Key that:")
        print(f"- Is about 20-25 characters long")
        print(f"- Example: 0050428f1a906270000000001 (25 chars)")
        print(f"\nMake sure you've updated your .env file with the new keyID!")
        print(f"Your new key should have:")
        print(f"- keyID: 0050428f1a906270000000001 (or similar, ~25 chars)")
        print(f"- applicationKey: K005rH1B5kjFA6QgKtyAbzl1F80qMeY (starts with 'K')")
        print(f"\nUpdate your .env file:")
        print(f"B2_APPLICATION_KEY_ID=0050428f1a906270000000001")
        print(f"B2_APPLICATION_KEY=K005rH1B5kjFA6QgKtyAbzl1F80qMeY")
        print(f"{'='*70}\n")
    elif len(aws_access_key_id) >= 20:
        print(f"B2_APPLICATION_KEY_ID looks good: {aws_access_key_id[:10]}... (length: {len(aws_access_key_id)})")
if aws_secret_access_key and len(aws_secret_access_key) < 20:
    print(f"Warning: B2_APPLICATION_KEY seems too short ({len(aws_secret_access_key)} chars). Expected ~40+ characters.")

# Print what we loaded (keys are masked)
if aws_access_key_id:
    print(f"Loaded B2_APPLICATION_KEY_ID: {aws_access_key_id[:10]}...{aws_access_key_id[-5:]} (length: {len(aws_access_key_id)})")
    print(f"  Expected keyID: 0050428f1a906270000000001")
    if aws_access_key_id == '0050428f1a906270000000001':
        print("  KeyID matches! Using correct key.")
    else:
        print("  WARNING: KeyID does NOT match! You may be using a different key.")
else:
    print("B2_APPLICATION_KEY_ID not found")
if aws_secret_access_key:
    print(f"Loaded B2_APPLICATION_KEY: {'*' * min(len(aws_secret_access_key), 20)}... (length: {len(aws_secret_access_key)})")
else:
    print("B2_APPLICATION_KEY not found")
print(f"Loaded B2_ENDPOINT_URL: {endpoint_url}")
print(f"Loaded B2_BUCKET_NAME: {bucket_name}")

# Create S3 client with region and config for proper pre-signed URL generation
s3_config = Config(
    signature_version='s3v4',
    s3={'addressing_style': 'path'}
)

s3_client = session.client(
    service_name='s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    region_name=region_name,
    config=s3_config
)

BUCKET_NAME = bucket_name


def generate_presigned_download_url(bucket_name, file_name, expiration=3600):
    try:
        # For Backblaze B2, we need to use the bucket in the URL path
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        # Backblaze B2 sometimes needs the bucket name in the path
        # If the URL doesn't include the bucket, we might need to adjust it
        return url
    except Exception as e:
        raise Exception(f"Error generating download URL: {str(e)}")


def generate_presigned_upload_url(bucket_name, file_name, expiration=3600):
    try:
        # Generate pre-signed URL for PUT operation
        # Backblaze B2 requires specific parameters
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_name
            },
            ExpiresIn=expiration,
            HttpMethod='PUT'
        )
        return url
    except Exception as e:
        raise Exception(f"Error generating upload URL: {str(e)}")


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/styles.css')
def styles():
    return send_from_directory('static', 'styles.css')


@app.route('/script.js')
def script():
    return send_from_directory('static', 'script.js')


@app.route('/api/generate-download-url', methods=['POST'])
def generate_download_url():
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        expiration = data.get('expiration', 3600)
        
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
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        expiration = data.get('expiration', 3600)
        
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
        print(f"\nError in list_files: {error_details}\n")
        return jsonify(error_details), 500


@app.route('/api/check-config', methods=['GET'])
def check_config():
    config_status = {
        'B2_APPLICATION_KEY_ID': 'Set' if aws_access_key_id else 'Missing',
        'B2_APPLICATION_KEY': 'Set' if aws_secret_access_key else 'Missing',
        'B2_ENDPOINT_URL': endpoint_url if endpoint_url else 'Missing',
        'B2_BUCKET_NAME': bucket_name if bucket_name else 'Missing',
        'key_id_length': len(aws_access_key_id) if aws_access_key_id else 0,
        'key_length': len(aws_secret_access_key) if aws_secret_access_key else 0,
        'key_id_preview': aws_access_key_id[:10] + '...' if aws_access_key_id else 'Not set',
        'endpoint_preview': endpoint_url if endpoint_url else 'Not set',
    }
    
    # Test bucket access
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        config_status['connection_test'] = 'Success'
        config_status['bucket_access'] = 'Authorized'
    except Exception as e:
        error_msg = str(e)
        config_status['connection_test'] = f'Failed: {error_msg}'
        config_status['bucket_access'] = 'Unauthorized'
        config_status['error_details'] = {
            'error_type': type(e).__name__,
            'error_message': error_msg
        }
        
        # Check if it's a permissions error
        if 'UnauthorizedAccess' in error_msg or 'not authorized' in error_msg.lower():
            config_status['fix_required'] = 'The Application Key needs permission to access this bucket. See README.md troubleshooting section.'
            config_status['key_verification'] = {
                'expected_key_id': '0050428f1a906270000000001',
                'actual_key_id_preview': aws_access_key_id[:10] + '...' + aws_access_key_id[-5:] if aws_access_key_id and len(aws_access_key_id) > 15 else 'N/A',
                'key_id_matches': aws_access_key_id == '0050428f1a906270000000001' if aws_access_key_id else False
            }
    
    return jsonify(config_status)


@app.route('/api/test-upload-url', methods=['POST'])
def test_upload_url():
    """Test if an upload URL is valid by checking its format"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Basic validation - check if URL looks like a valid pre-signed URL
        is_valid = url.startswith('http') and ('X-Amz' in url or 'AWSAccessKeyId' in url)
        
        return jsonify({
            'success': True,
            'url_valid': is_valid,
            'note': 'For direct browser uploads, CORS must be configured on your Backblaze B2 bucket. See README.md for details.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Proxy upload through server to avoid CORS issues"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_name = request.form.get('file_name', file.filename)
        
        if not file_name:
            return jsonify({'error': 'file_name is required'}), 400
        
        # Upload directly to B2 using the S3 client
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            file_name,
            ExtraArgs={'ContentType': file.content_type or 'application/octet-stream'}
        )
        
        return jsonify({
            'success': True,
            'file_name': file_name,
            'message': 'File uploaded successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, port=port)

