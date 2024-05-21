# ------------------------------------------------------------------
from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt
import time
import numpy as np
import base64
from PIL import Image
import io


def scan(img, all_images):
    imgs = all_images
    defimg = cv2.imdecode(np.frombuffer(img, np.uint8), -1)

    matches = []

    # if len(DeepFace.find(defimg)) == 0:
    #     return matches
    # # print(DeepFace.extract_faces("C:/Users/hemal/PycharmProjects/FindMe/images/istockphoto-1272744431-612x612.jpg"))

    thresh = 0.4

    for img in imgs:
        base64_decoded = base64.b64decode(img)

        # Open the image from bytes using PIL
        image = Image.open(io.BytesIO(base64_decoded))

        # Convert the image to a NumPy array
        image_np = np.array(image)
        # i1 = cv2.imread(img)
        try:
            topr = DeepFace.verify(defimg, image_np, threshold=thresh)
            print(topr)
            if topr['verified']:
                matches.append(image_np)
        except Exception as e:
            # Handle the exception here
            print(f"An error occurred while processing image: {e}")

    # print(DeepFace.verify(defimg, img))

    #     if DeepFace.verify(defimg, img)['verified'] == "true":
    #         matches.append(defimg)
    #
    # # print(matches)
    # for match in matches:
    #         plt.imshow(cv2.imread(match))

    return matches
