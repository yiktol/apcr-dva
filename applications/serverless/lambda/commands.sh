zip waiter.zip waiter.py
aws s3 cp waiter.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/waiter.zip
rm -f waiter.zip

zip barista.zip barista.py
aws s3 cp barista.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/barista.zip
rm -f barista.zip

zip dbwriter.zip dbwriter.py
aws s3 cp dbwriter.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/dbwriter.zip
rm -f dbwriter.zip

zip -r sales.zip ./sales.py
aws s3 cp ./sales.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/sales.zip
rm -f sales.zip

zip -r status.zip ./status.py
aws s3 cp ./status.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/status.zip
rm -f status.zip

zip -r orders.zip ./orders.py
aws s3 cp ./orders.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/orders.zip
rm -f orders.zip

zip cashier.zip ./cashier.py
aws s3 cp ./cashier.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/cashier.zip
rm -f cashier.zip

zip authorizer.zip authorizer.py
aws s3 cp authorizer.zip s3://yikyakyuk-ap-southeast-1-875692608981/wat/lambda/authorizer.zip
rm -f authorizer.zip



aws s3 cp /home/ubuntu/WAT/00-Demo/lambda/coffeshop/app.js s3://yikyakyuk-ap-southeast-1-875692608981/wat/website/static/assets/js/
aws s3 cp /home/ubuntu/WAT/00-Demo/lambda/coffeshop/coffee-order.css s3://yikyakyuk-ap-southeast-1-875692608981/wat/website/static/assets/css/
aws s3 cp /home/yikyakyuk/WAT/00-Demo/lambda/coffeshop/orderhere.html s3://yikyakyuk-ap-southeast-1-875692608981/wat/website/
