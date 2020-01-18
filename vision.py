"""
Calls Google's Cloud Vision API to turn images into text
"""
import argparse
from google.cloud import vision
import os
import io

#API Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/dzhou/Downloads/vision.json"

def get_text(filein, fileout):
    """
    Calls the Cloud Vision API to turn an image into text
    """
    client = vision.ImageAnnotatorClient()
    path = filein
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)

    text = response.text_annotations

    file = open(fileout, "w")
    file.write(text[0].description)
    file.close()

parser = argparse.ArgumentParser()
parser.add_argument('in_file', help='The image for text detection.')
parser.add_argument('-out_file', help='Optional output file', default=parser.parse_args().in_file + "totext")
args = parser.parse_args()

get_text(args.in_file, args.out_file)