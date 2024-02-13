import cv2
import numpy as np
from common.utilities import get_files_in_directory
from common.logger import logger
import math


class ImageProcessor:

    def __init__(self):
        """
        The constructor for ImageProcessor class.
        """

    def load_and_convert_to_hsv(self, image_path):
        # Load the image
        image = cv2.imread(image_path)
        # Convert to HSV
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    def get_average_hsv(self, image_directory, factor=0.8):
        logger.console(f"Get Avergage HSV in directory {image_directory}")
        image_paths = get_files_in_directory(image_directory)
        logger.console(f"Found {len(image_paths)} images")
        logger.console(image_paths)
        # Load and convert all images to HSV
        hsv_images = [self.load_and_convert_to_hsv(path) for path in image_paths]

        # Combine all HSV values from all images
        all_hsv_values = np.vstack([img.reshape(-1, 3) for img in hsv_images])

        # Calculate the average HSV value
        average_hsv = np.mean(all_hsv_values, axis=0)

        # Calculate the standard deviation or define a fixed threshold
        hsv_std = np.std(all_hsv_values, axis=0)

        # Define your HSV range for detection
        lower_hsv = average_hsv - hsv_std * factor  # Adjust 'factor' as needed
        upper_hsv = average_hsv + hsv_std * factor
        # Print out the determined range
        print(f"Lower HSV: {lower_hsv}")
        print(f"Upper HSV: {upper_hsv}")
        return lower_hsv, upper_hsv

    def detect_basketball(self, frame, lower_hsv, upper_hsv):
        # Convert frame to HSV and create a mask
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

        # Morphological opening to remove small objects
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:  # Avoid division by zero
                continue

            circularity = 4 * math.pi * area / (perimeter * perimeter)

            # Check if area is within the expected range
            logger.console(f"Area is {area}")
            if 100 < area < 150:  # Adjust these values based on the area calculation
                # Calculate the bounding rectangle to check aspect ratio
                x, y, width, height = cv2.boundingRect(contour)
                aspect_ratio = width / float(height)

                # Check if aspect ratio and circularity are within expected range
                if (
                    0.8 < aspect_ratio < 1.2 and circularity > 0.7
                ):  # Adjust circularity threshold as needed
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)
                    cv2.circle(frame, center, radius, (0, 255, 0), 2)  # Green circle

        return frame

    def detect_video_basketball(self):
        # Load your video
        cap = cv2.VideoCapture(
            "/home/irving/webdev/irving/sportlight/output/nba/videos/361_00:40_Wembanyama BLOCK .mp4"
        )
        # Get lower_hsv and upper_hsv
        lower_hsv, upper_hsv = self.get_average_hsv("resources/image/basketball_sample")
        # lower_hsv = np.array([5, 150, 150])
        # upper_hsv = np.array([15, 255, 255])
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect the basketball
            detected_frame = self.detect_basketball(frame, lower_hsv, upper_hsv)

            # Display the frame
            cv2.imshow("Basketball Detection", detected_frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
