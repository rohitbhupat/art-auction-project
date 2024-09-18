from PIL import Image
import imagehash
import os

# Folder where all the uploaded artwork images are stored
ARTWORK_FOLDER = 'path_to_artworks'

def is_duplicate_image(uploaded_image_path):
    # Calculate hash of the uploaded image
    uploaded_hash = imagehash.phash(Image.open(uploaded_image_path))

    # Iterate over all stored images in the folder to compare
    for image_file in os.listdir(ARTWORK_FOLDER):
        stored_image_path = os.path.join(ARTWORK_FOLDER, image_file)
        stored_hash = imagehash.phash(Image.open(stored_image_path))

        # If hash difference is below a threshold (e.g., 5), we consider it a duplicate
        if uploaded_hash - stored_hash < 5:
            return True

    return False
