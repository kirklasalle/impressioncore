
import os

import gdown


def download_celeba_user_link():
    # User provided link: https://drive.google.com/drive/folders/0B7EVK8r0v71pWEZsZE9oNnFzTm8?resourcekey=0-5BR16BdXnb8hVj6CNHKzLg
    # This is likely the "CelebA" root folder or subfolder.
    # We will try to download the folder using gdown folder support.

    url = "https://drive.google.com/drive/folders/0B7EVK8r0v71pWEZsZE9oNnFzTm8?resourcekey=0-5BR16BdXnb8hVj6CNHKzLg"
    output_dir = "F:/data/raw/vision/faces/celeba_download"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Attempting to download CelebA from user link: {url}")
    print(f"Output directory: {output_dir}")

    try:
        gdown.download_folder(url, output=output_dir, quiet=False, use_cookies=False)
        print("✅ Download completed.")
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    download_celeba_user_link()
