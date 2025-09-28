import os
from PIL import Image
import imagehash

def remove_duplicate_frames(input_folder, output_folder, hash_size=8, hash_threshold=5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Dictionary to store hashes
    unique_thumbnails = []
    hashes = {}
    hash_list = []
    
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):
            try:
                # Open image and compute hash
                image = Image.open(file_path)
                img_hash = imagehash.average_hash(image, hash_size)
                
                # Check if hash is similar to existing hashes
                is_duplicate = False
                for existing_hash, _ in hashes.items():
                    if abs(img_hash - existing_hash) <= hash_threshold:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    # Store hash and save unique image
                    hashes[img_hash] = filename
                    output_image_path = os.path.join(output_folder, filename)
                    image.save(output_image_path)
                    unique_thumbnails.append(filename)
                    print(f"Saved unique image: {filename}")
                else:
                    print(f"Removed duplicate image: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return unique_thumbnails
# # Example usage
# input_frames_dir = "downloads/filtered_faces"
# output_unique_frames_dir = "downloads/filtered_duplicates"

# remove_duplicate_frames(input_frames_dir, output_unique_frames_dir, hash_size=7, hash_threshold=4)


