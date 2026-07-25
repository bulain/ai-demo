import uuid
from datetime import date

import boto3
from botocore.config import Config
from decouple import config
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI()

_BUCKET = config("S3_BUCKET")
_client = boto3.client(
    "s3",
    endpoint_url=config("S3_ENDPOINT_URL"),
    aws_access_key_id=config("S3_ACCESS_KEY"),
    aws_secret_access_key=config("S3_SECRET_KEY"),
    region_name=config("S3_REGION", default="us-east-1"),
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

# content-type -> 扩展名映射
_EXT = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp"}


@app.post("/images")
async def upload_image(file: UploadFile):
    """上传图片，返回 key 与查看地址"""
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")
    ext = _EXT.get(content_type, "bin")
    key = f"g01_{date.today():%y%m%d}_{uuid.uuid4().hex}.{ext}"
    _client.put_object(
        Bucket=_BUCKET, Key=key, Body=await file.read(), ContentType=content_type
    )
    return {"key": key, "view_url": f"/images/{key}"}


@app.get("/images/{key}")
async def view_image(key: str):
    """从 S3 读取图片并直接返回字节流"""
    try:
        obj = _client.get_object(Bucket=_BUCKET, Key=key)
    except _client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="图片不存在")
    return Response(
        content=obj["Body"].read(),
        media_type=obj.get("ContentType", "application/octet-stream"),
    )
