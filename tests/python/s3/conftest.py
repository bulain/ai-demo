import uuid
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import boto3
import pytest
from botocore.config import Config
from decouple import config


def _add_trailing_slash(request, **kwargs):
    """给 bucket 级请求路径补尾斜杠。

    该端点是 nginx 反向代理，访问 /bucket 会 301 重定向到 /bucket/；
    但 SigV4 已对无斜杠路径签名，无法跟随重定向，且 botocore 会把 301
    误判为区域重定向导致无限递归。故在签名前补上尾斜杠。
    """
    parts = urlsplit(request.url)
    if not parts.path.endswith("/"):
        request.url = urlunsplit(
            (parts.scheme, parts.netloc, parts.path + "/", parts.query, parts.fragment)
        )
    return request


@pytest.fixture(scope="session")
def s3_client():
    """构造适配 S3 兼容端点的 boto3 客户端"""
    client = boto3.client(
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
    # bucket 级操作（如列举）需要尾斜杠，签名前改写路径
    client.meta.events.register("before-sign.s3.ListObjectsV2", _add_trailing_slash)
    return client


@pytest.fixture(scope="session")
def s3_bucket():
    """返回目标桶名"""
    return config("S3_BUCKET")


@pytest.fixture(scope="session")
def s3_prefix():
    """返回对象 key 前缀"""
    return config("S3_KEY_PREFIX", default="g01")


@pytest.fixture
def test_object(s3_client, s3_bucket, s3_prefix):
    """生成临时测试对象，测试结束后自动删除"""
    # key 格式：<prefix>/YYMMDD/<uuid>.png
    key = f"{s3_prefix}/{date.today():%y%m%d}/{uuid.uuid4().hex}.png"
    content = f"hello s3 {uuid.uuid4()}".encode("utf-8")
    yield key, content
    # teardown：删除临时对象，保持桶干净
    #s3_client.delete_object(Bucket=s3_bucket, Key=key)


_SAMPLE_PNG = Path(__file__).parent / "fixtures" / "sample.png"


@pytest.fixture
def image_object(s3_client, s3_bucket, s3_prefix):
    """生成临时图片测试对象，测试结束后自动删除"""
    key = f"{s3_prefix}/{date.today():%y%m%d}/{uuid.uuid4().hex}.png"
    content = _SAMPLE_PNG.read_bytes()
    yield key, content
    # teardown：删除临时对象，保持桶干净
    #s3_client.delete_object(Bucket=s3_bucket, Key=key)
