from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
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
            video_clips = []

            # Resize intro video to size of game clips
            sample_game_clip = VideoFileClip(video_paths[0])
            width, height = sample_game_clip.size
            logger.console(f"Width: {width}, Height: {height}")

            input_video_path = "resources/video/intro.mp4"
            output_video_path = "resources/video/intro_correct_size.mp4"

            resize(input_video_path, output_video_path, width, height)

            # Get the intro video
            intro_clip = VideoFileClip("resources/video/intro_correct_size.mp4")
            intro_audio = AudioFileClip("resources/audio/intro.mp3").audio_fadeout(5)
            outro_audio = AudioFileClip("resources/audio/outro.mp3").audio_fadeout(7)
            intro_clip = intro_clip.set_audio(intro_audio)
            video_clips.append(intro_clip)

            # Process videos
            # Before processing the videos, order the paths in alphabetical order to make sure they are in the right time sequence
            for videopath in video_paths:
                logger.console(f"Processing video: {videopath}")
                videofilename = videopath.split("/")[-1]
                # Keep only the ones that start with a number and and with .mp4 (These are the videos previously downloaded)
                if videofilename[0].isnumeric() and videofilename.endswith(".mp4"):
                    # Add filtered paths to clips list
                    video_clips.append(VideoFileClip(videopath))

            # Prepare and add image clips with outro audio
            if stats_home_team_image_path and stats_away_team_image_path:
                # Create an ImageClip with the stats image
                stats_home_team_image_clip = ImageClip(
                    stats_home_team_image_path
                ).set_duration(image_duration)
                stats_away_team_image_clip = ImageClip(
                    stats_away_team_image_path
                ).set_duration(image_duration)

                # Create composite clips for images with outro audio
                stats_home_team_video = CompositeVideoClip(
                    [stats_home_team_image_clip]
                ).set_audio(outro_audio)
                stats_away_team_video = CompositeVideoClip([stats_away_team_image_clip])
                image_clips = [stats_home_team_video, stats_away_team_video]
                video_clips += image_clips

            # Concatenate all clips
            final_video_clip = concatenate_videoclips(video_clips, method="compose")

            # Generate the logo clip
            video_size = (width, height)
            total_duration = sum(clip.duration for clip in video_clips)
            logo_clip = create_logo_clip(
                "resources/image/logo.png", video_size, total_duration
            )

            # Add the logo clip to the final composition
            final_video_clip = CompositeVideoClip([final_video_clip, logo_clip])

            # Write final video file
            final_video_clip.write_videofile(
                f"{output_path}/final_highlight_logo.mp4", codec="libx264", fps=30
            )

            # # Write final video file
            # final_video_clip.write_videofile(
            #     f"{output_path}/final_highlight.mp4", codec="libx264", fps=30
            # )
            # add_logo_to_video(
            #     f"{output_path}/final_highlight.mp4",
            #     f"{output_path}/final_highlight_logo.mp4",
            #     "resources/image/logo.png",
            # )
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            traceback.print_exc()


def resize(input_file, output_file, width, height):
    (
        ffmpeg.input(input_file)
        .filter("scale", width, height)
        .output(output_file)
        .overwrite_output()
        .run()
    )


def create_logo_clip(
    logo_path,
    video_size,
    duration,
    logo_size=(45, 45),
    padding_top=0,
    padding_right=20,
    bg_height=60,
):
    """
    Creates an ImageClip with the logo.

    Parameters:
        logo_path (str): Path to the logo image.
        video_size (tuple): Size of the video (width, height).
        duration (float): Duration of the logo clip.
        logo_size (tuple): Size of the logo (width, height).
        padding_top (int): Top padding for the logo.
        padding_right (int): Right padding for the logo.
        bg_height (int): Height of the black background.

    Returns:
        ImageClip: An ImageClip of the logo.
    """
    # Resize image to make it fit in the corner
    output_image_path = "resources/image/logo_resized.png"
    resize(logo_path, output_image_path, *logo_size)

    # Load and set the logo image
    logo = ImageClip(output_image_path)
    logo_position = (video_size[0] - logo_size[0] - padding_right, padding_top)
    logo = logo.set_position(logo_position).set_duration(duration)

    # Create black background
    bg_black = (
        TextClip(
            " "
            * 100,  # Adjust the number of spaces based on the desired width of the background
            fontsize=48,
            color="white",
            bg_color="black",
            font="Arial",
        )
        .set_duration(duration)
        .set_position(("right", "top"))
    )

    # Adjust the size of the background
    # bg_black = bg_black.set_size((logo_size[0] + padding_right, bg_height))

    # Overlay the logo on the black background
    final_logo_clip = CompositeVideoClip([bg_black, logo], size=video_size)

    return final_logo_clip


def add_logo_to_video(input_file, output_file, logo_path):
    video = VideoFileClip(input_file)

    # Create black background
    bg_black = TextClip(
        "                                                                                                                      ",
        fontsize=48,
        color="white",
        bg_color="black",
        font="Arial",
    )

    # Set the duration of the bg_black clip
    bg_black = bg_black.set_duration(video.duration)

    # Set the position of the bg_black top right
    bg_black = bg_black.set_pos(("right", "top"))

    # Resize image to make it fit in the corner
    output_image_path = "resources/image/logo_45_45.png"
    resize(logo_path, output_image_path, 45, 45)

    # Load your image
    image = ImageClip("resources/image/logo_45_45.png")

    # Set the duration of the image clip
    image = image.set_duration(video.duration)

    # Set the position of the image (top right corner)
    padding_top = 0
    padding_right = 20
    image = image.set_position(
        lambda t: (video.size[0] - image.size[0] - padding_right, padding_top)
    )

    # Overlay the text on your video
    final_video = CompositeVideoClip([video, bg_black, image])

    # Write the result to a file
    final_video.write_videofile(
        output_file,
        codec="libx264",
        fps=video.fps,
    )
