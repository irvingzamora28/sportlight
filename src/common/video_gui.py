import cv2

# Constants for button coordinates
PLAY_PAUSE_BUTTON_TOP_LEFT = (20, 430)
PLAY_PAUSE_BUTTON_BOTTOM_RIGHT = (70, 480)
TIMELINE_TOP = 450
TIMELINE_BOTTOM = 500


class BasketballVideoGUI:
    def __init__(self, video_file, x_coordinates):
        self.video_file = video_file
        self.x_coordinates = x_coordinates
        self.playing = True
        self.cap = cv2.VideoCapture(video_file)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        cv2.namedWindow("Basketball Video GUI")
        cv2.setMouseCallback("Basketball Video GUI", self.mouse_callback)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if (
                PLAY_PAUSE_BUTTON_TOP_LEFT[0] <= x <= PLAY_PAUSE_BUTTON_BOTTOM_RIGHT[0]
                and PLAY_PAUSE_BUTTON_TOP_LEFT[1]
                <= y
                <= PLAY_PAUSE_BUTTON_BOTTOM_RIGHT[1]
            ):
                self.playing = not self.playing
            elif TIMELINE_TOP <= y <= TIMELINE_BOTTOM:
                clicked_frame = int(((x - 100) / 600) * self.total_frames)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, clicked_frame)

    def draw_play_pause_button(self, frame):
        button_color = (255, 255, 255)
        button_text_color = (0, 0, 0)
        if self.playing:
            button_text = "Pause"
        else:
            button_text = "Play"
        cv2.rectangle(
            frame,
            PLAY_PAUSE_BUTTON_TOP_LEFT,
            PLAY_PAUSE_BUTTON_BOTTOM_RIGHT,
            button_color,
            -1,
        )
        cv2.putText(
            frame,
            button_text,
            (PLAY_PAUSE_BUTTON_TOP_LEFT[0] + 5, PLAY_PAUSE_BUTTON_TOP_LEFT[1] + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            button_text_color,
            2,
        )

    def draw_timeline(self, frame):
        timeline_color = (255, 255, 255)
        cv2.line(frame, (100, 480), (700, 480), timeline_color, 2)

        # Draw regular timeline intervals
        for i in range(100, 701, 100):
            cv2.line(frame, (i, 470), (i, 490), timeline_color, 2)

        # Iterate through x_coordinates to draw timestamps
        for timestamp, x_coord in self.x_coordinates.items():
            # Convert timestamp to position on the timeline
            position = (
                int((timestamp / (self.total_frames / self.fps * 1000)) * 600) + 100
            )

            # Check if the position is within the timeline bounds
            if 100 <= position <= 700:
                cv2.line(frame, (position, 470), (position, 490), (0, 255, 0), 2)

                # Optional: Draw the timestamp text
                cv2.putText(
                    frame,
                    str(timestamp),
                    (position - 15, 460),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                )

        # Highlight the current position on the timeline
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        current_position = int((current_frame / self.total_frames) * 600) + 100
        cv2.line(
            frame, (current_position, 470), (current_position, 490), (0, 0, 255), 2
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
            self.draw_timeline(frame)

            cv2.imshow("Basketball Video GUI", frame)

            key = cv2.waitKey(25)
            if key == ord("q"):
                break
            elif key == ord(" "):
                self.playing = not self.playing

            if self.playing:
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 1 >= self.total_frames:
                    break
                self.cap.set(
                    cv2.CAP_PROP_POS_FRAMES, self.cap.get(cv2.CAP_PROP_POS_FRAMES) + 1
                )

        self.cap.release()
        cv2.destroyAllWindows()
