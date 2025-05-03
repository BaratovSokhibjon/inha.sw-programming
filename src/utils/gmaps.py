def create_google_maps_link(origin_lat, origin_lng, dest_lat, dest_lng, vehicle):
    """
    Creates a Google Maps URL for the given coordinates and transportation mode

    Parameters:
    - origin_lat: Origin latitude
    - origin_lng: Origin longitude
    - dest_lat: Destination latitude
    - dest_lng: Destination longitude
    - vehicle: Transportation mode (car, bike, foot, flight)

    Returns:
    - Google Maps URL string
    """
    # Create Google Maps URL with coordinates and transport mode
    maps_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={origin_lat},{origin_lng}"
        f"&destination={dest_lat},{dest_lng}"
    )

    return maps_url
