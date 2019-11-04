import boto3

def add_face(s3_bucket, image_name, collection_name):
    s3_rekog = boto3.client('rekognition')
    request = {
        'S3Object': {
            'Bucket': s3_bucket,
            'Name': 'FaceRecog/' + image_name
        }
    }
    response = s3_rekog.index_faces(CollectionId=collection_name, Image=request,
                                   ExternalImageId=image_name, QualityFilter='AUTO', DetectionAttributes=['ALL'])
    face_record = response['FaceRecords']
    print('Result for: ' + image_name)
    print('Face indexed: ')
    print('Face Id: ' + face_record[0]['Face']['FaceId'])
    print('Person name: ' + face_record[0]['Face']['ExternalImageId'])
    print('Location: {}'.format(face_record[0]['Face']['BoundingBox']))

if __name__ == '__main__':
    add_face('awsrecok', 'johnny.jpg', 'networking')