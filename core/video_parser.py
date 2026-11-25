import os
import cv2
from typing import Dict, Any, List

class VideoParser:
    """
    High-throughput video stream decoder and keyframe extractor.
    Deconstructs video containers (.mp4, .mov, .avi, .mkv, .webm) into
    timestamped high-fidelity frames for downstream facial and scene forensic analysis.
    """

    def __init__(self, output_dir: str = "cache/keyframes"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_video(self, video_path: str, max_keyframes: int = 8) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "is_video": True,
            "file_path": video_path,
            "duration_sec": 0.0,
            "fps": 0.0,
            "total_frames": 0,
            "resolution": (0, 0),
            "keyframes": [],
            "error": None
        }

        if not os.path.exists(video_path):
            info["error"] = "Video file not found"
            return info

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            info["error"] = "Failed to open video stream codec"
            return info

        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration_sec = total_frames / fps if fps > 0 else 0.0

            info["fps"] = round(fps, 2)
            info["total_frames"] = total_frames
            info["resolution"] = (width, height)
            info["duration_sec"] = round(duration_sec, 2)

            if total_frames <= 0:
                info["error"] = "Empty or corrupt video stream"
                return info

            # Compute uniform sampling intervals
            num_samples = min(max_keyframes, max(1, total_frames // 10))
            step = max(1, total_frames // num_samples)

            keyframes_list = []
            base_name = os.path.splitext(os.path.basename(video_path))[0]

            for i in range(num_samples):
                frame_idx = i * step
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp_sec = round(frame_idx / fps, 2)
                frame_filename = f"{base_name}_frame_{i:03d}_{timestamp_sec}s.jpg"
                frame_filepath = os.path.join(self.output_dir, frame_filename)

                cv2.imwrite(frame_filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 92])

                keyframes_list.append({
                    "frame_index": frame_idx,
                    "timestamp_sec": timestamp_sec,
                    "file_path": frame_filepath
                })

            info["keyframes"] = keyframes_list

        except Exception as e:
            info["error"] = str(e)
        finally:
            cap.release()

        return info
