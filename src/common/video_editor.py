from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    ImageClip,
    vfx,
)
from common.utilities import json_stats_to_html_image
import ffmpeg
import traceback
import numpy as np
from common.logger import logger

MAX_DURATION = 8  # Maximum duration of each clip in seconds


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
                    video_clip = trim_clip(videopath, MAX_DURATION)
                    video_clips.append(video_clip)

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

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            traceback.print_exc()

    @staticmethod
    def edit_video(video_path, output_path):
        # Load your video
        clip = VideoFileClip(video_path)

        # Example ball positions with time (milliseconds)
        # Format: {time_in_milliseconds: x_coordinate, ...}
        ball_positions = {
            0: 500,
            3000: 105,  # 1 second
            3000: 750,  # 3 seconds
            6000: 450,  # 6 seconds
            # ... more time points (in milliseconds) and their corresponding x-coordinates
        }

        # Calculate the new width for a 9:16 aspect ratio
        new_width = int(clip.size[1] * 9 / 16)

        # Apply horizontal panning effect with smooth motion
        panned_clip = horizontal_pan_with_smooth_motion(clip, ball_positions, new_width)

        # Export the video with the panning effect
        panned_clip.write_videofile(output_path, codec="libx264", fps=24)


def horizontal_pan(clip, start_x, end_x, new_width):
    # This function returns a new clip with horizontal panning
    def make_frame(t):
        # Calculate the current x position for cropping
        current_x = start_x + (end_x - start_x) * t / clip.duration

        # Ensure the position stays within bounds
        current_x = max(0, min(current_x, clip.size[0] - new_width))

        # Crop and return the frame
        return clip.crop(
            x1=current_x, y1=0, x2=current_x + new_width, y2=clip.size[1]
        ).get_frame(t)

    # Create a new clip with the modified frames
    new_clip = clip.fl(lambda gf, t: make_frame(t))
    return new_clip


def horizontal_pan_with_smooth_motion(
    clip, ball_positions, new_width, ease_factor=0.05
):
    # Convert ball_positions to arrays for interpolation
    times = np.array(list(ball_positions.keys()))
    positions = np.array([ball_positions[t] for t in times])

    # Current position of the camera
    current_camera_x = 0

    # This function applies a horizontal panning effect based on the ball's position
    def make_frame(t):
        nonlocal current_camera_x

        # Convert t to milliseconds
        t_milliseconds = t * 1000

        # Interpolate to find the ball's position at time t
        target_x = np.interp(t_milliseconds, times, positions)

        # Smoothly adjust the camera's position towards the target
        # using an easing factor for gradual movement
        current_camera_x += (target_x - current_camera_x) * ease_factor

        # Calculate the left x-coordinate of the cropping area
        # so that the ball is centered
        current_x = max(
            0, min(current_camera_x - new_width // 2, clip.size[0] - new_width)
        )

        # Crop and return the frame
        return clip.crop(
            x1=current_x, y1=0, x2=current_x + new_width, y2=clip.size[1]
        ).get_frame(t)

    # Create a new clip with the modified frames
    new_clip = clip.fl(lambda gf, t: make_frame(t))
    return new_clip


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
            " " * 100,
            fontsize=48,
            color="white",
            bg_color="black",
            font="Arial",
        )
        .set_duration(duration)
        .set_position(("right", "top"))
    )

    # Overlay the logo on the black background
    final_logo_clip = CompositeVideoClip([bg_black, logo], size=video_size)

    return final_logo_clip


def trim_clip(videopath, max_duration):
    """
    Trims a video clip to a specified maximum duration from the end.

    Parameters:
        videopath (str): Path to the video file.
        max_duration (int): Maximum duration of the trimmed video clip in seconds.

    Returns:
        VideoFileClip: A trimmed video clip.
    """
    video_clip = VideoFileClip(videopath)

    # Trim 1 seconds from the end if the clip is longer than max_duration
    if video_clip.duration > 1:
        video_clip = video_clip.subclip(0, video_clip.duration - 1)

    # If the clip is still longer than max_duration, trim the beginning
    if video_clip.duration > max_duration:
        start_time = video_clip.duration - max_duration
        video_clip = video_clip.subclip(start_time, video_clip.duration)

    return video_clip
