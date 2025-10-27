"""
Test MinIO connection and bucket access
Run this script to verify MinIO setup: python test_minio.py
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'somrosly_project.settings')
django.setup()

import boto3
from botocore.client import Config
from django.conf import settings

def test_minio_connection():
    """Test MinIO connection and bucket access"""
    print("🔍 Testing MinIO Connection...")
    print("-" * 50)
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.AWS_S3_REGION_NAME,
            verify=settings.AWS_S3_VERIFY
        )
        
        print(f"✅ Connection successful!")
        print(f"📦 Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
        print(f"🪣 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        print("-" * 50)
        
        # List buckets
        print("\n📋 Available Buckets:")
        response = s3_client.list_buckets()
        for bucket in response['Buckets']:
            print(f"  - {bucket['Name']}")
        
        # Check if our bucket exists
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        print(f"\n🔍 Checking bucket '{bucket_name}'...")
        
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists and is accessible!")
            
            # Try to list objects in the bucket
            print(f"\n📁 Listing objects in '{bucket_name}':")
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
            
            if 'Contents' in response:
                print(f"  Found {len(response['Contents'])} object(s):")
                for obj in response['Contents']:
                    print(f"    - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print("  (Bucket is empty)")
                
        except s3_client.exceptions.NoSuchBucket:
            print(f"❌ Bucket '{bucket_name}' does not exist!")
            print(f"\n💡 Creating bucket '{bucket_name}'...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' created successfully!")
            
            # Set bucket policy to public-read
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            import json
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print(f"✅ Bucket policy set to public-read")
        
        print("\n" + "=" * 50)
        print("🎉 MinIO is configured correctly!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("  1. Check if MinIO server is running")
        print("  2. Verify credentials in .env file")
        print("  3. Check network connectivity to MinIO server")
        print("  4. Ensure bucket exists or create it manually")
        return False

if __name__ == '__main__':
    test_minio_connection()
