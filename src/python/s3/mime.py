import uuid
from datetime import date

import boto3
from botocore.config import Config
from decouple import config


class Attachment:
    """S3 附件工具类：上传图片 + 生成查看签名 URL"""

    def __init__(self):
        # 配置从 .env 读取（python-decouple）
        self._bucket = config("S3_BUCKET")
        self._client = boto3.client(
            "s3",
            endpoint_url=config("S3_ENDPOINT_URL"),
            aws_access_key_id=config("S3_ACCESS_KEY"),
            aws_secret_access_key=config("S3_SECRET_KEY"),
            region_name=config("S3_REGION", default="us-east-1"),
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    def upload(self, image_bytes: bytes) -> str:
        """上传图片，返回 key，格式 'g01_YYMMDD_<uuid>.png'"""
        key = f"g01_{date.today():%y%m%d}_{uuid.uuid4().hex}.png"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=image_bytes,
            ContentType="image/png",
        )
        return key

    def view_url(self, attachment_id: str, expire_seconds: int = 300) -> str:
        """传入 upload 返回的 key，生成内联查看的预签名 URL"""
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": attachment_id,
                "ResponseContentType": "image/png",
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=expire_seconds,
        )
