import boto3

"""
    This Python script creates a face collection that will be used by AWS Face Rekognition
    for recognize faces from a CS course
"""


S3_REKOG = boto3.client('rekognition')
COLLECTION_NAME = 'networking'


def create():
    print('Creatin collection: ' + COLLECTION_NAME)
    response = S3_REKOG.create_collection(CollectionId=COLLECTION_NAME)
    print('Colletion ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Collection: ' + COLLECTION_NAME + ' has been created')


if __name__ == '__main__':
    create()
