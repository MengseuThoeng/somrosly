"""
Custom storage backends for Somrosly
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """Custom storage for media files using MinIO/S3"""
    location = ''
    file_overwrite = False
    default_acl = 'public-read'
