import os
from rembg import remove

class ImageUtilities:

    def __init__(self):
        """
        The constructor for ImageUtilities class.
        """

    def is_image_file(self, filename):
        return filename.lower().endswith((".png", ".jpg", ".jpeg"))

    def process_single_image(self, input_path, output_path):
        with open(input_path, "rb") as input_file:
            input_bytes = input_file.read()

        # Remove the background
        output_bytes = remove(input_bytes)

        # Save the output image as png
        with open(output_path, "wb") as output_file:
            output_file.write(output_bytes)

        print(f"Background removed from {input_path} and saved to {output_path}")

    def make_image_transparent(self, input_path, output_path):
        # Check if input path is a directory
        if os.path.isdir(input_path):
            for filename in os.listdir(input_path):
                if self.is_image_file(filename):
                    input_file_path = os.path.join(input_path, filename)
                    output_file_path = os.path.join(
                        output_path, "transparent_" + filename + ".png"
                    )
                    self.process_single_image(input_file_path, output_file_path)
        else:
            self.process_single_image(input_path, output_path + ".png")
