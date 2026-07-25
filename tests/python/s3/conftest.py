import uuid

import boto3
import pytest
from botocore.config import Config
from decouple import config


@pytest.fixture(scope="session")
def s3_client():
    """构造适配 S3 兼容端点的 boto3 客户端"""
    return boto3.client(
        "s3",
        endpoint_url=config("S3_ENDPOINT_URL"),
        aws_access_key_id=config("S3_ACCESS_KEY"),
        aws_secret_access_key=config("S3_SECRET_KEY"),
        region_name=config("S3_REGION", default="us-east-1"),
        config=Config(
            signature_version="s3v4",              # 对应 api: S3v4
            s3={"addressing_style": "path"},       # 对应 path: auto
        ),
    )


@pytest.fixture(scope="session")
def s3_bucket():
    """返回目标桶名"""
    return config("S3_BUCKET")


@pytest.fixture
def test_object(s3_client, s3_bucket):
    """生成临时测试对象，测试结束后自动删除"""
    key = f"test-{uuid.uuid4()}.txt"
    content = f"hello s3 {uuid.uuid4()}".encode("utf-8")
    yield key, content
    # teardown：删除临时对象，保持桶干净
    s3_client.delete_object(Bucket=s3_bucket, Key=key)
