import os
import random
from PIL import Image, ImageDraw, ImageFont

class ImageThumbnailCreator:
    def __init__(self, team1_name, team2_name, player1, player2, team1_score, team2_score):
        self.team1_name = team1_name
        self.team2_name = team2_name
        self.team1_score = team1_score
        self.team2_score = team2_score

        # Fixed attributes
        self.background_image_path = 'resources/image/black-smoke.jpg'
        self.font_path = self._find_font_path()
        self.thumbnail_width = 1280
        self.thumbnail_height = 720
        self.half_width = self.thumbnail_width // 2

        # Load images
        self.player1_image = self._load_random_image(team1_name.lower(), os.path.join(player1))
        self.player2_image = self._load_random_image(team2_name.lower(), os.path.join(player2))
        self.team1_logo = Image.open(f"resources/image/nba/{team1_name.lower()}/logo.png")
        self.team2_logo = Image.open(f"resources/image/nba/{team2_name.lower()}/logo.png")

        # Prepare thumbnail
        self.thumbnail = self._prepare_thumbnail()
        self._add_team_logos()
        self._add_players()
        self._add_text()

    def _find_font_path(self):
        path = "resources/fonts/MutantAcademyBB.ttf"
        if os.path.exists(path):
            return path
        raise FileNotFoundError("Arial font not found in expected locations.")

    def _load_random_image(self, team_name, player_name):
        directory = f"resources/image/nba/{team_name}/{player_name.lower()}"
        images = os.listdir(directory)
        return Image.open(os.path.join(directory, random.choice(images)))

    def _prepare_thumbnail(self):
        background_image = Image.open(self.background_image_path).resize((self.thumbnail_width, self.thumbnail_height))
        return background_image

    def _resize_and_convert_logo(self, logo, width=800, height=800, alpha=0.5):
        resized_logo = logo.resize((width, height)).convert("RGBA")
        alpha_channel = resized_logo.split()[3].point(lambda p: p * alpha)
        resized_logo.putalpha(alpha_channel)
        return resized_logo

    def _add_team_logos(self):
        team1_logo = self._resize_and_convert_logo(self.team1_logo)
        team2_logo = self._resize_and_convert_logo(self.team2_logo)
        team1_position = (self.thumbnail_width // 4 - 400, self.thumbnail_height // 2 - 400)
        team2_position = (3 * self.thumbnail_width // 4 - 400, self.thumbnail_height // 2 - 400)
        self.thumbnail.paste(team1_logo, team1_position, team1_logo)
        self.thumbnail.paste(team2_logo, team2_position, team2_logo)

    def _add_players(self):
        player1_resized, player1_position = self._resize_and_center(self.player1_image, self.half_width, self.thumbnail_height)
        player2_resized, player2_position = self._resize_and_center(self.player2_image, self.half_width, self.thumbnail_height)
        player2_position = (player2_position[0] + self.half_width, player2_position[1])
        self.thumbnail.paste(player1_resized, player1_position, player1_resized)
        self.thumbnail.paste(player2_resized, player2_position, player2_resized)

    def _add_text(self):
        draw = ImageDraw.Draw(self.thumbnail)
        
        # Draw "vs" text
        vs_font = ImageFont.truetype(self.font_path, 300)
        self._draw_shadowed_text(draw, "vs", self.thumbnail_width // 2, self.thumbnail_height // 8, vs_font)

        # Draw team names
        team_name_font = ImageFont.truetype(self.font_path, 300)
        self._draw_shadowed_text(draw, self.team1_name, self.thumbnail_width // 4, self.thumbnail_height - 380, team_name_font, center=True)
        self._draw_shadowed_text(draw, self.team2_name, 3 * self.thumbnail_width // 4, self.thumbnail_height - 380, team_name_font, center=True)

        # Draw team scores
        score_font = ImageFont.truetype(self.font_path, 120)
        self._draw_shadowed_text(draw, self.team1_score, self.thumbnail_width // 4, self.thumbnail_height - 130, score_font, center=True)
        self._draw_shadowed_text(draw, self.team2_score, 3 * self.thumbnail_width // 4, self.thumbnail_height - 130, score_font, center=True)

    def _draw_shadowed_text(self, draw, text, center_x, position_y, font, center=False):
        shadow_offset = (8, 8)
        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        if center:
            # Center the text if required
            text_position = ((self.thumbnail_width // 2 - text_width) // 2 + (center_x - self.thumbnail_width // 4), position_y)
        else:
            # Calculate position based on provided center_x and position_y
            text_position = (center_x - text_width // 2, position_y)
        shadow_position = (text_position[0] + shadow_offset[0], text_position[1] + shadow_offset[1])
        
        # Draw shadow
        draw.text(shadow_position, text, fill="black", font=font)
        # Draw text
        draw.text(text_position, text, fill="white", font=font)


    def _resize_and_center(self, image, target_width, target_height):
        original_width, original_height = image.size
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        center_x = (target_width - new_width) // 2
        center_y = target_height - new_height
        return resized_image, (center_x, center_y)

    def save(self, filename="nba_highlight_thumbnail.png"):
        self.thumbnail.save(filename)