import os
import cv2
import numpy as np
from typing import Dict, Any, List

class SceneAnalyzer:
    """
    Environmental and visual forensics analyzer.
    Extracts minute scene clues: lighting vector, color temperature,
    perceptual hashes, and ambient environment classification.
    """

    def analyze(self, image_path: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "perceptual_hash": None,
            "lighting_profile": {},
            "dominant_colors": [],
            "environment_type": "Unknown",
            "sharpness_score": 0.0,
            "error": None
        }

        if not os.path.exists(image_path):
            result["error"] = "File not found"
            return result

        img = cv2.imread(image_path)
        if img is None:
            result["error"] = "Failed to load image"
            return result

        h, w = img.shape[:2]

        # 1. Perceptual Hash (Difference Hash - dHash)
        resized_gray = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (9, 8))
        diff = resized_gray[:, 1:] > resized_gray[:, :-1]
        dhash_val = sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])
        result["perceptual_hash"] = f"{dhash_val:016x}"

        # 2. Sharpness Score (Blur Detection)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        result["sharpness_score"] = round(lap_var, 2)

        # 3. Lighting & Brightness Profile
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        mean_brightness = float(np.mean(v_channel))
        std_brightness = float(np.std(v_channel))

        # Vertical lighting gradient (Sun overhead vs ground reflection)
        top_half = np.mean(v_channel[:h//2, :])
        bottom_half = np.mean(v_channel[h//2:, :])
        lighting_ratio = round(float(top_half / (bottom_half + 1e-5)), 2)

        result["lighting_profile"] = {
            "mean_brightness": round(mean_brightness, 1),
            "contrast_deviation": round(std_brightness, 1),
            "overhead_bias_ratio": lighting_ratio,
            "condition": "High Contrast / Direct Sunlight" if std_brightness > 65 else "Diffused / Overcast"
        }

        # 4. Dominant Colors (k-Means clustering)
        try:
            pixels = img.reshape(-1, 3).astype(np.float32)
            # Sample subset for speed
            sample_idx = np.random.choice(pixels.shape[0], min(5000, pixels.shape[0]), replace=False)
            sample_pixels = pixels[sample_idx]

            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(sample_pixels, 3, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

            dominant = []
            for c in centers:
                b, g, r = [int(val) for val in c]
                hex_code = f"#{r:02x}{g:02x}{b:02x}"
                dominant.append({"hex": hex_code, "rgb": [r, g, b]})
            result["dominant_colors"] = dominant
        except Exception:
            pass

        # 5. Environment Classification
        if mean_brightness < 45:
            env = "Night / Low-Light Environment"
        elif lighting_ratio > 1.35 and mean_brightness > 120:
            env = "Outdoor Daylight (Overhead Sun)"
        elif 80 <= mean_brightness <= 170 and std_brightness < 45:
            env = "Indoor Controlled Lighting"
        else:
            env = "Ambient Daylight"

        result["environment_type"] = env
        return result
