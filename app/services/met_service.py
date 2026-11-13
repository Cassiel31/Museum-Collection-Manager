
import requests

BASE_URL = "https://collectionapi.metmuseum.org/public/collection"


def search_artifacts(query):
    url = f"{BASE_URL}/v1.1/search"

    params = {
        "q": query,
        "hasImages": "true",
        "limit": 20
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    return response.json().get("objectIDs") or []


def get_artifact(object_id):
    url = f"{BASE_URL}/v1/objects/{object_id}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.json()


from datetime import datetime


def import_artifact(object_id, supabase):
    # Fetch artwork from the Met
    artwork = get_artifact(object_id)

    # Prevent duplicate imports
    existing = (
        supabase.table("artifacts")
        .select("artifact_id")
        .eq("met_object_id", object_id)
        .execute()
    )

    if existing.data:
        return {
            "message": "Artifact already imported!",
            "artifact_id": existing.data[0]["artifact_id"]
        }

    # Find or create artist
    artist_name = artwork.get("artistDisplayName") or "Unknown Artist"

    artist_result = (
        supabase.table("artists")
        .select("artist_id")
        .eq("name", artist_name)
        .execute()
    )

    if artist_result.data:
        artist_id = artist_result.data[0]["artist_id"]
    else:
        birth_year = int(artwork["artistBeginDate"]) if artwork.get("artistBeginDate", "").isdigit() and int(artwork["artistBeginDate"]) < 9999 else None
        death_year = int(artwork["artistEndDate"]) if artwork.get("artistEndDate", "").isdigit() and int(artwork["artistEndDate"]) < 9999 else None

        new_artist = supabase.table("artists").insert({
            "name": artist_name,
            "birth_year": birth_year,
            "death_year": death_year,
            "nationality": artwork.get("artistNationality") or None,
            "biography": artwork.get("artistDisplayBio") or None
        }).execute()

        artist_id = new_artist.data[0]["artist_id"]

    # Find or create category
    category_name = artwork.get("classification") or artwork.get("department") or "Unclassified"

    category_result = (
        supabase.table("categories")
        .select("category_id")
        .eq("category_name", category_name)
        .execute()
    )

    if category_result.data:
        category_id = category_result.data[0]["category_id"]
    else:
        new_category = supabase.table("categories").insert({
            "category_name": category_name,
            "description": "Imported from the Metropolitan Museum of Art."
        }).execute()

        category_id = new_category.data[0]["category_id"]

    # Prepare creation year
    creation_year = artwork.get("objectBeginDate")
    if creation_year == 0:
        creation_year = None

    # Insert artifact
    new_artifact = supabase.table("artifacts").insert({
        "title": artwork.get("title") or "Untitled Artifact",
        "description": artwork.get("creditLine") or None,
        "artist_id": artist_id,
        "category_id": category_id,
        "origin": artwork.get("country") or None,
        "period": artwork.get("period") or artwork.get("culture") or None,
        "creation_year": creation_year,
        "material": artwork.get("medium") or None,
        "dimensions": artwork.get("dimensions") or None,
        "image_url": artwork.get("primaryImageSmall") or artwork.get("primaryImage") or None,
        "met_object_id": object_id
    }).execute()

    return {
        "message": "Artifact imported successfully!",
        "artifact_id": new_artifact.data[0]["artifact_id"],
        "title": artwork.get("title"),
        "image_url": artwork.get("primaryImageSmall")
    }

