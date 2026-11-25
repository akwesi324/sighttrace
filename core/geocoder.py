import os
import requests
from typing import Dict, Any, Optional
import folium

class Geocoder:
    """
    Geographic Resolver and Interactive Map Generator.
    Resolves decimal coordinates to physical addresses and builds
    high-precision pinpoint maps with custom accuracy radii (e.g. 10m).
    """

    def __init__(self, cache_dir: str = "cache/maps"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.headers = {"User-Agent": "SightTrace-Forensics/1.0"}

    def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """Query OpenStreetMap Nominatim for street address."""
        result = {
            "resolved": False,
            "address": "Coordinates only (Offline/Unresolved)",
            "city": "Unknown",
            "country": "Unknown",
            "postcode": "",
            "raw": {}
        }

        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"

        try:
            resp = requests.get(url, headers=self.headers, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get("address", {})
                result["resolved"] = True
                result["address"] = data.get("display_name", "")
                result["city"] = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county", "Unknown")
                result["country"] = addr.get("country", "Unknown")
                result["postcode"] = addr.get("postcode", "")
                result["raw"] = data
        except Exception as e:
            result["error"] = str(e)

        return result

    def generate_map_html(self, lat: float, lon: float, radius_m: float = 10.0, output_name: str = "map.html") -> str:
        """Create interactive Folium map with pinpoint marker and 10m precision boundary."""
        output_path = os.path.join(self.cache_dir, output_name)

        m = folium.Map(
            location=[lat, lon],
            zoom_start=18,
            tiles="OpenStreetMap",
            max_zoom=20
        )

        # 10m Precision Radius Circle (Neon Green / Cyan)
        folium.Circle(
            radius=radius_m,
            location=[lat, lon],
            color="#00D2FF",
            weight=2,
            fill=True,
            fill_color="#00F59B",
            fill_opacity=0.25,
            popup=f"GPS Accuracy Perimeter: ±{radius_m}m"
        ).add_to(m)

        # Target Pinpoint Marker
        folium.Marker(
            location=[lat, lon],
            popup=f"Target Coordinates: {lat:.6f}, {lon:.6f}",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
        ).add_to(m)

        m.save(output_path)
        return output_path
