import os
from PIL import Image, ImageChops
import numpy as np

def remove_grey_background(image, grey_threshold=(200, 200, 200), replace_color=(255, 255, 255)):
    """
    Removes greyish background from an image and replaces it with a solid color (default: white).
    """
    data = np.array(image)
    
    # Extract RGBA channels
    red, green, blue, alpha = data.T

    # Define the grey background condition
    grey_background = (
        (red >= grey_threshold[0]) &
        (green >= grey_threshold[1]) &
        (blue >= grey_threshold[2])
    )

    # Replace grey pixels with the replacement color (white by default)
    data[..., :-1][grey_background.T] = replace_color

    # Recreate and return the new image
    return Image.fromarray(data)

def ensure_pure_white_background(image, background_color=(255, 255, 255)):
    """
    Ensures an image has a pure white background by removing transparency and replacing grey backgrounds.
    """
    # Remove grey background first
    image = remove_grey_background(image)

    # Handle transparency by compositing onto a white background
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        alpha = image.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", image.size, background_color + (255,))
        image = Image.composite(image, bg, alpha).convert("RGB")
    else:
        image = image.convert("RGB")
    return image

def trim_border(image, border_color=None):
    """
    Trims the border of an image based on the background color.
    """
    if border_color is None:
        border_color = image.getpixel((0, 0))  # Assume top-left pixel as the border color
    
    bg = Image.new(image.mode, image.size, border_color)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image

def resize_image(image, max_size):
    """
    Resizes the image so the longest side equals `max_size`, maintaining aspect ratio.
    """
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height

    if original_width > original_height:
        new_width = max_size
        new_height = int(max_size / aspect_ratio)
    else:
        new_height = max_size
        new_width = int(max_size * aspect_ratio)

    return image.resize((new_width, new_height), Image.LANCZOS)

def process_image(input_path, output_path, max_size=500, final_size=(1000, 1000), background_color=(255, 255, 255)):
    """
    Processes a single image:
    - Ensures a pure white background
    - Removes grey background
    - Trims borders
    - Resizes and centers the image in a square canvas
    - Saves it as a WEBP file
    """
    try:
        with Image.open(input_path).convert("RGBA") as img:
            # Ensure a pure white background and remove grey background
            img = ensure_pure_white_background(img, background_color)

            # Trim the border
            cropped_img = trim_border(img)

            # Resize while maintaining aspect ratio
            resized_img = resize_image(cropped_img, max_size)

            # Create a square canvas with a white background
            final_img = Image.new("RGB", final_size, background_color)

            # Center the resized image on the canvas
            x_offset = (final_size[0] - resized_img.size[0]) // 2
            y_offset = (final_size[1] - resized_img.size[1]) // 2
            final_img.paste(resized_img, (x_offset, y_offset))

            # Save the final image in WEBP format
            output_webp_path = os.path.splitext(output_path)[0] + ".webp"
            final_img.save(output_webp_path, format="WEBP", quality=85, optimize=True)
            print(f"Processed and saved: {output_webp_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def process_folder(input_folder, output_folder, max_size=500, final_size=(1000, 1000), background_color=(255, 255, 255)):
    """
    Processes all images in a folder, removes grey background, and saves the processed images.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)  # Output will be converted to .webp
            process_image(input_path, output_path, max_size, final_size, background_color)

# Folder paths (fixed to match your environment)
input_folder = "/home/dell/image/input_folder"  # Input folder
output_folder = "/home/dell/image/output_folder"  # Output folder

# Process all images in the input folder
process_folder(input_folder, output_folder)
