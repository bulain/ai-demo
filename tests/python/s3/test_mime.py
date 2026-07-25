import requests

from src.python.s3.mime import Attachment


def test_upload_and_view():
    """上传图片 → 查看签名 URL → 匿名下载内容一致"""
    att = Attachment()
    data = open("tests/python/s3/fixtures/sample.png", "rb").read()
    key = att.upload(data)
    assert key.startswith("g01_")
    assert key.endswith(".png")
    assert len(key) == len("g01_YYMMDD_") + 32 + len(".png")

    url = att.view_url(key)
    print(f"\n图片查看地址: {url}")
    assert "response-content-type=image" in url
    assert "response-content-disposition=inline" in url

    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    assert resp.content == data
    assert resp.headers["Content-Type"] == "image/png"
