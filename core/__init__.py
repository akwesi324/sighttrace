import os
from typing import Dict, Any, List
from .exif_extractor import ExifExtractor
from .video_parser import VideoParser
from .facial_analyzer import FacialAnalyzer
from .scene_analyzer import SceneAnalyzer
from .geocoder import Geocoder

class GeoVisionPipeline:
    """
    Unified Forensics & Visual Geolocation Pipeline.
    Analyzes images (selfies, photos) and videos across all formats,
    extracts minute EXIF, sensor, and facial biometric signals,
    and maps physical coordinates with pinpoint accuracy (down to 10m).
    """

    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.3gp'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tiff', '.bmp'}

    def __init__(self):
        self.exif = ExifExtractor()
        self.video = VideoParser()
        self.facial = FacialAnalyzer()
        self.scene = SceneAnalyzer()
        self.geocoder = Geocoder()

    def process(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        _, ext = os.path.splitext(file_path.lower())
        is_video = ext in self.VIDEO_EXTENSIONS

        report: Dict[str, Any] = {
            "success": True,
            "file_name": os.path.basename(file_path),
            "file_type": "Video" if is_video else "Image",
            "file_size_bytes": os.path.getsize(file_path),
            "geolocation": {
                "has_coordinates": False,
                "coordinates": None,
                "accuracy_radius_m": None,
                "resolved_address": None,
                "map_file": None
            },
            "facial_analysis": {
                "faces_detected": 0,
                "faces": []
            },
            "scene_forensics": {},
            "device_telemetry": {},
            "timestamp": None
        }

        analysis_image = file_path

        # If video, extract keyframes first
        if is_video:
            v_res = self.video.process_video(file_path, max_keyframes=4)
            report["video_telemetry"] = {
                "fps": v_res.get("fps"),
                "duration_sec": v_res.get("duration_sec"),
                "total_frames": v_res.get("total_frames"),
                "keyframes_count": len(v_res.get("keyframes", []))
            }
            if v_res.get("keyframes"):
                # Use first primary keyframe for visual analysis
                analysis_image = v_res["keyframes"][0]["file_path"]

        # 1. EXIF and Hardware Metadata
        exif_res = self.exif.extract(file_path if not is_video else analysis_image)
        report["device_telemetry"] = exif_res.get("device", {})
        report["camera_settings"] = exif_res.get("camera_settings", {})
        report["timestamp"] = exif_res.get("timestamp")

        if exif_res.get("has_gps") and exif_res.get("coordinates"):
            coords = exif_res["coordinates"]
            lat, lon = coords["latitude"], coords["longitude"]
            radius = exif_res.get("accuracy_radius_m", 10.0)

            # Reverse geocode to address
            geo_info = self.geocoder.reverse_geocode(lat, lon)
            map_path = self.geocoder.generate_map_html(lat, lon, radius_m=radius, output_name=f"map_{os.path.basename(file_path)}.html")

            report["geolocation"] = {
                "has_coordinates": True,
                "coordinates": coords,
                "altitude_m": exif_res.get("altitude_m"),
                "accuracy_radius_m": radius,
                "resolved_address": geo_info.get("address"),
                "city": geo_info.get("city"),
                "country": geo_info.get("country"),
                "map_file": map_path
            }

        # 2. Facial Biometrics
        face_res = self.facial.detect_faces(analysis_image)
        report["facial_analysis"] = {
            "faces_detected": face_res.get("faces_detected", 0),
            "faces": face_res.get("faces", [])
        }

        # 3. Scene Forensics
        scene_res = self.scene.analyze(analysis_image)
        report["scene_forensics"] = {
            "perceptual_hash": scene_res.get("perceptual_hash"),
            "lighting_profile": scene_res.get("lighting_profile"),
            "dominant_colors": scene_res.get("dominant_colors"),
            "environment_type": scene_res.get("environment_type"),
            "sharpness_score": scene_res.get("sharpness_score")
        }

        return report
