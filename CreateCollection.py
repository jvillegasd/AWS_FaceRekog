import boto3

def create(collection_name):
    aws_rekog = boto3.client('rekognition')
    print('Creatin collection: ' + collection_name)
    response = aws_rekog.create_collection(CollectionId=collection_name)
    print('Colletion ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Done!')

if __name__ == '__main__':
    collection_name = 'networking'
    create(collection_name)