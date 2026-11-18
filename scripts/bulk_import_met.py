import sys
import time
from pathlib import Path

# Make the project root importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import supabase
from app.services.met_service import search_artifacts, get_artifact, import_artifact

TARGET = 60

SEARCH_TERMS = [
    "painting",
    "sculpture",
    "print",
    "drawing",
    "ceramic",
    "textile",
    "jewelry",
    "furniture",
    "photograph",
    "manuscript",
    "glass",
    "vase",
    "coin",
    "armor",
    "musical instrument",
]

print("Searching the Metropolitan Museum collection...")

object_ids = []
seen = set()

for term in SEARCH_TERMS:
    try:
        results = search_artifacts(term)

        added = 0
        for object_id in results[:80]:
            if object_id not in seen:
                seen.add(object_id)
                object_ids.append(object_id)
                added += 1

        print(f"  {term}: found {added} new candidates")

    except Exception as error:
        print(f"  Search failed for '{term}': {error}")

print(f"\nCollected {len(object_ids)} unique candidates.")
print(f"Importing up to {TARGET} public-domain artworks with images...\n")

imported = 0
skipped = 0
failed = 0

for object_id in object_ids:
    if imported >= TARGET:
        break

    try:
        artwork = get_artifact(object_id)

        # Only import public-domain objects with actual images
        if not artwork.get("isPublicDomain"):
            skipped += 1
            continue

        if not (artwork.get("primaryImage") or artwork.get("primaryImageSmall")):
            skipped += 1
            continue

        if not artwork.get("title"):
            skipped += 1
            continue

        result = import_artifact(object_id, supabase)

        if result.get("message") == "Artifact imported successfully!":
            imported += 1
            print(
                f"[{imported}/{TARGET}] "
                f"{result.get('title')} "
                f"(Met ID: {object_id})"
            )
        else:
            skipped += 1
            print(f"[SKIPPED] Already imported: {object_id}")

        time.sleep(0.12)

    except Exception as error:
        failed += 1
        print(f"[ERROR] Met ID {object_id}: {error}")
        time.sleep(0.2)

print("\n========== IMPORT SUMMARY ==========")
print(f"Successfully imported: {imported}")
print(f"Skipped:               {skipped}")
print(f"Failed:                {failed}")
print("====================================")

if imported < TARGET:
    print(
        f"\nOnly {imported} were imported. "
        "We can run another batch with additional search terms."
    )
