from presign import handler


class FakeS3:
    def __init__(self):
        self.called_with = None

    def generate_presigned_url(self, op, Params, ExpiresIn):
        self.called_with = (op, Params, ExpiresIn)
        return f"https://example-bucket.s3.amazonaws.com/{Params['Key']}?sig=abc"


def test_generate_url_happy_path():
    s3 = FakeS3()
    url, err = handler.generate_url(s3, "bucket", "ORD-000123")
    assert err is None
    assert "receipts/ORD-000123.pdf" in url
    op, params, expires = s3.called_with
    assert op == "get_object"
    assert params["Key"] == "receipts/ORD-000123.pdf"
    assert expires == handler.EXPIRES_IN == 900


def test_generate_url_rejects_bad_order_id():
    s3 = FakeS3()
    url, err = handler.generate_url(s3, "bucket", "nope")
    assert url is None
    assert err["statusCode"] == 400
    assert s3.called_with is None
