from django.conf import settings
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.auth import default as google_credentials
from rest_framework import status
from rest_framework.response import Response


class BlobHandler:
    @staticmethod
    def delete_blob(blob_name):
        try:
            google_credentials()
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(settings.GS_MEDIA_BUCKET_NAME)
            bucket.delete_blob(blob_name)
        except NotFound as err:
            return Response({"error": str(err)}, status.HTTP_400_BAD_REQUEST)
        return Response(status.HTTP_200_OK)