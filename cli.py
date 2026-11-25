import os
import sys
import json
import argparse
from core import SightTracePipeline

def main():
    parser = argparse.ArgumentParser(description="SightTrace — Visual Forensics & Geolocation Command Line Tool")
    parser.add_argument("file", help="Path to evidence image or video file")
    parser.add_argument("--json", action="store_true", help="Output pure JSON format")
    parser.add_argument("--compare", help="Optional reference face image to match against", default=None)

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[!] File not found: {args.file}")
        sys.exit(1)

    pipeline = SightTracePipeline()
    report = pipeline.process(args.file)

    if args.compare and os.path.exists(args.compare):
        ref_faces = pipeline.facial.detect_faces(args.compare)
        if ref_faces.get("faces") and report.get("facial_analysis", {}).get("faces"):
            match_res = pipeline.facial.compare_faces(
                report["facial_analysis"]["faces"][0]["embedding"],
                ref_faces["faces"][0]["embedding"]
            )
            report["identity_match"] = match_res

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=" * 60)
    print(" 🛰️  SIGHTTRACE FORENSICS REPORT")
    print("=" * 60)
    print(f" Target File       : {report['file_name']} ({report['file_type']})")
    print(f" Timestamp         : {report.get('timestamp') or 'None'}")
    
    dev = report.get('device_telemetry', {})
    if dev:
        print(f" Camera Hardware   : {dev.get('Make', '')} {dev.get('Model', '')} ({dev.get('Software', '')})")

    geo = report.get('geolocation', {})
    print("-" * 60)
    if geo.get('has_coordinates'):
        coords = geo['coordinates']
        print(f" [✓] GPS RESOLVED  : {coords['latitude']:.6f}° {coords['latitude_ref']}, {coords['longitude']:.6f}° {coords['longitude_ref']}")
        print(f" Precision Radius  : ±{geo.get('accuracy_radius_m', 10.0)} meters")
        print(f" Physical Address  : {geo.get('resolved_address')}")
        if geo.get('map_file'):
            print(f" Interactive Map   : {geo['map_file']}")
    else:
        print(" [X] GPS RESOLVED  : None (Hardware coordinates absent/stripped)")

    face = report.get('facial_analysis', {})
    print("-" * 60)
    print(f" Faces Detected    : {face.get('faces_detected', 0)}")
    for f in face.get('faces', []):
        print(f"   Subject #{f['face_id']}: Coverage {f['face_area_pct']}%, Sharpness {f['sharpness_score']}")

    if "identity_match" in report:
        im = report["identity_match"]
        print(f" Identity Match    : {im['similarity_pct']}% similarity ({im['confidence']} Confidence)")

    scene = report.get('scene_forensics', {})
    print("-" * 60)
    print(f" Environment       : {scene.get('environment_type')}")
    print(f" Perceptual dHash  : {scene.get('perceptual_hash')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
