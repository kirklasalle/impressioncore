
import os

from datasets import load_dataset


def download_faces():
    data_dir = "F:/data/raw/vision/faces"
    os.makedirs(data_dir, exist_ok=True)

    print("--------------------------------------------------")
    print("Downloading LFW (Labeled Faces in the Wild)...")
    lfw_mirrors = ["scikit-learn/lfw_pairs", "erilyth/lfw-pairs", "dalle-mini/lfw"]

    for mirror in lfw_mirrors:
        try:
            print(f"Trying mirror: {mirror}")
            dataset = load_dataset(mirror, split="train", trust_remote_code=True)
            save_path = os.path.join(data_dir, "lfw")
            dataset.save_to_disk(save_path)
            print(f"✅ LFW Downloaded to: {save_path}")
            break
        except Exception as e:
            print(f"⚠️ Failed to load {mirror}: {e}")

    print("--------------------------------------------------")
    print("Downloading CelebA...")
    celeba_mirrors = ["bencsk/celeba", "dalle-mini/celeba", "nielsr/celeba-hq"]

    for mirror in celeba_mirrors:
        try:
            print(f"Trying mirror: {mirror}")
            dataset = load_dataset(mirror, split="train", trust_remote_code=True)
            save_path = os.path.join(data_dir, "celeba")
            dataset.save_to_disk(save_path)
            print(f"✅ CelebA Downloaded to: {save_path}")
            break
        except Exception as e:
            print(f"⚠️ Failed to load {mirror}: {e}")

if __name__ == "__main__":
    download_faces()
