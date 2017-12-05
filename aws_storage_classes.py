from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """uploads to 'mybucket/staticfile/', serves from 'cloudfront.net/staticfile/'"""
    location = 'staticfile'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_S3_CUSTON_DOMAIN
        super(StaticStorage, self).__init__(*args, **kwargs)

class MediaStorage(S3Boto3Storage):
    """uploads to 'mybucket/media/', serves from 'cloudfront.net/media/'"""
    location = 'media'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = settings.AWS_S3_CUSTON_DOMAIN
        super(MediaStorage, self).__init__(*args, **kwargs)
