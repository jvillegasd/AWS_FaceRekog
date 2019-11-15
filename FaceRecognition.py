import boto3
import io
import tweepy
import credentials
import requests
from pprint import pprint
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

"""
    This Python script gets an image from AWS S3 Bucket and use it for face recogniction.
    After a face is detected, it tries to recognize who is they comparing it with a
    Amazon Rekognition's Collection. 
    Amazon Rekognition's JSON response returns a boundary box where the faces lie and their
    coordinates are expressed as the ratio of the image. Coordinates formulas:
        xCoordinate = xInPixels/imageWidth
        yCoordinate = yInPixels/imageHeight
    
    There are two methods to get photos for face recognitions (testcases):
    -) Using Amazon S3: face_recog_with_s3()
    -) Using Twitter API: face_recog_with_twitter()
"""

AWS_REKOG = boto3.client('rekognition')
S3_CONN = boto3.resource('s3')
S3_BUCKET_NAME = 'awsrecok'
S3_TESTCASES_FOLDER = 'Testcases/'
IMAGE_NAME = 'prueba8.jpg'
COLLECTION_NAME = 'networking'
TWITTER_FACE_RECOG_HASHTAG = 'face_networking2019UN'


def get_image_from_s3():
    aws_s3_object = S3_CONN.Object(
        S3_BUCKET_NAME, S3_TESTCASES_FOLDER + IMAGE_NAME)
    response = aws_s3_object.get()
    bytes_array = io.BytesIO(response['Body'].read())
    return Image.open(bytes_array)


def get_bounding_boxes(request):
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


def face_recognition_saving_image(image):
    print('Starting to recognize faces from Amazon S3 Bucket: {}'.format(S3_BUCKET_NAME))
    request = {
        'S3Object': {
            'Bucket': S3_BUCKET_NAME,
            'Name': S3_TESTCASES_FOLDER + IMAGE_NAME
        }
    }
    bounding_boxes = get_bounding_boxes(request)
    img_width, img_height = image.size
    faces_name = []
    for face in bounding_boxes:
        faces_name.append(get_face_name(face, image))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Hack-Bold.ttf", 37)
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
    print('Faces recognition has finished.')


def face_recog_with_s3():
    image = get_image_from_s3()
    face_recognition_saving_image(image)


def face_recognition_retweet(image, bytes_array, tweet_user):
    twitter_reply = '@{} Recognized faces: '.format(tweet_user)
    request = {
        'Bytes': bytes_array.getvalue()
    }
    bounding_boxes = get_bounding_boxes(request)
    for face in bounding_boxes:
        name = get_face_name(face, image)
        if name:
            twitter_reply += name + ","
    return twitter_reply


def face_recog_with_twitter():
    print('Starting to recognize faces from Twitter hashtag: {}'.format(
        TWITTER_FACE_RECOG_HASHTAG))
    auth = tweepy.OAuthHandler(
        credentials.CONSUMER_API_KEY, credentials.CONSUMER_API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN,
                          credentials.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    for tweet in tweepy.Cursor(api.search, q=TWITTER_FACE_RECOG_HASHTAG, include_entities=True).items():
        if 'media' in tweet.entities:
            image_url = tweet.entities['media'][0]['media_url']
            response = requests.get(image_url)
            bytes_array = io.BytesIO(response.content)
            image = Image.open(bytes_array)
            tweet_user = tweet.user.screen_name
            tweet_reply = face_recognition_retweet(
                image, bytes_array, tweet_user)
            try:
                api.update_status(tweet_reply[:-1], tweet.id)
                print('Replied tweet.')
            except tweepy.error.TweepError:
                print('This tweet has already been replied.')
    print('Faces recognition has finished.')


if __name__ == '__main__':
    face_recog_with_twitter()
