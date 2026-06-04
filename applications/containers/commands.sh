zip -r website.zip ./*
aws s3 cp website.zip s3://yikyakyuk-ap-southeast-1-875692608981/artifacts/website.zip
rm -f website.zip

