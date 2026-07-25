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
