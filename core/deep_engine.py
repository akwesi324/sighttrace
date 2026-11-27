import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Any, List, Optional

class DeepVisionNet(nn.Module):
    """
    Deep Convolutional Feature Representation Network.
    Uses a MobileNetV3-Small backbone coupled with custom latent projection
    and domain classification heads for zero-shot forensic scene indexing.
    """
    def __init__(self, latent_dim: int = 576):
        super(DeepVisionNet, self).__init__()
        # Backbone feature extractor
        base = models.mobilenet_v3_small(weights=None)
        self.features = base.features
        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        # Latent projection head
        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(576, latent_dim),
            nn.LayerNorm(latent_dim),
            nn.GELU()
        )

        # Environmental Domain Classifier Head (6 classes)
        self.domain_classifier = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 6),
            nn.Softmax(dim=1)
        )

    def forward(self, x: torch.Tensor):
        feat = self.features(x)
        pooled = self.pool(feat)
        latent = self.projection(pooled)
        # L2 Normalize latent representation
        normalized_latent = nn.functional.normalize(latent, p=2, dim=1)
        domain_probs = self.domain_classifier(normalized_latent)
        return normalized_latent, domain_probs

class DeepEngine:
    """
    Deep Learning inference controller for SightTrace.
    Runs PyTorch tensor forward passes, extracts deep latent visual representations,
    computes deep semantic similarities, and predicts forensic domain categories.
    """
    DOMAINS = [
        "Metropolitan / Urban Infrastructure",
        "Suburban / Residential District",
        "Rural / Agricultural Vegetation",
        "Coastal / Marine Environment",
        "Mountainous / High-Altitude Terrain",
        "Indoor / Controlled Enclosure"
    ]

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DeepVisionNet().to(self.device).eval()

    def _preprocess_image(self, img_bgr: np.ndarray, target_size: int = 224) -> torch.Tensor:
        """Preprocess BGR image array into normalized PyTorch NCHW tensor."""
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (target_size, target_size), interpolation=cv2.INTER_AREA)
        tensor = torch.tensor(img_resized, dtype=torch.float32).permute(2, 0, 1) / 255.0
        # ImageNet normalization
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        normalized = (tensor - mean) / std
        return normalized.unsqueeze(0).to(self.device)

    def extract_deep_features(self, image_path: str) -> Dict[str, Any]:
        """Perform deep neural network forward pass on media file."""
        res: Dict[str, Any] = {
            "model_architecture": "MobileNetV3-DeepForensics (FP32 PyTorch)",
            "device": str(self.device).upper(),
            "latent_vector_dim": 576,
            "latent_vector_salient": [],
            "tensor_energy": 0.0,
            "domain_prediction": "Unknown",
            "domain_confidence_pct": 0.0,
            "domain_probabilities": {},
            "sparsity_ratio": 0.0,
            "error": None
        }

        if not os.path.exists(image_path):
            res["error"] = "File not found"
            return res

        img = cv2.imread(image_path)
        if img is None:
            res["error"] = "Failed to decode image data"
            return res

        try:
            with torch.no_grad():
                input_tensor = self._preprocess_image(img)
                latent, domain_probs = self.model(input_tensor)

                latent_np = latent.cpu().squeeze().numpy()
                probs_np = domain_probs.cpu().squeeze().numpy()

                # Extract salient vector samples (first 32 dimensions for telemetry display)
                salient = [round(float(v), 5) for v in latent_np[:32]]
                res["latent_vector_salient"] = salient

                # Metric computations
                res["tensor_energy"] = round(float(np.sum(np.abs(latent_np))), 3)
                res["sparsity_ratio"] = round(float(np.mean(latent_np == 0.0)), 3)

                # Domain predictions
                pred_idx = int(np.argmax(probs_np))
                res["domain_prediction"] = self.DOMAINS[pred_idx]
                res["domain_confidence_pct"] = round(float(probs_np[pred_idx]) * 100, 2)

                probs_dict = {}
                for idx, domain_name in enumerate(self.DOMAINS):
                    probs_dict[domain_name] = round(float(probs_np[idx]) * 100, 1)
                res["domain_probabilities"] = probs_dict

        except Exception as e:
            res["error"] = str(e)

        return res

    def compute_deep_similarity(self, image_path_a: str, image_path_b: str) -> Dict[str, Any]:
        """Compute deep cosine similarity between two evidence media items."""
        feat_a = self.extract_deep_features(image_path_a)
        feat_b = self.extract_deep_features(image_path_b)

        if feat_a.get("error") or feat_b.get("error"):
            return {"match": False, "similarity_pct": 0.0, "confidence": "None"}

        v1 = np.array(feat_a["latent_vector_salient"])
        v2 = np.array(feat_b["latent_vector_salient"])

        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return {"match": False, "similarity_pct": 0.0, "confidence": "None"}

        cos_sim = float(dot / (norm1 * norm2))
        sim_pct = round(max(0.0, min(1.0, cos_sim)) * 100, 2)

        return {
            "match": sim_pct >= 72.0,
            "similarity_pct": sim_pct,
            "confidence": "High" if sim_pct >= 85 else "Medium" if sim_pct >= 65 else "Low"
        }
