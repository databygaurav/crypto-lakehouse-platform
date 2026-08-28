import boto3

from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_BUCKET,
    AWS_SECRET_ACCESS_KEY,
)


class S3Storage:

    def __init__(
        self,
        bucket=AWS_S3_BUCKET,
        region=AWS_REGION,
        s3_client=None
    ):
        if not bucket:
            raise ValueError("AWS_S3_BUCKET is required")

        self.bucket = bucket

        if s3_client is not None:
            self.s3 = s3_client
            return

        client_options = {
            "region_name": region
        }

        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            client_options.update(
                {
                    "aws_access_key_id": AWS_ACCESS_KEY_ID,
                    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY
                }
            )

        self.s3 = boto3.client(
            "s3",
            **client_options
        )

    def upload_file(self, local_file, s3_key):

        self.s3.upload_file(
            str(local_file),
            self.bucket,
            s3_key
        )

        return s3_key
