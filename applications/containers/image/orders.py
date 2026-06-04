import boto3

sqs = boto3.client("sqs", region_name='ap-southeast-1')
dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1')

def get_orders():
	response = sqs.get_queue_attributes(
		QueueUrl=(sqs.get_queue_url(QueueName='QueueOne'))['QueueUrl'],
		AttributeNames=['ApproximateNumberOfMessages',
						'ApproximateNumberOfMessagesNotVisible',
						'ApproximateNumberOfMessagesDelayed']
	)

	ApproximateNumberOfMessages = response['Attributes']['ApproximateNumberOfMessages']
	ApproximateNumberOfMessagesNotVisible = response['Attributes']['ApproximateNumberOfMessagesNotVisible']
	ApproximateNumberOfMessagesDelayed = response['Attributes']['ApproximateNumberOfMessagesDelayed']

	response = sqs.get_queue_attributes(
		QueueUrl=(sqs.get_queue_url(QueueName='QueueTwo'))['QueueUrl'],
		AttributeNames=['ApproximateNumberOfMessagesNotVisible'])

	Q2ApproximateNumberOfMessagesNotVisible = response['Attributes']['ApproximateNumberOfMessagesNotVisible']
	print('Number of Orders Going into the Queue:  ',
		  Q2ApproximateNumberOfMessagesNotVisible)

	response = dynamodb.scan(
		TableName=(dynamodb.list_tables(ExclusiveStartTableName='Coffeeshop'))[
			'TableNames'][0],
		Select='COUNT')

	dynamoItems = response['Count']
	print('Number of Orders recorded in the Database: ', dynamoItems)
	print('Number of Orders fullfilled:             ',
		  ApproximateNumberOfMessagesNotVisible)
	print('Number of Orders the Process of being deliver to Customer: ',
		  ApproximateNumberOfMessagesDelayed)

	status = {
		"ApproximateNumberOfMessagesNotVisible": ApproximateNumberOfMessagesNotVisible,
		"ApproximateNumberOfMessagesDelayed": ApproximateNumberOfMessagesDelayed,
		"ApproximateNumberOfMessages": Q2ApproximateNumberOfMessagesNotVisible,
		"dynamoItems": dynamoItems
		
	}

	return status