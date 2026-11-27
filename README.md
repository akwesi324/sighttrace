# 🛰️ SightTrace — Visual Forensics & Identity Mapping Suite

> **High-precision media forensics, deep learning domain classification, facial biometric analysis, and geographic coordinate mapping (down to 10m precision) for image and video assets.**

---

## ⚡ Overview

SightTrace is a Python-based visual forensics and identity intelligence platform. Operating as a dedicated forensic utility inside an OS-in-a-VM workstation environment, it analyzes images (selfies, full-frame photos, documents) and video streams across all major extensions (`.jpg`, `.png`, `.heic`, `.webp`, `.mp4`, `.mov`, `.mkv`, `.webm`) to extract minute hardware signatures, facial biometric embeddings, PyTorch deep neural representations, and high-precision geographic telemetry.

---

## 🔍 Core Capabilities

1. **PyTorch Deep Learning & Neural Domain Classification**:
   * Neural backbone utilizing `MobileNetV3` coupled with custom latent projection and domain classifier heads.
   * Generates 576-dimensional L2-normalized latent feature vectors for zero-shot forensic scene indexing.
   * Classifies environmental settings across 6 core domains: Metropolitan/Urban, Suburban/Residential, Rural/Agricultural, Coastal/Marine, Mountainous/Terrain, and Indoor Enclosures.
   * Calculates tensor energy and sparsity indices for scene complexity analysis.

2. **VM OS Forensic Workstation Interface**:
   * Styled as a dedicated forensic utility window operating on a forensic Linux VM desktop (`/dev/pts/1`).
   * Window title bar with authentic controls, system resource telemetry (RAM, CPU, swap, kernel status).
   * 4-tab investigative console:
     - **Tab 1: Satellite Radar & 10m Geo-Perimeter**: High-precision interactive map with targeting reticle and 10m pulse perimeter.
     - **Tab 2: Deep Learning Tensor & Domain**: 576-d latent feature micro-spectrum visualizer and animated 6-class domain probability bars.
     - **Tab 3: Biometrics & Facial Vectors**: Facial landmark tracking, eye detection, bounding box frame coverage, and identity comparison.
     - **Tab 4: VM Forensic Terminal**: Real-time monospace journalctl / dmesg event log stream.

3. **Hardware & EXIF Telemetry Extraction**:
   * Parses exchangeable image file format (EXIF) headers down to native sensor values.
   * Extracts camera make, model, lens profile, focal length, exposure, and ISO.
   * Resolves raw GPS degrees/minutes/seconds into signed decimal coordinates with sub-meter numerical precision.
   * Identifies 10-meter perimeter accuracy based on GPS Dilution of Precision (DOP).

4. **Full Video Keyframe Decomposition**:
   * Uniform and motion-based keyframe sampling for all video containers.
   * Temporal alignment to map visual cues across video duration.

5. **Facial Biometrics & Consented Identity Verification**:
   * Detects faces and facial landmark geometry (eye spacing, nose bridge, jawline).
   * Generates salient biometric feature vectors for verification.
   * Measures cosine similarity against reference images for consented identity verification.

6. **Minute Scene & Environmental Forensics**:
   * Difference Hashing (dHash) for duplicate detection and perceptual matching.
   * Environmental classification (Direct sunlight, diffused daylight, night/low-light, indoor).
   * Dominant color palette extraction via k-Means clustering.

---

## 🚀 Quick Start

### Installation & Cloning
```bash
git clone https://github.com/akwesi324/sighttrace.git
cd sighttrace
pip install -r requirements.txt
```

### 1. Launching the VM OS Forensic Workstation
```bash
python server.py 8085
```
Open [http://localhost:8085](http://localhost:8085) in any modern web browser to access the VM desktop forensic workstation interface.

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
sighttrace/
├── core/
│   ├── __init__.py           # Unified pipeline runner
│   ├── deep_engine.py        # PyTorch MobileNetV3 deep learning engine & domain classifier
│   ├── exif_extractor.py     # EXIF & hardware GPS parser (10m accuracy)
│   ├── video_parser.py       # Keyframe extractor for video files
│   ├── facial_analyzer.py    # Facial biometric topology & embeddings
│   ├── scene_analyzer.py     # dHash, lighting vectors & environmental cues
│   └── geocoder.py           # Reverse geocoding & Leaflet/Folium map generator
├── web/
│   ├── static/
│   │   ├── css/style.css     # VM OS forensic dark desktop theme & styles
│   │   └── js/app.js         # Tab manager, tensor visualizer & map controller
│   └── templates/
│       └── index.html        # VM desktop window forensic workstation
├── cli.py                    # Command-line interface with deep learning metrics
├── server.py                 # HTTP REST API & Web Dashboard Server
├── requirements.txt          # Dependencies (PyTorch, OpenCV, Pillow, Folium)
└── README.md                 # Project documentation
```

---

## ⚖️ Legal & Privacy Notice
This software is intended for authorized digital asset management, open-source intelligence (OSINT) research, consented identity verification, and media forensics. Users are responsible for complying with all applicable biometric privacy regulations (e.g., GDPR, BIPA, CCPA) and anti-surveillance laws in their jurisdiction.

---

<p align="center">
  <strong>© MaskedOps. All Rights Reserved.</strong>
</p>
