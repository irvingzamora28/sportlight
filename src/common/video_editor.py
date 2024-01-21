from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip
from common.utilities import json_stats_to_html_image

import traceback


class VideoEditor:
    @staticmethod
    def create_highlight_video(video_paths, output_path, stats_json, image_duration=5):
        """
        Creates a video from a list of video paths and adds stats as text overlay in a table format.

        Parameters:
            video_paths (list): List of paths to video files.
            output_path (str): Path to save the final video.
            stats_json (dict): JSON object containing player statistics.
            image_duration (int): Duration for which the image is displayed.

        Returns:
            None
        """
        try:
            # Generate HTML table image from stats JSON
            stats_image_path = "stats_image.png"
            json_stats_to_html_image(stats_json, stats_image_path)

            # Process videos
            clips = [VideoFileClip(video_path) for video_path in video_paths]

            # Create an ImageClip with the stats image
            stats_image_clip = ImageClip(stats_image_path).set_duration(image_duration)

            # Concatenate video clips and append the image clip at the end
            final_clip = concatenate_videoclips(
                clips + [stats_image_clip], method="compose"
            )
            final_clip.write_videofile(output_path, codec="libx264", fps=24)
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
