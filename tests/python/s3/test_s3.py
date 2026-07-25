import requests


def test_upload(s3_client, s3_bucket, test_object):
    """上传对象，断言响应状态码为 200"""
    key, content = test_object
    resp = s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_list(s3_client, s3_bucket, test_object):
    """先上传再列举，断言测试 key 出现在结果中"""
    key, content = test_object
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    resp = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=key)
    keys = [obj["Key"] for obj in resp.get("Contents", [])]
    assert key in keys


def test_download_roundtrip(s3_client, s3_bucket, test_object):
    """上传后下载，断言内容字节完全一致"""
    key, content = test_object
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    resp = s3_client.get_object(Bucket=s3_bucket, Key=key)
    downloaded = resp["Body"].read()
    assert downloaded == content


def test_download_presigned_url(s3_client, s3_bucket, test_object):
    """生成 get_object 预签名 URL，匿名下载并校验内容一致"""
    key, content = test_object
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_bucket, "Key": key},
        ExpiresIn=300,
    )
    print(f"\n预签名下载地址: {url}")

    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    assert resp.content == content


def test_view_presigned_image_url(s3_client, s3_bucket, image_object):
    """上传真实图片，生成可在浏览器内联查看的预签名 URL"""
    key, content = image_object
    s3_client.put_object(
        Bucket=s3_bucket, Key=key, Body=content, ContentType="image/png"
    )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": s3_bucket,
            "Key": key,
            "ResponseContentType": "image/png",
            "ResponseContentDisposition": "inline",
        },
        ExpiresIn=300,
    )
    print(f"\n图片查看地址: {url}")

    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    assert resp.content == content
    assert resp.headers["Content-Type"] == "image/png"
