import cv2
import numpy as np
from common.utilities import get_files_in_directory
from common.logger import logger
import math
import torch


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

    def detect_basketball(self, frame, lower_hsv, upper_hsv, frame_number, fps):
        # Convert frame to HSV and create a mask
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

        # Morphological opening to remove small objects
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize a dictionary to store timestamp (key) and X coordinate (value)
        detections = {}

        # Calculate the timestamp for the current frame
        timestamp = int(round(frame_number / fps * 1000))  # Convert to milliseconds

        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:  # Avoid division by zero
                continue

            circularity = 4 * math.pi * area / (perimeter * perimeter)

            # Check if area is within the expected range
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
                    logger.console(
                        f"Green circle drawn at {center} : {center[0]}, {center[1]}"
                    )
                    # Add the timestamp and X coordinate to the detections dictionary
                    detections[timestamp] = center[0]

        return frame, detections

    def detect_video_basketball(self, video_path):
        # Load your video
        cap = cv2.VideoCapture(video_path)

        # Get the frame rate of the video
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get lower_hsv and upper_hsv
        lower_hsv, upper_hsv = self.get_average_hsv("resources/image/basketball_sample")
        # Initialize a dictionary to hold timestamp (key) and X coordinate (value)
        basketball_detections = {}

        frame_number = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect the basketball and get its X coordinates with timestamps
            detected_frame, detections = self.detect_basketball(
                frame, lower_hsv, upper_hsv, frame_number, fps
            )
            # Update the basketball_detections dictionary with new detections
            basketball_detections.update(detections)

            frame_number += 1

            # Display the frame
            cv2.imshow("Basketball Detection", detected_frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Print the detections
        for timestamp, x_coord in basketball_detections.items():
            print(f"{timestamp}: {x_coord}")
        return basketball_detections

    def detect_video_basketball_pytorch(self, video_path):
        model = torch.hub.load("ultralytics/yolov5", "yolov5l", pretrained=True)

        # Load video
        cap = cv2.VideoCapture(video_path)

        # Get lower_hsv and upper_hsv
        lower_hsv, upper_hsv = self.get_average_hsv("resources/image/basketball_sample")

        # Initialize a dictionary for detections
        basketball_detections = {}

        # Get the frame rate of the video
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_number = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect objects in the frame
            results = model(frame)

            # Process and display results
            for det in results.xyxy[0]:
                # Extract the bounding box and class label
                x1, y1, x2, y2, conf, cls_id = det
                label = results.names[int(cls_id)]

                # Filter for 'sports ball'
                if label == "sports ball":
                    # Inside YOLO detection loop after identifying 'sports ball'
                    x1, y1, x2, y2 = map(int, det[:4])
                    cropped_frame = frame[y1:y2, x1:x2]
                    hsv_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

                    # Morphological opening
                    kernel = np.ones((5, 5), np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

                    # Find contours
                    contours, _ = cv2.findContours(
                        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                    )
                    for contour in contours:
                        # Draw circle on original frame
                        (x, y), radius = cv2.minEnclosingCircle(contour)
                        center = (
                            int(x) + x1,
                            int(y) + y1,
                        )  # Adjust coordinates for original frame
                        # Calculate the timestamp for the current frame
                        timestamp = int(
                            round(frame_number / fps * 1000)
                        )  # Convert to milliseconds

                        # Store the x-coordinate of the detected basketball's center
                        basketball_detections[timestamp] = center[0]

            frame_number += 1
            # Calculate and display progress
            progress = (frame_number / total_frames) * 100
            print(
                f"Processing: {frame_number}/{total_frames} frames ({progress:.2f}%)",
                end="\r",
            )

            if cv2.waitKey(1) == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        # Outside the while loop
        for timestamp, x_coord in basketball_detections.items():
            print(f"{timestamp}: {x_coord}")

        return basketball_detections
