import boto3

from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_S3_BUCKET
)


class S3Storage:

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def upload_file(self, local_file, s3_key):

        self.s3.upload_file(
            local_file,
            AWS_S3_BUCKET,
            s3_key
        )

        print("File uploaded successfully!")