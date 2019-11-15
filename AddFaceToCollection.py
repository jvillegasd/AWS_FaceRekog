import boto3
import tweepy
import io
import credentials
import requests
from pprint import pprint

"""
    This Python script connects to a folder located on an AWS S3 Bucket.
    Retrieve all faces that will be added in the Current Collection in order to
    make Amazon Rekognition works with a specific Collection.
    
    Also, this script fetch photos from tweets with a certain hashtag attached in order
    to add this faces on Amazon Rekognition.
    Tweet Schema: {
        hashtag
        name
    }
    Example:
            #hashtagThatIWant
            Sara
    Example:
            #hashtagThatIWant
            Scarlett_Johanson

"""


AWS_REKOG = boto3.client('rekognition')
S3_CONN = boto3.client('s3')
S3_BUCKET_NAME = 'awsrecok'
S3_FACE_FOLDER = 'FaceRecog/'
COLLECTION_NAME = 'networking'
TWITTER_ADD_FACE_HASHTAG = '#networking2019UN'


def init_collection_from_s3():
    print('Fetching images from Amazon S3')
    response = S3_CONN.list_objects_v2(
        Bucket=S3_BUCKET_NAME, Prefix=S3_FACE_FOLDER, Delimiter='/')
    images_object = response['Contents']
    for image_object in images_object:
        if image_object['Size'] == 0:
            continue
        add_face_from_s3(image_object['Key'])


def add_face_from_s3(image_route):
    print('Adding face...')
    request = {
        'S3Object': {
            'Bucket': S3_BUCKET_NAME,
            'Name': image_route
        }
    }
    image_name = image_route.replace(S3_FACE_FOLDER, "")
    response = AWS_REKOG.index_faces(CollectionId=COLLECTION_NAME, Image=request,
                                     ExternalImageId=image_name, QualityFilter='AUTO', DetectionAttributes=['ALL'])
    face_record = response['FaceRecords']
    print('Result for: ' + image_name)
    print('Face indexed: ')
    print('Face Id: ' + face_record[0]['Face']['FaceId'])
    print('Person name: ' + face_record[0]['Face']['ExternalImageId'])
    print('Location: {}'.format(face_record[0]['Face']['BoundingBox']))
    print('------------------------------------------------------------------------------------------------------------')


def init_collection_from_twitter():
    print('|===========================================================================================================|')
    print('Fetching images from Twitter hashtag: {}'.format(
        TWITTER_ADD_FACE_HASHTAG))
    auth = tweepy.AppAuthHandler(
        credentials.CONSUMER_API_KEY, credentials.CONSUMER_API_SECRET_KEY)
    api = tweepy.API(auth)
    for tweet in tweepy.Cursor(api.search, q=TWITTER_ADD_FACE_HASHTAG, include_entities=True).items():
        image_name = tweet.text.replace(TWITTER_ADD_FACE_HASHTAG, '')
        if 'media' in tweet.entities:
            image_url = tweet.entities['media'][0]['media_url']
            tweet_url = tweet.entities['media'][0]['url']
            image_name = image_name.replace(tweet_url, '')
            image_name = image_name.strip()
            response = requests.get(image_url)
            bytes_array = io.BytesIO(response.content)
            add_face_from_twitter(bytes_array, image_name)


def add_face_from_twitter(bytes_array, image_name):
    print('Adding face...')
    request = {
        'Bytes': bytes_array.getvalue()
    }
    response = AWS_REKOG.index_faces(CollectionId=COLLECTION_NAME, Image=request,
                                     ExternalImageId=image_name, QualityFilter='AUTO', DetectionAttributes=['ALL'])
    face_record = response['FaceRecords']
    print('Result for: ' + image_name)
    print('Face indexed: ')
    print('Face Id: ' + face_record[0]['Face']['FaceId'])
    print('Person name: ' + face_record[0]['Face']['ExternalImageId'])
    print('Location: {}'.format(face_record[0]['Face']['BoundingBox']))
    print('------------------------------------------------------------------------------------------------------------')


if __name__ == '__main__':
    print('Initializing Collection: ' + COLLECTION_NAME)
    init_collection_from_s3()
    init_collection_from_twitter()
    print('Collection: ' + COLLECTION_NAME + ' has been initialized')
