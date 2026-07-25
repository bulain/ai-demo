import uuid
from datetime import date
from pathlib import Path

import boto3
from botocore.config import Config
from decouple import config
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI()

_BUCKET = config("S3_BUCKET")
_PREFIX = config("S3_KEY_PREFIX", default="g01")  # 前缀不能含下划线
_client = boto3.client(
    "s3",
    endpoint_url=config("S3_ENDPOINT_URL"),
    aws_access_key_id=config("S3_ACCESS_KEY"),
    aws_secret_access_key=config("S3_SECRET_KEY"),
    region_name=config("S3_REGION", default="us-east-1"),
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)


@app.post("/images")
async def upload_image(file: UploadFile):
    """上传图片，返回 key 与查看地址"""
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")
    # 扩展名跟随上传文件名，缺省用 .png
    ext = Path(file.filename or "").suffix or ".png"
    name = f"{date.today():%y%m%d}/{uuid.uuid4().hex}{ext}"  # 260725/abc.png
    s3_key = f"{_PREFIX}/{name}"                             # g01/260725/abc.png（存 S3）
    key = f"{_PREFIX}_{name.replace('/', '_')}"              # g01_260725_abc.png（对外返回）
    _client.put_object(
        Bucket=_BUCKET, Key=s3_key, Body=await file.read(), ContentType=content_type
    )
    return {"key": key, "view_url": f"/images/{key}"}


@app.get("/images/{key}")
async def view_image(key: str):
    """从 S3 读取图片并直接返回字节流"""
    s3_key = key.replace("_", "/", 2)  # g01_260725_abc.png -> g01/260725/abc.png
    try:
        obj = _client.get_object(Bucket=_BUCKET, Key=s3_key)
    except _client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="图片不存在")
    return Response(
        content=obj["Body"].read(),
        media_type=obj.get("ContentType", "application/octet-stream"),
    )
