import random
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from faker import Faker
from mcp.server.fastmcp import FastMCP
from pydantic import Field

app = FastMCP()
fake = Faker()


@dataclass
class Hotel:
    name: str
    address: str
    location: str
    rating: float
    price_per_night: float
    hotel_type: str
    amenities: list[str]
    available_rooms: int


@dataclass
class HotelSuggestions:
    hotels: list[Hotel]


def validate_iso_date(date_str: str, param_name: str):
    """
    Validates that a string is in ISO format (YYYY-MM-DD) and returns the parsed date.

    Args:
        date_str: The date string to validate
        param_name: Name of the parameter for error messages

    Returns:
        The parsed date object

    Raises:
        ValueError: If the date is not in ISO format or is invalid
    """
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not iso_pattern.match(date_str):
        raise ValueError(f"{param_name} must be in ISO format (YYYY-MM-DD), got: {date_str}")

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid {param_name}: {e}")


@app.tool()
async def suggest_hotels(
    location: Annotated[str, Field(description="Location (city or area) to search for hotels")],
    check_in: Annotated[str, Field(description="Check-in date in ISO format (YYYY-MM-DD)")],
    check_out: Annotated[str, Field(description="Check-out date in ISO format (YYYY-MM-DD)")],
) -> HotelSuggestions:
    """
    Suggest hotels based on location and dates.
    """
    # Validate dates
    check_in_date = validate_iso_date(check_in, "check_in")
    check_out_date = validate_iso_date(check_out, "check_out")

    # Ensure check_out is after check_in
    if check_out_date <= check_in_date:
        raise ValueError("check_out date must be after check_in date")

    # Create realistic mock data for hotels
    hotel_types = ["Luxury", "Boutique", "Budget", "Business"]
    amenities = ["Free WiFi", "Pool", "Spa", "Gym", "Restaurant", "Bar", "Room Service", "Parking"]

    # Generate a rating between 3.0 and 5.0
    def generate_rating():
        return round(random.uniform(3.0, 5.0), 1)

    # Generate a price based on hotel type
    def generate_price(hotel_type):
        price_ranges = {
            "Luxury": (250, 600),
            "Boutique": (180, 350),
            "Budget": (80, 150),
            "Resort": (200, 500),
            "Business": (150, 300),
        }
        min_price, max_price = price_ranges.get(hotel_type, (100, 300))
        return round(random.uniform(min_price, max_price))

    # Generate between 3 and 8 hotels
    num_hotels = random.randint(3, 8)
    hotels = []

    neighborhoods = [
        "Downtown",
        "Historic District",
        "Waterfront",
        "Business District",
        "Arts District",
        "University Area",
    ]

    for i in range(num_hotels):
        hotel_type = random.choice(hotel_types)
        hotel_amenities = random.sample(amenities, random.randint(3, 6))
        neighborhood = random.choice(neighborhoods)

        hotel = Hotel(
            name=f"{hotel_type} {['Hotel', 'Inn', 'Suites', 'Resort', 'Plaza'][random.randint(0, 4)]}",
            address=fake.street_address(),
            location=f"{neighborhood}, {location}",
            rating=generate_rating(),
            price_per_night=generate_price(hotel_type),
            hotel_type=hotel_type,
            amenities=hotel_amenities,
            available_rooms=random.randint(1, 15),
        )
        hotels.append(hotel)

    # Sort by rating to show best hotels first
    hotels.sort(key=lambda x: x.rating, reverse=True)
    return HotelSuggestions(hotels=hotels)


if __name__ == "__main__":
    app.run(transport="streamable-http")
