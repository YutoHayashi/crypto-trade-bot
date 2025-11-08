import boto3

from .exception import RuntimeException


class S3ClientException(RuntimeException):
    """Base exception for S3 client errors."""
    _title = "S3 Client Exception"


class S3Client:
    """
    A simple S3 client to interact with AWS S3 buckets.
    This client provides methods to get objects from a specified S3 bucket.
    """
    bucket: str = None
    _client: boto3.client = None
    
    def __init__(self, bucket: str = None):
        """
        Initializes the S3Client with the specified bucket name.
        :param bucket: The name of the S3 bucket to interact with.
        """
        self.bucket = bucket
        self._client = boto3.client('s3')
    
    def get_object(self, key: str):
        try:
            response = self._client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            return response
        except Exception as e:
            raise S3ClientException(f"Getting object {key} from bucket {self._bucket}: {e}") from e