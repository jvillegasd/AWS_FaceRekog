import boto3
import io
from pprint import pprint
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

"""
    This Python script gets an image from AWS S3 Bucket and use it for face recogniction.
    After a face is detected, it tries to recognize who is they comparing it with a
    AWS Face Rekognition Collection from a CS course. 
    AWS Face Rekognition JSON response returns a boundary box where the faces lie and their
    coordinates are expressed as the ratio of the image. Coordinates formulas:
        xCoordinate = xInPixels/imageWidth
        yCoordinate = yInPixels/imageHeight
"""

AWS_REKOG = boto3.client('rekognition')
S3_CONN = boto3.resource('s3')
S3_BUCKET_NAME = 'awsrecok'
IMAGE_NAME = 'prueba7.jpg'
COLLECTION_NAME = 'networking'


def get_image():
    aws_s3_object = S3_CONN.Object(
        S3_BUCKET_NAME, 'Testcases/' + IMAGE_NAME)
    response = aws_s3_object.get()
    bytes_array = io.BytesIO(response['Body'].read())
    return Image.open(bytes_array)


def get_bounding_boxes():
    request = {
        'S3Object': {
            'Bucket': S3_BUCKET_NAME,
            'Name': 'Testcases/' + IMAGE_NAME
        }
    }
    response = AWS_REKOG.detect_faces(Image=request, Attributes=['ALL'])
    bounding_boxes = []
    for details in response['FaceDetails']:
        bounding_boxes.append(details['BoundingBox'])
    return bounding_boxes


def face_exists(request):
    response = AWS_REKOG.detect_faces(Image=request, Attributes=['ALL'])
    return response['FaceDetails'] != []


def get_face_name(face, image):
    img_width, img_height = image.size
    width = img_width * face['Width']
    height = img_height * face['Height']
    left = img_width * face['Left']
    top = img_height * face['Top']
    area = (left, top, left + width, top + height)
    cropped_image = image.crop(area)
    bytes_array = io.BytesIO()
    cropped_image.save(bytes_array, format="PNG")
    request = {
        'Bytes': bytes_array.getvalue()
    }
    if face_exists(request):
        response = AWS_REKOG.search_faces_by_image(
            CollectionId=COLLECTION_NAME, Image=request, FaceMatchThreshold=70)
        if response['FaceMatches']:
            return response['FaceMatches'][0]['Face']['ExternalImageId']
        else:
            return 'Not recognized'
    return ''


def face_recognition(image):
    print('Starting to recognize faces...')
    bounding_boxes = get_bounding_boxes()
    img_width, img_height = image.size
    faces_name = []
    for face in bounding_boxes:
        faces_name.append(get_face_name(face, image))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Hack-Bold.ttf", 40)
    for i in range(len(bounding_boxes)):
        if not faces_name[i]:
            continue
        width = img_width * bounding_boxes[i]['Width']
        height = img_height * bounding_boxes[i]['Height']
        left = img_width * bounding_boxes[i]['Left']
        top = img_height * bounding_boxes[i]['Top']
        points = ((left, top), (left + width, top), (left + width,
                                                     top + height), (left, top + height), (left, top))
        draw.line(points, fill='#00d400', width=4)
        draw.text((left, top), faces_name[i], font=font)
        print('A face has been recognized. Name: ' + faces_name[i])
    image.save("output.png")
    print('Faces recognition has finished')


if __name__ == '__main__':
    image = get_image()
    face_recognition(image)
