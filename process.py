import os
import shutil
from PIL import Image
import imagehash
import networkx as nx

def group_images_by_similarity(threshold=5):
    """
    Groups images from the 'logos' directory based on their visual similarity using a graph
    + connected components approach. Copies each group into 'groups/{group_id}'.

    Args:
        threshold (int): Maximum Hamming distance between hashes to consider images connected.

    Returns:
        dict: A dictionary where keys are group IDs and values are lists of image file paths.
    """
    logos_dir = "logos"
    groups_dir = "groups"
    os.makedirs(groups_dir, exist_ok=True)

    # Get all image paths
    image_paths = [
        os.path.join(logos_dir, f)
        for f in os.listdir(logos_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
    ]

    if not image_paths:
        print("No images found in the 'logos' directory.")
        return {}

    # Compute perceptual hashes for each image
    image_hashes = {}
    for path in image_paths:
        try:
            with Image.open(path) as img:
                image_hashes[path] = imagehash.phash(img)
        except Exception as e:
            print(f"Error processing {path}: {e}")

    # Build a graph where each image is a node
    G = nx.Graph()
    for path in image_paths:
        G.add_node(path)

    # For every pair of images, add an edge if distance < threshold
    for i in range(len(image_paths)):
        for j in range(i+1, len(image_paths)):
            path_i = image_paths[i]
            path_j = image_paths[j]
            dist = image_hashes[path_i] - image_hashes[path_j]
            if dist < threshold:
                G.add_edge(path_i, path_j)

    # Find connected components, each is a group
    groups = {}
    for idx, component in enumerate(nx.connected_components(G)):
        groups[idx] = list(component)

    # Copy images to group directories
    for gid, paths in groups.items():
        group_path = os.path.join(groups_dir, f"group_{gid}")
        os.makedirs(group_path, exist_ok=True)
        for src_path in paths:
            try:
                shutil.copy(src_path, group_path)
            except Exception as e:
                print(f"Error copying {src_path} to {group_path}: {e}")

    return groups

if __name__ == '__main__':
    clusters = group_images_by_similarity(threshold=19)
    with open("process_results.txt", "w") as f:
        for group_id, files in clusters.items():
            f.write(f"Group {group_id}:\n")
            for file_path in files:
                f.write(f"  - {file_path}\n")

