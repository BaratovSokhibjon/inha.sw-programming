import urllib.parse

def find_real_accommodations(location, price_range="medium"):
    """
    Generate links to real accommodation services for the given location

    Parameters:
    - location: Destination location name
    - price_range: Price range preference (low, medium, high)

    Returns:
    - Formatted string with accommodation links
    """
    # URL encode the location for use in URLs
    encoded_location = urllib.parse.quote(location)

    # Define accommodation service links
    booking_url = f"https://www.booking.com/searchresults.html?ss={encoded_location}"
    airbnb_url = f"https://www.airbnb.com/s/{encoded_location}/homes"
    hotels_url = f"https://www.hotels.com/search.do?destination-id={encoded_location}"
    expedia_url = f"https://www.expedia.com/Hotel-Search?destination={encoded_location}"

    # Add price filters based on preference
    if price_range == "low":
        booking_url += "&nflt=price%3D1%3B"
        airbnb_url += "?price_max=75"
    elif price_range == "high":
        booking_url += "&nflt=price%3D4%3B5%3B"
        airbnb_url += "?price_min=150"
    else:  # medium
        booking_url += "&nflt=price%3D2%3B3%3B"
        airbnb_url += "?price_min=75&price_max=150"

    # Format the accommodation links
    accommodation_links = (
        f"Here are some accommodation options in [highlight]{location}[/highlight]:\n\n"
        f"• [link={booking_url}]Booking.com[/link] - Wide range of hotels and apartments\n"
        f"• [link={airbnb_url}]Airbnb[/link] - Private rooms and entire homes\n"
        f"• [link={hotels_url}]Hotels.com[/link] - Hotel deals and discounts\n"
        f"• [link={expedia_url}]Expedia[/link] - Package deals with flights\n\n"
        f"You can click any of these links to open them in your browser."
    )

    return accommodation_links
