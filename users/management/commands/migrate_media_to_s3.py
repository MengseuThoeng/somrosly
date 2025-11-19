"""
Management command to migrate local media files to MinIO/S3 storage
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import User
from pins.models import Pin
import os
import boto3
from botocore.client import Config


class Command(BaseCommand):
    help = 'Migrate local media files to MinIO/S3 storage'

    def handle(self, *args, **options):
        if not settings.USE_S3:
            self.stdout.write(self.style.ERROR('S3 storage is not enabled in settings'))
            return

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.AWS_S3_REGION_NAME,
            use_ssl=settings.AWS_S3_USE_SSL,
            verify=settings.AWS_S3_VERIFY
        )

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        media_root = settings.BASE_DIR / 'media'
        
        uploaded_count = 0
        error_count = 0

        # Migrate user profile pictures
        self.stdout.write('Migrating user profile pictures...')
        for user in User.objects.filter(profile_picture__isnull=False):
            if user.profile_picture:
                local_path = media_root / str(user.profile_picture)
                
                if local_path.exists():
                    try:
                        # Upload to S3/MinIO
                        with open(local_path, 'rb') as f:
                            s3_client.upload_fileobj(
                                f,
                                bucket_name,
                                str(user.profile_picture),
                                ExtraArgs={
                                    'ContentType': self.get_content_type(str(user.profile_picture)),
                                    'ACL': 'public-read'
                                }
                            )
                        
                        self.stdout.write(self.style.SUCCESS(f'✓ Uploaded: {user.profile_picture}'))
                        uploaded_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'✗ Error uploading {user.profile_picture}: {str(e)}'))
                        error_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ File not found: {local_path}'))

        # Migrate pin images
        self.stdout.write('\nMigrating pin images...')
        for pin in Pin.objects.all():
            if pin.image:
                local_path = media_root / str(pin.image)
                
                if local_path.exists():
                    try:
                        # Upload to S3/MinIO
                        with open(local_path, 'rb') as f:
                            s3_client.upload_fileobj(
                                f,
                                bucket_name,
                                str(pin.image),
                                ExtraArgs={
                                    'ContentType': self.get_content_type(str(pin.image)),
                                    'ACL': 'public-read'
                                }
                            )
                        
                        self.stdout.write(self.style.SUCCESS(f'✓ Uploaded: {pin.image}'))
                        uploaded_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'✗ Error uploading {pin.image}: {str(e)}'))
                        error_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ File not found: {local_path}'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully uploaded: {uploaded_count} files'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {error_count} files'))
        self.stdout.write('='*50)

    def get_content_type(self, filename):
        """Determine content type based on file extension"""
        extension = filename.lower().split('.')[-1]
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
        }
        return content_types.get(extension, 'application/octet-stream')
