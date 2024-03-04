import os
from rembg import remove
from PIL import Image

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

        # Assume `remove` is a function that removes the background
        # and returns the image bytes with transparency
        output_bytes = remove(input_bytes)

        # Save the output image temporarily to process it for cropping
        temp_path = "temp_image.png"
        with open(temp_path, "wb") as temp_file:
            temp_file.write(output_bytes)

        # Crop the image to remove transparent borders
        cropped_image = self.crop_transparency(temp_path)
        
        # Save the cropped image to the final output path
        cropped_image.save(output_path, "PNG")

        print(f"Background removed and image cropped from {input_path} and saved to {output_path}")

    def crop_transparency(self, image_path):
        """
        Crops transparent borders from an image.
        """
        image = Image.open(image_path)
        image = image.convert("RGBA")

        # Find the bounding box of the non-transparent pixels
        bbox = image.getbbox()

        if bbox:
            return image.crop(bbox)
        return image  # Return the original image if no cropping is needed

    def make_image_transparent(self, input_path, output_path):
        # Check if input path is a directory
        if os.path.isdir(input_path):
            for filename in os.listdir(input_path):
                if self.is_image_file(filename):
                    input_file_path = os.path.join(input_path, filename)
                    output_file_path = os.path.join(
                        output_path, "transparent_" + os.path.splitext(filename)[0] + ".png"
                    )
                    self.process_single_image(input_file_path, output_file_path)
        else:
            self.process_single_image(input_path, output_path + ".png")

