import boto3
import json
from botocore.client import Config
from decouple import config

# MinIO configuration
s3_client = boto3.client(
    's3',
    endpoint_url=config('AWS_S3_ENDPOINT_URL'),
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
    config=Config(signature_version='s3v4'),
    region_name=config('AWS_S3_REGION_NAME', default='us-east-1'),
    use_ssl=False,
    verify=False
)

bucket_name = config('AWS_STORAGE_BUCKET_NAME')

# Define bucket policy to allow public read access
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}

print(f"🔧 Setting public read policy for bucket: {bucket_name}")
print("--------------------------------------------------")

try:
    # Set the bucket policy
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
    print(f"✅ Bucket policy updated successfully!")
    print(f"📖 The bucket '{bucket_name}' is now publicly readable")
    
    # Verify the policy
    response = s3_client.get_bucket_policy(Bucket=bucket_name)
    print("\n📋 Current bucket policy:")
    print(json.dumps(json.loads(response['Policy']), indent=2))
    
except Exception as e:
    print(f"❌ Error setting bucket policy: {e}")
    print("\n💡 Alternative: You can manually set the policy in MinIO console:")
    print(f"   1. Go to http://159.65.8.211:9001/browser/{bucket_name}")
    print("   2. Click on 'Manage' -> 'Access Rules'")
    print("   3. Set access policy to 'Public' or 'Download'")
