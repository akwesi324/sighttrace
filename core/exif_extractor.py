import os
import math
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags

class ExifExtractor:
    """
    Forensics-grade EXIF metadata and GPS coordinate parser.
    Converts raw hardware tags into normalized geographic coordinates,
    timestamps, and camera equipment telemetry.
    """

    def __init__(self):
        self.gps_tag_map = {
            ExifTags.GPSTAGS.get(t, t): t for t in ExifTags.GPSTAGS
        }

    def _convert_dms_to_decimal(self, dms_tuple, ref: str) -> Optional[float]:
        """Convert Degrees/Minutes/Seconds tuple to signed decimal degrees."""
        try:
            # Handle float or rational numbers
            deg = float(dms_tuple[0])
            minute = float(dms_tuple[1])
            sec = float(dms_tuple[2])

            decimal = deg + (minute / 60.0) + (sec / 3600.0)
            if ref in ['S', 'W', 's', 'w']:
                decimal = -decimal
            return round(decimal, 7)
        except Exception:
            return None

    def extract(self, file_path: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "has_exif": False,
            "has_gps": False,
            "coordinates": None,
            "altitude_m": None,
            "accuracy_radius_m": None,
            "timestamp": None,
            "device": {},
            "camera_settings": {},
            "raw_tags_count": 0
        }

        if not os.path.exists(file_path):
            result["error"] = "File does not exist"
            return result

        try:
            with Image.open(file_path) as img:
                exif_data = img.getexif()
                if not exif_data:
                    return result

                result["has_exif"] = True
                result["raw_tags_count"] = len(exif_data)

                # Parse standard EXIF tags
                device_info = {}
                settings = {}

                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    val_str = str(value).strip().replace('\x00', '')

                    if tag_name in ['Make', 'Model', 'Software', 'HostComputer']:
                        device_info[tag_name] = val_str
                    elif tag_name in ['LensModel', 'FocalLength', 'FNumber', 'ExposureTime', 'ISOSpeedRatings']:
                        settings[tag_name] = val_str
                    elif tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        if not result["timestamp"]:
                            result["timestamp"] = val_str

                # Inspect IFD GPS dictionary
                gps_ifd = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
                if gps_ifd:
                    gps_parsed = {}
                    for k, v in gps_ifd.items():
                        k_name = ExifTags.GPSTAGS.get(k, str(k))
                        gps_parsed[k_name] = v

                    lat_raw = gps_parsed.get('GPSLatitude')
                    lat_ref = gps_parsed.get('GPSLatitudeRef', 'N')
                    lon_raw = gps_parsed.get('GPSLongitude')
                    lon_ref = gps_parsed.get('GPSLongitudeRef', 'E')

                    if lat_raw and lon_raw:
                        lat = self._convert_dms_to_decimal(lat_raw, lat_ref)
                        lon = self._convert_dms_to_decimal(lon_raw, lon_ref)

                        if lat is not None and lon is not None:
                            result["has_gps"] = True
                            result["coordinates"] = {
                                "latitude": lat,
                                "longitude": lon,
                                "latitude_ref": lat_ref,
                                "longitude_ref": lon_ref
                            }

                            # Altitude
                            alt_raw = gps_parsed.get('GPSAltitude')
                            if alt_raw:
                                try:
                                    result["altitude_m"] = round(float(alt_raw), 2)
                                except Exception:
                                    pass

                            # Accuracy radius (DOP / Horizontal Positioning Error)
                            dop_raw = gps_parsed.get('GPSDOP')
                            if dop_raw:
                                try:
                                    # HDOP * standard baseline (typically 5m baseline)
                                    result["accuracy_radius_m"] = round(float(dop_raw) * 5.0, 1)
                                except Exception:
                                    result["accuracy_radius_m"] = 10.0
                            else:
                                # Standard high-precision consumer smartphone GPS radius
                                result["accuracy_radius_m"] = 8.5

                    # GPS Date/Time Stamp
                    gps_date = gps_parsed.get('GPSDateStamp')
                    gps_time = gps_parsed.get('GPSTimeStamp')
                    if gps_date and gps_time:
                        try:
                            h, m, s = [int(float(x)) for x in gps_time]
                            result["timestamp"] = f"{gps_date} {h:02d}:{m:02d}:{s:02d} UTC"
                        except Exception:
                            pass

                result["device"] = device_info
                result["camera_settings"] = settings

        except Exception as err:
            result["error"] = str(err)

        return result
