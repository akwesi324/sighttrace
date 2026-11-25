# 🛰️ GeoVision AI — Visual Forensics & Identity Mapping Suite

> **High-precision media forensics, facial biometric analysis, and geographic coordinate mapping (down to 10m precision) for image and video assets.**

---

## ⚡ Overview

GeoVision AI is a Python-based visual forensics and identity intelligence platform. It analyzes images (selfies, full-frame photos, documents) and video streams across all major extensions (`.jpg`, `.png`, `.heic`, `.webp`, `.mp4`, `.mov`, `.mkv`, `.webm`) to extract minute hardware signatures, facial biometric embeddings, and geographic telemetry.

---

## 🔍 Core Capabilities

1. **Hardware & EXIF Telemetry Extraction**:
   * Parses exchangeable image file format (EXIF) headers down to native sensor values.
   * Extracts camera make, model, lens profile, focal length, exposure, and ISO.
   * Resolves raw GPS degrees/minutes/seconds into signed decimal coordinates with sub-meter numerical precision.
   * Identifies 10-meter perimeter accuracy based on GPS Dilution of Precision (DOP).

2. **Full Video Keyframe Decomposition**:
   * Uniform and motion-based keyframe sampling for all video containers.
   * Temporal alignment to map visual cues across video duration.

3. **Facial Biometric & Identity Verification**:
   * Detects faces and facial landmark geometry (eye spacing, nose bridge, jawline).
   * Generates 512-dimensional deep learning facial embeddings (`InceptionResnetV1` / `FaceNet`).
   * Measures cosine similarity against reference images for consented identity verification.

4. **Minute Scene & Environmental Forensics**:
   * Difference Hashing (dHash) for duplicate detection and perceptual matching.
   * Environmental classification (Direct sunlight, diffused daylight, night/low-light, indoor).
   * Vertical lighting gradient analysis to infer overhead sun vectors.
   * Dominant color palette extraction via k-Means clustering.

5. **Interactive Mapping & Reverse Geocoding**:
   * Queries OpenStreetMap Nominatim to resolve physical street addresses, city, and postal codes.
   * Generates interactive Leaflet & Folium maps rendering a high-precision 10-meter search radius around coordinates.

---

## 🚀 Quick Start

### Prerequisites
* Python 3.10+
* Installed packages: `pip install -r requirements.txt`

### 1. Launching the Web Dashboard
```bash
python server.py 8085
```
Open [http://localhost:8085](http://localhost:8085) in any modern web browser to access the drag-and-drop forensics interface and live map radar.

### 2. Command Line Interface (CLI)
```bash
# Scan a photo or video
python cli.py path/to/evidence.jpg

# Output full JSON report
python cli.py path/to/evidence.jpg --json

# Compare target against a reference face
python cli.py path/to/evidence.jpg --compare path/to/reference_face.jpg
```

---

## 📂 Project Structure

```
geovision-ai/
├── core/
│   ├── __init__.py           # Unified pipeline runner
│   ├── exif_extractor.py     # EXIF & hardware GPS parser (10m accuracy)
│   ├── video_parser.py       # Keyframe extractor for video files
│   ├── facial_analyzer.py    # Deep learning facial embeddings & comparison
│   ├── scene_analyzer.py     # dHash, lighting vectors & environmental cues
│   └── geocoder.py           # Reverse geocoding & Leaflet/Folium map generator
├── web/
│   ├── static/
│   │   ├── css/style.css     # Cyber-forensics dark interface
│   │   └── js/app.js         # Interactive upload & radar map controller
│   └── templates/
│       └── index.html        # Main dashboard interface
├── cli.py                    # Command-line interface
├── server.py                 # HTTP REST API & Web Dashboard Server
├── requirements.txt          # Dependencies
└── README.md                 # Project documentation
```

---

## ⚖️ Legal & Privacy Notice
This software is intended for authorized digital asset management, open-source intelligence (OSINT) research, consented identity verification, and media forensics. Users are responsible for complying with all applicable biometric privacy regulations (e.g., GDPR, BIPA, CCPA) and anti-surveillance laws in their jurisdiction.
