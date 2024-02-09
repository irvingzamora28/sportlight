from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    ImageClip,
)
from common.utilities import json_stats_to_html_image
import ffmpeg
import traceback
from common.logger import logger


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

            video_paths.sort()
            clips = []

            # Resize intro video to size of game clips
            sample_game_clip = VideoFileClip(video_paths[0])
            width, height = sample_game_clip.size
            logger.console(f"Width: {width}, Height: {height}")

            input_video_path = "resources/video/intro.mp4"
            output_video_path = "resources/video/intro_correct_size.mp4"

            resize_video(input_video_path, output_video_path, width, height)

            # Get the intro video
            intro_clip = VideoFileClip("resources/video/intro_correct_size.mp4")
            audio = AudioFileClip("resources/audio/intro.mp3").audio_fadeout(5)
            clips.append(intro_clip.set_audio(audio))

            # Process videos
            # Before processing the videos, order the paths in alphabetical order to make sure they are in the right time sequence
            for videopath in video_paths:
                logger.console(f"Processing video: {videopath}")
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
            logger.error(f"An error occurred: {e}")
            traceback.print_exc()


def resize_video(input_path, output_path, width, height):
    (ffmpeg.input(input_path).filter("scale", width, height).output(output_path).run())
