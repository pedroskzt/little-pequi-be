from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

DISHES_1 = [
    "Beef Wellington",
    "Caesar Salad",
    "Chicken Parmesan",
    "Filet Mignon",
    "Fish and Chips",
    "French Onion Soup",
    "Lasagna",
    "Lobster Bisque",
    "Margherita Pizza",
    "Pad Thai",
    "Risotto",
    "Spaghetti Carbonara",
    "Sushi Platter",
    "Tiramisu",
    "Vegetable Curry"
]
DISHES_2 = [
    "Ratatouille",
    "Duck Confit",
    "Beef Bourguignon",
    "Paella",
    "Pho"
]


def create_image_file(name, ext='png', empty_image=False, mode='RGB', size=(64, 64),
                      **kwargs) -> SimpleUploadedFile:
    """
        Helper function to create a simple test image file.
    :param name: Image file name with extension. Example: 'test_image.png'
    :param ext: File extension. Default: 'png'. Example: 'png' or 'jpg'
    :param empty_image: True if the image file should be empty. Default: False
    :param mode: Image mode. Default: 'RGB'. Example: 'RGB' or 'L'
    :param size: Image size. Default: (64, 64). Example: (128, 128) or (256, 256)
    :return:
        SimpleUploadedFile: An instance of SimpleUploadedFile with the image file content.
    """

    in_memory_image = BytesIO()

    image = Image.new(mode=mode, size=size, **kwargs)
    image.save(in_memory_image, format=ext)

    content = in_memory_image.getvalue() if not empty_image else b''

    # Simulates an image upload with the testing image.
    image = SimpleUploadedFile(
        name=name,
        content=content,
        content_type=f'image/{ext}'
    )
    return image
