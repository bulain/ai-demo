def test_upload(s3_client, s3_bucket, test_object):
    """上传对象，断言响应状态码为 200"""
    key, content = test_object
    resp = s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
