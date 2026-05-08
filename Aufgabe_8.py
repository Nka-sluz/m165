from pymongo import MongoClient
from PIL import Image, ImageDraw

client = MongoClient('mongodb://localhost:27017/')
db = client['restaurants']
neighborhoods = db['neighborhoods']

IMAGE_SIZE = (900, 900)
PADDING = 30


def get_rings(doc):
    """Return all outer rings for a document, supporting Polygon and MultiPolygon"""
    geom = doc['geometry']
    if geom['type'] == 'Polygon':
        return [geom['coordinates'][0]]
    elif geom['type'] == 'MultiPolygon':
        return [polygon[0] for polygon in geom['coordinates']]
    return []


def coords_to_pixels(ring, min_lon, max_lon, min_lat, max_lat):
    width, height = IMAGE_SIZE
    draw_w = width - 2 * PADDING
    draw_h = height - 2 * PADDING
    pixels = []
    for lon, lat in ring:
        x = PADDING + (lon - min_lon) / (max_lon - min_lon) * draw_w
        # y-axis is inverted: higher latitude = lower pixel y
        y = PADDING + (1 - (lat - min_lat) / (max_lat - min_lat)) * draw_h
        pixels.append((x, y))
    return pixels


def draw_single_polygon():
    doc = neighborhoods.find_one()
    rings = get_rings(doc)

    all_coords = [pt for ring in rings for pt in ring]
    min_lon = min(p[0] for p in all_coords)
    max_lon = max(p[0] for p in all_coords)
    min_lat = min(p[1] for p in all_coords)
    max_lat = max(p[1] for p in all_coords)

    im = Image.new("RGB", IMAGE_SIZE, color=(20, 20, 30))
    draw = ImageDraw.Draw(im)

    for ring in rings:
        pixels = coords_to_pixels(ring, min_lon, max_lon, min_lat, max_lat)
        draw.polygon(pixels, fill=(0, 80, 120), outline=(0, 220, 255))

    name = doc.get('name', 'Unknown')
    draw.text((10, 10), name, fill=(255, 255, 255))

    im.show()
    print(f"Polygon '{name}' gezeichnet.")


def draw_all_polygons():
    docs = list(neighborhoods.find())

    all_coords = [pt for doc in docs for ring in get_rings(doc) for pt in ring]
    min_lon = min(p[0] for p in all_coords)
    max_lon = max(p[0] for p in all_coords)
    min_lat = min(p[1] for p in all_coords)
    max_lat = max(p[1] for p in all_coords)

    im = Image.new("RGB", IMAGE_SIZE, color=(20, 20, 30))
    draw = ImageDraw.Draw(im)

    for doc in docs:
        for ring in get_rings(doc):
            pixels = coords_to_pixels(ring, min_lon, max_lon, min_lat, max_lat)
            draw.polygon(pixels, fill=(0, 60, 100), outline=(0, 200, 255))

    im.show()
    print(f"{len(docs)} Polygone gezeichnet")


def main():
    print("=== Neighborhoods Visualizer ===")
    print("1 - Einzelnes Polygon zeichnen")
    print("2 - Alle Polygone zeichnen")
    choice = input("Auswahl: ").strip()

    if choice == "1":
        draw_single_polygon()
    elif choice == "2":
        draw_all_polygons()
    else:
        print("Ungültige Auswahl")


if __name__ == "__main__":
    main()
