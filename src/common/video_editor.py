from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    ImageClip,
)
from common.utilities import json_stats_to_html_image

import traceback


class VideoEditor:
    @staticmethod
    def create_highlight_video(
        video_paths, output_path, box_score_data, image_duration=5
    ):
        """
        Creates a video from a list of video paths and adds stats as text overlay in a table format.

        Parameters:
            video_paths (list): List of paths to video files.
            output_path (str): Path to save the final video.
            box_score_data (dict): JSON object containing player statistics.
            image_duration (int): Duration for which the image is displayed.

        Returns:
            None
        """
        try:
            if len(box_score_data) > 0:
                stats_home_team_json = {
                    "players": box_score_data[0]["game"]["homeTeam"]["players"]
                }
                # Generate HTML table image from stats JSON
                stats_home_team_image_path = f"{output_path}/stats_home_team_image.png"
                json_stats_to_html_image(
                    stats_home_team_json, stats_home_team_image_path
                )

                stats_away_team_json = {
                    "players": box_score_data[0]["game"]["awayTeam"]["players"]
                }
                # Generate HTML table image from stats JSON
                stats_away_team_image_path = f"{output_path}/stats_away_team_image.png"
                json_stats_to_html_image(
                    stats_away_team_json, stats_away_team_image_path
                )

            clips = []

            # Get the intro video
            intro_clip = VideoFileClip("resources/video/intro.mp4")
            audio = AudioFileClip("resources/audio/intro.mp3").audio_fadeout(5)
            clips.append(intro_clip.set_audio(audio))

            # Process videos
            # Before processing the videos, order the paths in alphabetical order to make sure they are in the right time sequence
            video_paths.sort()
            for videopath in video_paths:
                print(f"Processing video: {videopath}")
                videofilename = videopath.split("/")[-1]
                # Keep only the ones that start with a number and and with .mp4 (These are the videos previously downloaded)
                if videofilename[0].isnumeric() and videofilename.endswith(".mp4"):
                    # Add filtered paths to clips list
                    clips.append(VideoFileClip(videopath))

            if stats_home_team_image_path and stats_away_team_image_path:
                # Create an ImageClip with the stats image
                stats_home_team_image_clip = ImageClip(
                    stats_home_team_image_path
                ).set_duration(image_duration)
                stats_away_team_image_clip = ImageClip(
                    stats_away_team_image_path
                ).set_duration(image_duration)

                # Concatenate video clips and append the image clip at the end
                final_clip = concatenate_videoclips(
                    clips + [stats_home_team_image_clip] + [stats_away_team_image_clip],
                    method="compose",
                )
            else:
                final_clip = concatenate_videoclips(clips, method="compose")

            final_clip.write_videofile(
                f"{output_path}/final_highlight.mp4", codec="libx264", fps=30
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
