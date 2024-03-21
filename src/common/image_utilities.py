import os
from rembg import remove
from PIL import Image, ImageDraw, ImageFilter, ImageOps


class ImageUtilities:

    def __init__(self):
        """
        The constructor for ImageUtilities class.
        """

    def is_image_file(self, filename):
        return filename.lower().endswith((".png", ".jpg", ".jpeg"))

    def process_single_image(self, input_path, output_path, add_outline=False):
        with open(input_path, "rb") as input_file:
            input_bytes = input_file.read()

        # Assume `remove` is a function that removes the background
        # and returns the image bytes with transparency
        output_bytes = remove(input_bytes)

        # Save the output image temporarily to process it
        temp_path = "temp_image.png"
        with open(temp_path, "wb") as temp_file:
            temp_file.write(output_bytes)

        # Crop the image to remove transparent borders
        cropped_image = self.crop_transparency(temp_path)

        if add_outline:
            cropped_image = self.add_white_outline(cropped_image)

        # Save the final image to the output path
        cropped_image.save(output_path, "PNG")
        # Remove temp image after processing
        os.remove(temp_path)

        print(
            f"Background removed and image processed from {input_path} and saved to {output_path}"
        )

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

    def add_white_outline(self, image, outline_size=10, outline_smooth=2):
        """
        Adds a smoothed white outline that follows the contours of the image subject.
        """
        # Create a mask of the non-transparent parts of the image
        alpha = image.split()[-1]
        mask = alpha.point(lambda p: 255 if p > 0 else 0)

        # Dilate the mask to create the outline
        dilation = Image.new('L', (mask.size[0] + 2 * outline_size, mask.size[1] + 2 * outline_size), 0)
        dilation.paste(mask, (outline_size, outline_size))
        dilation = dilation.filter(ImageFilter.MaxFilter(2 * outline_size + 1))

        # Apply a blur filter to the dilated mask to smooth the edges of the outline
        blurred_dilation = dilation.filter(ImageFilter.GaussianBlur(outline_smooth))

        # Create a new image for the white outline, based on the blurred and dilated mask
        white_outline = ImageOps.colorize(blurred_dilation, 'white', 'white')
        white_outline.putalpha(blurred_dilation)

        # Create a new image to hold the original plus the outline
        combined_image = Image.new('RGBA', white_outline.size, (0, 0, 0, 0))
        
        # Paste the white outline onto the combined image
        combined_image.paste(white_outline, (0, 0), white_outline)

        # Paste the original image on top of the white outline
        combined_image.paste(image, (outline_size, outline_size), image)

        return combined_image



    def make_image_transparent(self, input_path, output_path, add_outline=False):
        # Check if input path is a directory
        if os.path.isdir(input_path):
            for filename in os.listdir(input_path):
                if self.is_image_file(filename):
                    input_file_path = os.path.join(input_path, filename)
                    output_file_path = os.path.join(
                        output_path,
                        "transparent_" + os.path.splitext(filename)[0] + ".png",
                    )
                    self.process_single_image(
                        input_file_path, output_file_path, add_outline
                    )
        else:
            self.process_single_image(input_path, output_path + ".png", add_outline)
