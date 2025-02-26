from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        metadata = {}

        if exif_data is not None:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                metadata[tag_name] = value

            # Extração de dados GPS
            if "GPSInfo" in metadata:
                gps_info = {}
                for key in metadata["GPSInfo"].keys():
                    gps_tag = GPSTAGS.get(key, key)
                    gps_info[gps_tag] = metadata["GPSInfo"][key]
                metadata["GPSInfo"] = gps_info
        
        return metadata
    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return {}

def display_metadata(metadata):
    for tag, value in metadata.items():
        print(f"{tag}: {value}")
    
    # Exibir localização se disponível
    if "GPSInfo" in metadata:
        gps_info = metadata["GPSInfo"]
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = convert_gps_to_decimal(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
            lon = convert_gps_to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
            print(f"Localização aproximada: {lat}, {lon}")

def convert_gps_to_decimal(coord, ref):
    degrees, minutes, seconds = coord
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

if __name__ == "__main__":
    image_path = input("Enter the path to the image: ")
    metadata = extract_metadata(image_path)
    display_metadata(metadata)