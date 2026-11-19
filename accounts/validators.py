"""Validation shared by every place a person's photo can be uploaded."""
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_profile_image(file):
    """
    Accept a JPEG, PNG or WebP up to 5 MB that Pillow can actually decode.
    Checking the real file content (not only the declared content-type) stops
    renamed non-image files being stored.
    """
    if file is None:
        return file
    if file.size > MAX_IMAGE_BYTES:
        raise ValidationError("Image must be 5 MB or smaller.")
    try:
        file.seek(0)
        with Image.open(file) as image:
            image_format = image.format
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise ValidationError("Upload a valid image file (JPEG, PNG or WebP).")
    finally:
        file.seek(0)
    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Upload a JPEG, PNG or WebP image.")
    return file
