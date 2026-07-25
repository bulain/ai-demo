from pathlib import Path

from fastapi.testclient import TestClient

from src.python.s3.server import app

client = TestClient(app)
_SAMPLE_PNG = Path(__file__).parent / "fixtures" / "sample.png"


def test_upload_and_view():
    """上传图片 → 拿 view_url → 查看返回相同字节"""
    data = _SAMPLE_PNG.read_bytes()
    resp = client.post(
        "/images",
        files={"file": ("sample.png", data, "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"].startswith("g01_")
    assert body["key"].endswith(".png")

    view = client.get(body["view_url"])
    assert view.status_code == 200
    assert view.content == data
    assert view.headers["content-type"] == "image/png"


def test_upload_rejects_non_image():
    """上传非图片返回 400"""
    resp = client.post(
        "/images",
        files={"file": ("a.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
