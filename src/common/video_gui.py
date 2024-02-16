import cv2

# Constants for layout
PLAY_PAUSE_BUTTON_WIDTH = 50
PLAY_PAUSE_BUTTON_HEIGHT = 50
KEYFRAME_BUTTON_LEFT = 80
KEYFRAME_BUTTON_WIDTH = 100
DELETE_BUTTON_WIDTH = 100
TIMELINE_LENGTH = 600
TIMELINE_HEIGHT = 20

# Constants for vertical position from the bottom of the window
BUTTONS_BOTTOM_OFFSET = 30
TIMELINE_BOTTOM_OFFSET = 10


class BasketballVideoGUI:
    def __init__(self, video_file, x_coordinates):
        self.video_file = video_file
        self.x_coordinates = x_coordinates
        self.playing = True
        self.cap = cv2.VideoCapture(video_file)
        self.keyframe_mode = False
        self.delete_mode = False
        if not self.cap.isOpened():
            raise ValueError("Video file could not be opened")

        # Initialize window height
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Could not read the video file")

        # Here we're assuming that the height of the video frame is the height of the window
        self.window_height = frame.shape[0]

        # Other initializations...
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cv2.namedWindow("Basketball Video GUI")
        cv2.setMouseCallback("Basketball Video GUI", self.mouse_callback)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Calculate the Y coordinates for the button and timeline
            button_top = (
                self.window_height - BUTTONS_BOTTOM_OFFSET - PLAY_PAUSE_BUTTON_HEIGHT
            )
            button_bottom = self.window_height - BUTTONS_BOTTOM_OFFSET
            timeline_top = self.window_height - TIMELINE_BOTTOM_OFFSET - TIMELINE_HEIGHT
            timeline_bottom = self.window_height - TIMELINE_BOTTOM_OFFSET
            print(f"Clicked at x={x}, y={y}")
            print(f"Button top: {button_top}, Timeline top: {timeline_top}")
            delete_button_left = KEYFRAME_BUTTON_LEFT + KEYFRAME_BUTTON_WIDTH + 20
            if (
                delete_button_left <= x <= delete_button_left + DELETE_BUTTON_WIDTH
                and button_top <= y <= button_bottom
            ):
                self.delete_mode = not self.delete_mode
                self.keyframe_mode = False

            # Handle keyframe deletion
            elif (
                self.delete_mode
                and 20 <= x <= 20 + TIMELINE_LENGTH
                and timeline_top <= y <= timeline_bottom
            ):
                print("Deleting keyframe")
                # Find and delete the nearest keyframe to the click position
                clicked_frame = int(((x - 20) / TIMELINE_LENGTH) * self.total_frames)
                print(f"Clicked on frame {clicked_frame}")
                timestamp_to_delete = min(
                    self.x_coordinates.keys(),
                    key=lambda k: abs(self.x_coordinates[k] - clicked_frame),
                )
                del self.x_coordinates[timestamp_to_delete]
                self.delete_mode = False

            # Check if the click is within the play/pause button area
            elif (
                20 <= x <= 20 + PLAY_PAUSE_BUTTON_WIDTH
                and button_top <= y <= button_bottom
            ):
                self.playing = not self.playing
            # Check if the click is within the timeline area
            elif (
                20 <= x <= 20 + TIMELINE_LENGTH
                and timeline_top <= y <= timeline_bottom
                and not self.delete_mode
            ):
                clicked_frame = int(((x - 20) / TIMELINE_LENGTH) * self.total_frames)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, clicked_frame)
            # Toggle keyframe mode when keyframe button is clicked
            if (
                KEYFRAME_BUTTON_LEFT
                <= x
                <= KEYFRAME_BUTTON_LEFT + KEYFRAME_BUTTON_WIDTH
                and button_top <= y <= button_bottom
            ):
                self.keyframe_mode = not self.keyframe_mode
                self.delete_mode = False
                # Check if keyframe mode is active and click is on the video area
            elif self.keyframe_mode and y < button_top and y < timeline_top:
                # Get current timestamp
                timestamp = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))

                # Save the timestamp and X coordinate
                self.x_coordinates[timestamp] = x

                # Print or handle the saved keyframe
                print(f"Keyframe added at timestamp: {timestamp}ms, X coordinate: {x}")

                # Reset keyframe mode
                self.keyframe_mode = False
            print(f"Keyframes: {self.x_coordinates}")

    def draw_add_keyframe_button(self, frame):
        # Change button color based on self.keyframe_mode
        button_color = (0, 255, 0) if self.keyframe_mode else (255, 255, 255)
        button_text_color = (0, 0, 0)
        button_top = (
            self.window_height - BUTTONS_BOTTOM_OFFSET - PLAY_PAUSE_BUTTON_HEIGHT
        )
        button_bottom = self.window_height - BUTTONS_BOTTOM_OFFSET
        top_left = (KEYFRAME_BUTTON_LEFT, button_top)
        bottom_right = (
            KEYFRAME_BUTTON_LEFT + KEYFRAME_BUTTON_WIDTH,
            button_bottom,
        )

        cv2.rectangle(frame, top_left, bottom_right, button_color, -1)
        cv2.putText(
            frame,
            "Keyframe",
            (KEYFRAME_BUTTON_LEFT + 5, button_top + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            button_text_color,
            2,
        )

    def draw_play_pause_button(self, frame):
        video_height = frame.shape[0]
        button_color = (255, 255, 255)
        button_text_color = (0, 0, 0)
        if self.playing:
            button_text = "Pause"
        else:
            button_text = "Play"

        # Calculate top-left position based on the window size
        top_left = (20, video_height - BUTTONS_BOTTOM_OFFSET - PLAY_PAUSE_BUTTON_HEIGHT)
        bottom_right = (
            top_left[0] + PLAY_PAUSE_BUTTON_WIDTH,
            top_left[1] + PLAY_PAUSE_BUTTON_HEIGHT,
        )

        cv2.rectangle(frame, top_left, bottom_right, button_color, -1)
        cv2.putText(
            frame,
            button_text,
            (top_left[0] + 5, top_left[1] + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            button_text_color,
            2,
        )

    def draw_delete_keyframe_button(self, frame):
        # Choose position and size for the delete button
        button_color = (0, 0, 255) if self.delete_mode else (255, 255, 255)
        delete_button_left = KEYFRAME_BUTTON_LEFT + KEYFRAME_BUTTON_WIDTH + 20
        button_top = (
            self.window_height - BUTTONS_BOTTOM_OFFSET - PLAY_PAUSE_BUTTON_HEIGHT
        )
        button_bottom = self.window_height - BUTTONS_BOTTOM_OFFSET

        top_left = (delete_button_left, button_top)
        bottom_right = (delete_button_left + DELETE_BUTTON_WIDTH, button_bottom)

        cv2.rectangle(frame, top_left, bottom_right, button_color, -1)
        cv2.putText(
            frame,
            "Delete",
            (delete_button_left + 5, button_top + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            2,
        )

    def draw_timeline(self, frame):
        video_height = frame.shape[0]
        timeline_color = (255, 255, 255)

        # Calculate start and end positions based on the window size
        start_x = 20
        start_y = video_height - TIMELINE_BOTTOM_OFFSET
        end_x = start_x + TIMELINE_LENGTH

        cv2.line(frame, (start_x, start_y), (end_x, start_y), timeline_color, 2)

        # Draw timestamps from x_coordinates
        for timestamp, x_coord in self.x_coordinates.items():
            # Convert timestamp to position on the timeline
            position = (
                int(
                    (timestamp / (self.total_frames / self.fps * 1000))
                    * TIMELINE_LENGTH
                )
                + start_x
            )

            # Check if the position is within the timeline bounds
            if start_x <= position <= end_x:
                cv2.line(
                    frame,
                    (position, start_y - 10),
                    (position, start_y + 10),
                    (0, 255, 0),
                    2,
                )
                # Optional: Draw the timestamp text
                cv2.putText(
                    frame,
                    str(timestamp),
                    (position - 15, start_y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                )

        # Highlight the current position on the timeline
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        current_position = (
            int((current_frame / self.total_frames) * TIMELINE_LENGTH) + start_x
        )
        cv2.line(
            frame,
            (current_position, start_y - 10),
            (current_position, start_y + 10),
            (0, 0, 255),
            2,
        )

    def draw_line_at_x(self, frame, x_coord):
        """Draw a blue vertical line at the specified X coordinate."""
        height = frame.shape[0]
        cv2.line(frame, (x_coord, 0), (x_coord, height), (255, 0, 0), 2)

    def run(self):
        # Get video dimensions
        ret, frame = self.cap.read()
        video_height, video_width = frame.shape[:2]
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to first frame

        # Calculate new width for a 9:16 aspect ratio
        new_width = int(video_height * 9 / 16)

        # Initialize the last known X coordinate
        last_known_x_coord = None

        while self.cap.isOpened():
            if self.playing:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Get the current timestamp in milliseconds
                timestamp = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))

                # Find the closest timestamp in the dictionary
                closest_timestamp = min(
                    self.x_coordinates.keys(), key=lambda k: abs(k - timestamp)
                )

                # Update the last known X coordinate if within the threshold
                if abs(timestamp - closest_timestamp) < 100:  # 100 ms threshold
                    last_known_x_coord = self.x_coordinates[closest_timestamp]

                # Use the last known X coordinate if available
                if last_known_x_coord is not None:
                    x_coord = last_known_x_coord

                    # Calculate the viewport edges
                    left_edge = max(
                        0, min(x_coord - new_width // 2, video_width - new_width)
                    )
                    right_edge = left_edge + new_width

                    # Darken areas outside the viewport
                    frame[:, :left_edge] = frame[:, :left_edge] // 2  # Darken left side
                    frame[:, right_edge:] = (
                        frame[:, right_edge:] // 2
                    )  # Darken right side

                    # Draw vertical lines at the edges of the viewport
                    cv2.line(
                        frame, (left_edge, 0), (left_edge, video_height), (0, 255, 0), 2
                    )
                    cv2.line(
                        frame,
                        (right_edge, 0),
                        (right_edge, video_height),
                        (0, 255, 0),
                        2,
                    )

                    # Draw the blue line at the basketball's position
                    self.draw_line_at_x(frame, x_coord)

            self.draw_play_pause_button(frame)
            self.draw_add_keyframe_button(frame)
            self.draw_timeline(frame)
            self.draw_delete_keyframe_button(frame)

            cv2.imshow("Basketball Video GUI", frame)

            key = cv2.waitKey(25)
            if key == ord("q"):
                break
            elif key == ord(" "):
                self.playing = not self.playing
            elif key == ord("k") or key == ord("s"):
                self.keyframe_mode = not self.keyframe_mode
            elif key == ord("d"):
                self.delete_mode = not self.delete_mode

            if self.playing:
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 1 >= self.total_frames:
                    break
                self.cap.set(
                    cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 1
                )

        self.cap.release()
        cv2.destroyAllWindows()
