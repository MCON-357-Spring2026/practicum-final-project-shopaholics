import boto3
from botocore.exceptions import ClientError
from flask import current_app


def _client():
    return boto3.client(
        "s3",
        region_name=current_app.config["AWS_REGION"],
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
    )


def upload_file(file_obj, key: str, content_type: str = "image/jpeg") -> str:
    """Upload a file-like object to S3. Returns the S3 key."""
    _client().upload_fileobj(
        file_obj,
        current_app.config["S3_BUCKET"],
        key,
        ExtraArgs={"ContentType": content_type},
    )
    return key


def delete_file(key: str) -> None:
    """Delete an object from S3 by key."""
    try:
        _client().delete_object(
            Bucket=current_app.config["S3_BUCKET"],
            Key=key,
        )
    except ClientError:
        pass


def get_presigned_url(key: str) -> str:
    """Return a temporary pre-signed GET URL for a private S3 object."""
    return _client().generate_presigned_url(
        "get_object",
        Params={
            "Bucket": current_app.config["S3_BUCKET"],
            "Key": key,
        },
        ExpiresIn=current_app.config["S3_PRESIGNED_URL_EXPIRY"],
    )


def download_bytes(key: str) -> bytes:
    """Download an S3 object and return its raw bytes."""
    response = _client().get_object(
        Bucket=current_app.config["S3_BUCKET"],
        Key=key,
    )
    return response["Body"].read()
