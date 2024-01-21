from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
)
import traceback


class VideoEditor:
    @staticmethod
    def format_stats_to_table(stats_json):
        """
        Formats player statistics JSON into a table-like string.

        Parameters:
            stats_json (dict): JSON object containing player statistics.

        Returns:
            str: Formatted table string.
        """
        header = "Name\tMins\tPts\tReb\tAst\tStl\tBlk\tTO\n"
        lines = [header]
        for player in stats_json["players"]:
            line = (
                f"{player['nameI']}\t"
                f"{player['statistics']['minutes']}\t"
                f"{player['statistics']['points']}\t"
                f"{player['statistics']['reboundsTotal']}\t"
                f"{player['statistics']['assists']}\t"
                f"{player['statistics']['steals']}\t"
                f"{player['statistics']['blocks']}\t"
                f"{player['statistics']['turnovers']}\n"
            )
            lines.append(line)
        return "".join(lines)

    @staticmethod
    def create_highlight_video(video_paths, output_path, stats_json, text_duration=5):
        """
        Creates a video from a list of video paths and adds stats as text overlay in a table format.

        Parameters:
            video_paths (list): List of paths to video files.
            output_path (str): Path to save the final video.
            stats_json (dict): JSON object containing player statistics.
            text_duration (int): Duration for which each text is displayed.

        Returns:
            None
        """
        try:
            formatted_stats = VideoEditor.format_stats_to_table(stats_json)
            clips = []
            for video_path in video_paths:
                clip = VideoFileClip(video_path)
                txt_clip = TextClip(
                    formatted_stats, fontsize=64, color="white", method="label"
                )
                txt_clip = txt_clip.set_position(("center", "center")).set_duration(
                    text_duration
                )
                video = CompositeVideoClip([clip, txt_clip])
                clips.append(video)

            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec="libx264", fps=24)
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
