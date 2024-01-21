from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
)
import traceback


class VideoEditor:
    @staticmethod
    def create_highlight_video(video_paths, output_path, stats_texts, text_duration=5):
        """
        Creates a video from a list of video paths and adds stats as text overlay.

        Parameters:
            video_paths (list): List of paths to video files.
            output_path (str): Path to save the final video.
            stats_texts (list): List of stats
            text_duration (int): Duration for which each text is displayed.

        Returns:
            None
        """
        try:
            clips = []
            for i, video_path in enumerate(video_paths):
                print(video_path)
                clip = VideoFileClip(video_path)
                txt_clip = TextClip(stats_texts[0], fontsize=24, color="white")
                txt_clip = txt_clip.set_position(("center", "bottom")).set_duration(
                    text_duration
                )
                video = CompositeVideoClip(
                    [clip, txt_clip]
                )  # Overlay text on the video
                clips.append(video)

            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec="libx264", fps=24)
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
