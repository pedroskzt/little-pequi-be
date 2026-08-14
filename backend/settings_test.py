from .settings import *

GS_PROJECT_ID = "test-project"
GS_MEDIA_BUCKET_NAME = "test-bucket"
MEDIA_URL = f"https://storage.googleapis.com/{GS_MEDIA_BUCKET_NAME}/"

STORAGES["default"]["OPTIONS"]["bucket_name"] = GS_MEDIA_BUCKET_NAME
STORAGES["staticfiles"]["OPTIONS"]["bucket_name"] = GS_MEDIA_BUCKET_NAME
