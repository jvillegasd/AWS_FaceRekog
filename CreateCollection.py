import boto3
from botocore.exceptions import ClientError

"""
    This Python script creates a face collection that will be used by AWS Face Rekognition
    for recognize faces from a specific Collection.
"""


AWS_REKOG = boto3.client('rekognition')
COLLECTION_NAME = 'networking'


def create():
    print('Creating collection: {}'.format(COLLECTION_NAME))
    try:
        response = AWS_REKOG.create_collection(CollectionId=COLLECTION_NAME)
        print('Colletion ARN: {}'.format(response['CollectionArn']))
        print('Status code: {}'.format(str(response['StatusCode'])))
        print('Collection: {} has been created.'.format(COLLECTION_NAME))
    except AWS_REKOG.exceptions.ResourceAlreadyExistsException:
        print('Collection: {} already exists.'.format(COLLECTION_NAME))


if __name__ == '__main__':
    create()
