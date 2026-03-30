
import os

import gdown


def download_celeba_direct():
    output_dir = "F:/data/raw/vision/faces/celeba"
    os.makedirs(output_dir, exist_ok=True)

    # Known ID for img_align_celeba.zip
    file_id = "0B7EVK8r0v71pZjFTYXZWM3FlRnM"
    url = f"https://drive.google.com/uc?id={file_id}"
    output_file = os.path.join(output_dir, "img_align_celeba.zip")

    print(f"Attempting valid file ID download: {file_id}")
    try:
        gdown.download(url, output_file, quiet=False)
        print("✅ Download successful!")
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    download_celeba_direct()
