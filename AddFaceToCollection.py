import boto3
from pprint import pprint

"""
    This Python script connects to a folder located on an AWS S3 Bucket.
    Retrieve all faces that will be added in the Current Collection in order to
    make AWS Face Rekognition works with a CS Course students faces
"""


S3_REKOG = boto3.client('rekognition')
S3_CONN = boto3.client('s3')
S3_BUCKET_NAME = 'awsrecok'
COLLECTION_NAME = 'networking'


def init_collection():
    print('Initializing Collection: ' + COLLECTION_NAME)
    response = S3_CONN.list_objects_v2(
        Bucket=S3_BUCKET_NAME, Prefix='FaceRecog/', Delimiter='/')
    images_object = response['Contents']
    for image_object in images_object:
        if image_object['Size'] == 0:
            continue
        add_face(image_object['Key'])
    print('Collection: ' + COLLECTION_NAME + ' has been initialized')


def add_face(image_route):
    print('Adding face...')
    request = {
        'S3Object': {
            'Bucket': S3_BUCKET_NAME,
            'Name': image_route
        }
    }
    image_name = image_route.replace("FaceRecog/", "")
    response = S3_REKOG.index_faces(CollectionId=COLLECTION_NAME, Image=request,
                                    ExternalImageId=image_name, QualityFilter='AUTO', DetectionAttributes=['ALL'])
    face_record = response['FaceRecords']
    print('Result for: ' + image_name)
    print('Face indexed: ')
    print('Face Id: ' + face_record[0]['Face']['FaceId'])
    print('Person name: ' + face_record[0]['Face']['ExternalImageId'])
    print('Location: {}'.format(face_record[0]['Face']['BoundingBox']))
    print('---------------------------------------------------------------------------------------------')


if __name__ == '__main__':
    init_collection()
