"""
Initial attempt at using OCR to read a receipt. Used Google's open source Tesseract OCR. Even after trying various ways
of preprocessing the image, could only obtain ~85% accuracy. Crucial text such as the prices were frequently incorrect.
While this could've been dealt with by building a dictionary of grocery items so that item names and prices could be
matched, instead I tried Google's Cloud Vision API, which performed with nearly 100% accuracy.
"""
import os
import cv2
import imutils
import numpy
import pytesseract
from PIL import Image
from transform import four_point_transform

# Path to tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'


def removeborders(image):
    """
    Finds the largest contour in the image and removes everything outside of it
    """
    # Compute ratio of old height to the new height, keep a copy of the original image,
    # and resize the image to make edge detection more accurate
    ratio = image.shape[0] / 500.0
    original = image.copy()
    image = imutils.resize(image, height=500)

    # Convert image to grayscale and apply Gaussian filter to remove noise
    # and smooth the image out. Erosion removes noise and dilation
    # returns the characters back to normal size
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # kernel = numpy.ones((3, 3), numpy.uint8)
    # gray = cv2.erode(gray, kernel, iterations=1)
    # gray = cv2.dilate(gray, kernel, iterations=1)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Find edges in the image
    edges = cv2.Canny(gray, 75, 200)

    # Find the contours in the edged image, keeping only the largest ones
    contours = cv2.findContours(edges.copy(), cv2.RETR_LIST,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    # Loop over the contours
    for contour in contours:
        # Approximate the contour
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        # If our approximated contour has four points, then we
        # can assume that we have found our paper
        if len(approx) == 4:
            paper = approx
            break

    # Show the contour of the paper
    try:
        cv2.drawContours(image, [paper], -1, (0, 255, 0), 2)
    except:
        raise Exception("No contour with four edges has been found.")
    cv2.imshow("Paper", imutils.resize(image, height=1000))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Apply the four point transform to obtain a top-down
    # view of the original image
    borderless = four_point_transform(
        original, paper.reshape(4, 2) * ratio)

    # Convert the borderless image to grayscale, then threshold it to
    # make it black and white (increase contrast for image processing)
    borderless = cv2.cvtColor(borderless, cv2.COLOR_BGR2GRAY)
    borderless = cv2.threshold(
        borderless, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Show the final image
    cv2.imshow("Final", imutils.resize(borderless, height=1000))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return borderless


def main():
    """
    Processes images using Tesseract OCR
    """

    # Get file name from user input and load the inputted image
    filepath = input("Enter the file path: ").strip()
    image = cv2.imread(filepath)
    # Store grayscale image as a temporary file to apply OCR
    filename = "temp.png"
    cv2.imwrite(filename, removeborders(image))

    # Load the image as a PIL image, apply OCR, and then delete the temporary file
    text = pytesseract.image_to_string(
        Image.open(filename), config='--psm 4')
    os.remove("temp.png")
    file = open(filepath + "text", "w")
    file.write(text)
    file.close()


main()
