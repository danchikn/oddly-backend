import re

_PATTERNS = [
    # Google Maps: ?q=41.29,69.24 or @41.29,69.24
    re.compile(r'[?&]q=(-?\d+\.?\d*),(-?\d+\.?\d*)'),
    re.compile(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'),
    re.compile(r'/place/(-?\d+\.?\d*),(-?\d+\.?\d*)'),
    # 2GIS: ?m=69.24%2C41.29 (lng,lat) or ?m=69.24,41.29
    re.compile(r'[?&]m=(-?\d+\.?\d*)(?:%2C|,)(-?\d+\.?\d*)'),
    # Generic: two floats separated by comma in path
    re.compile(r'/(-?\d{1,3}\.\d{3,}),(-?\d{1,3}\.\d{3,})'),
]

# 2GIS uses lng,lat order in ?m= param
_LNG_LAT_PATTERNS = {3}  # index of the 2GIS ?m= pattern


def parse_coordinates(url: str) -> tuple[float, float] | None:
    for i, pattern in enumerate(_PATTERNS):
        match = pattern.search(url)
        if match:
            a, b = float(match.group(1)), float(match.group(2))
            if i in _LNG_LAT_PATTERNS:
                lat, lng = b, a
            else:
                lat, lng = a, b
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
    return None
