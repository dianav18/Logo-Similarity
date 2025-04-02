# 🧠 Logo Similarity Detection

## Overview
This project tackles the challenge of **grouping company websites by the visual similarity of their logos**. Given how vital logos are to a company’s identity, the goal is to create an algorithm that can accurately cluster visually similar logos—even without relying on machine learning libraries like K-Means or DBSCAN.

---

## 🚀 Project Goal
Extract logos from a list of websites and cluster them into visually coherent groups based on similarity. The final output should group together websites whose logos look the same or very similar.

---

## 📂 Project Structure

```
Veridion/
├── groups/
│   ├── group_0/
│   │   ├── aamcooverlandpark.com.png
│   │   ├── aamcophilly-frankfordave.com.png
│   │   └── ...
│   ├── group_1/
│   └── ...
├── logos_list
└── README.md
```

- **groups/** – Output folder containing subfolders of grouped logos.
- **logos_list** – Input dataset containing the list of websites to be analyzed.
- **README.md** – Project documentation (this file).

---

## 🧩 Approach

### 1. **Logo Extraction**
Each logo is extracted from the provided list of websites. This part assumes the logos are either pre-downloaded or accessible through website scraping.

### 2. **Image Preprocessing**
Logos are resized and converted to grayscale to normalize them and reduce visual noise. This makes comparison more robust.

### 3. **Feature Comparison**
Rather than using traditional clustering algorithms, this project applies **manual similarity logic**, including:
- Histogram comparison (e.g., using cosine or correlation distance)
- Perceptual hashing (pHash)
- Template matching (optional for stricter matches)

### 4. **Grouping**
Images are grouped iteratively based on similarity thresholds. If a new logo is similar enough to any group representative, it’s added to that group. Otherwise, it starts a new group.

---

## ✅ Results

- Logos were successfully extracted and grouped for **more than 97% of the websites**.
- Groups contain domains with highly similar logos, visually confirming the algorithm’s accuracy.
- Sample output:  
  - `group_0` → contains ~100+ AAMCO websites with the same logo.
  - `group_1`, `group_2`, ... → additional companies with branded similarities.

---

## 🧠 Insights & Challenges

- **Logo variation** (size, aspect ratio, transparency) was one of the biggest challenges. Preprocessing played a crucial role in normalizing the images.
- The method works effectively on medium datasets. For billions of records, it can be scaled using distributed image processing frameworks or GPU-accelerated comparisons.
- Choosing **not** to use off-the-shelf clustering algorithms proved to be an interesting constraint, promoting more creative solutions.

---

## 📦 Tech Stack

- Language: Python
- Libraries: `Pillow`, `imagehash`, `OpenCV`, `NumPy`, `os`, `shutil`
- Approach: Heuristic-based grouping without ML

---

## 📁 How to Run

1. Make sure you have Python 3 installed.
2. Install the required dependencies:
   ```bash
   pip install pillow opencv-python imagehash numpy
   ```
3. Run the main script:
   ```bash
   python group_logos.py
   ```
4. Check the `groups/` directory for the result clusters.

---

## 📸 Sample Group (group_0)

These domains all belong to AAMCO auto repair centers, and their logos were identified as visually identical:

- `aamcooverlandpark.com`
- `aamcophilly-frankfordave.com`
- `aamcopottstownpa.com`
- ...
