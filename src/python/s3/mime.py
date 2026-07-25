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
        self._prefix = config("S3_KEY_PREFIX", default="g01")  # 前缀不能含下划线
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
        """上传图片，S3 路径 '<prefix>/YYMMDD/<uuid>.png'，返回 key '<prefix>_YYMMDD_<uuid>.png'"""
        name = f"{date.today():%y%m%d}/{uuid.uuid4().hex}.png"  # 260725/abc.png
        s3_key = f"{self._prefix}/{name}"                       # g01/260725/abc.png（存 S3）
        key = f"{self._prefix}_{name.replace('/', '_')}"        # g01_260725_abc.png（对外返回）
        self._client.put_object(
            Bucket=self._bucket,
            Key=s3_key,
            Body=image_bytes,
            ContentType="image/png",
        )
        return key

    def download(self, attachment_id: str) -> bytes:
        """传入 upload 返回的 key，从 S3 读取原始字节"""
        s3_key = attachment_id.replace("_", "/", 2)  # g01_260725_abc.png -> g01/260725/abc.png
        obj = self._client.get_object(Bucket=self._bucket, Key=s3_key)
        return obj["Body"].read()

    def view_url(self, attachment_id: str, expire_seconds: int = 300) -> str:
        """传入 upload 返回的 key，生成内联查看的预签名 URL"""
        s3_key = attachment_id.replace("_", "/", 2)  # g01_260725_abc.png -> g01/260725/abc.png
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": s3_key,
                "ResponseContentType": "image/png",
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=expire_seconds,
        )
