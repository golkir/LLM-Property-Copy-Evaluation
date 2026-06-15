{
  "property_id": int,
  "property_name": string,
  "property_type": string,              # e.g. "NormalApartment", "Villa", "Cottage"
  "description": {
    "name": string,
    "headline": string,
    "description": string,              # may contain HTML
  },
  "amenities": [string],               # internal codes, e.g. "BathroomAndLaundry", "DishWasher", "InternetBroadband"
  "image_urls": [string],
  "reviews": [string],                  # full guest review texts
  "num_of_reviews": int,
  "average_review_score": float,        // e.g. 4.96
  "rental_info": {
    "max_guests": int,
    "bedrooms": int,
    "bathrooms": int
  },
  "location": {
    "city": string,
    "country": string,
    "latitude": float,
    "longitude": float
  },
  "policies": {
    "cancellation_policy": string | null,
    "payment_schedule": string | null,
    "damage_deposit": string | null
  },
  "house_rules": {
    "check_in_time": string,            // e.g. "3 PM"
    "check_out_time": string            // e.g. "11 AM"
  }
}