import cv2
import numpy as np


def get_black_to_white_ratio(image):
    if image is None:
        return 0

    # Define thresholds
    # Black/gray: pixel values from 0 to 200 (adjust threshold as needed)
    # White: pixel values from 201 to 255
    black_gray_mask = image <= 200
    white_mask = image > 200

    # Count pixels
    black_gray_count = np.sum(black_gray_mask)
    white_count = np.sum(white_mask)

    # Calculate the ratio
    if white_count > 0:  # Avoid division by zero
        ratio = black_gray_count / white_count
    else:
        ratio = float("inf")  # All pixels are black/gray

    return ratio


def compare_images(image1, image2):
    if image1 is None or image2 is None:
        return 0

    # Convert to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Detect ORB keypoints and descriptors
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

    # Match descriptors using BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches by distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Check the number of good matches
    print(f"Number of matches: {len(matches)}")

    # leaving the following comment block for debug purposes when needed -- TODO: add argparse arg to toggle
    # if len(matches) > 10:  # Threshold for similarity
    #     print("Images are similar")
    #     cv2.imshow(f"{len(matches)} Images are similar - Image 1", image1)
    #     cv2.imshow(f"{len(matches)} Images are similar - Image 2", image2)
    # else:
    #     print("Images are not similar")
    #     cv2.imshow(f"{len(matches)} Images are not similar - Image 1", image1)
    #     cv2.imshow(f"{len(matches)} Images are not similar - Image 2", image2)

    # # Wait for a key press and close the windows
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return len(matches)
