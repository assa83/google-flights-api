"""Fare alert: cheapest Google Flights fares for a route, plus the cheapest day to fly.

Usage: python example.py LHR JFK --days-ahead 30 --max-price 450 --calendar-days 14
"""
import argparse
import os
import sys

from apify_client import ApifyClient

ACTOR = "lagenuina_agency/google-flights-scraper"
TOKEN = os.environ.get("APIFY_TOKEN")
if not TOKEN:
    sys.exit("Set APIFY_TOKEN first: https://console.apify.com/settings/integrations")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("origin", help="IATA airport code, e.g. LHR")
    p.add_argument("destination", help="IATA airport code, e.g. JFK")
    p.add_argument("--days-ahead", type=int, default=30)
    p.add_argument("--return-after", type=int, help="nights for a round trip (omit for one way)")
    p.add_argument("--max-price", type=float, help="alert threshold (total price)")
    p.add_argument("--calendar-days", type=int, default=0, help="also find the cheapest day in the next N days")
    p.add_argument("--currency", default="USD")
    a = p.parse_args()

    run_input = {
        "origin": a.origin, "destination": a.destination,
        "departureDate": f"{a.days_ahead} days",
        "currency": a.currency, "sortBy": "price", "maxResults": 10,
        "calendarDays": a.calendar_days,
    }
    if a.return_after:
        run_input["returnDate"] = f"{a.days_ahead + a.return_after} days"

    client = ApifyClient(TOKEN)
    run = client.actor(ACTOR).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    flights = [i for i in items if i["type"] == "flight"]
    if flights and flights[0].get("priceInsights"):
        pi = flights[0]["priceInsights"]
        print(f"Google says prices are {pi['priceLevel']} (typical {pi['typicalPriceLow']}-{pi['typicalPriceHigh']} {a.currency})")
    for f in flights:
        flag = "ALERT " if a.max_price is not None and f["price"] is not None and f["price"] <= a.max_price else "      "
        print(f"{flag}{f['price']} {f['currency']}  {', '.join(f['airlines'])}  {f['departureTime']} -> {f['arrivalTime']}  "
              f"{f['stops']} stop(s)  {', '.join(f['flightNumbers'])}")

    days = [i for i in items if i["type"] == "calendarDay" and i["lowestPrice"] is not None]
    if days:
        best = min(days, key=lambda d: d["lowestPrice"])
        print(f"Cheapest day in the next {a.calendar_days}: {best['departureDate']} at {best['lowestPrice']} {best['currency']}")
    errors = [i for i in items if i["type"] == "error"]
    for e in errors:
        print("error:", e["error"])


if __name__ == "__main__":
    main()
