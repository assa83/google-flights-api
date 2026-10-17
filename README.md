# Google Flights API – working example (Python, JS, n8n)

Get flight prices from Google Flights for any route and date – fare, airlines, flight numbers, stops, layovers, times, CO2, Google's low / typical / high price verdict with price history, a price calendar (cheapest day to fly) and booking links – and get an alert when a fare drops below your threshold.

Powered by the [google-flights-scraper](https://apify.com/lagenuina_agency/google-flights-scraper) actor on Apify. No browser, no cookies, no account on Google.

## Example output (real result, shortened)

```json
{
  "type": "flight",
  "origin": "MXP",
  "destination": "JFK",
  "departureDate": "2026-12-10",
  "returnDate": "2026-12-17",
  "price": 709,
  "currency": "EUR",
  "airlines": ["Vueling", "LEVEL"],
  "flightNumbers": ["VY 6045", "LL 2627"],
  "departureTime": "2026-12-10T15:10",
  "arrivalTime": "2026-12-10T22:00",
  "durationMinutes": 770,
  "stops": 1,
  "layovers": [{ "airport": "BCN", "city": "Barcelona", "durationMinutes": 120 }],
  "priceInsights": { "lowestPrice": 709, "typicalPriceLow": 510, "typicalPriceHigh": 960, "priceLevel": "typical" }
}
```

Real output of `python/example.py LHR JFK --max-price 600 --calendar-days 5`:

```
Google says prices are typical (typical 400-570 USD)
ALERT 505 USD  JetBlue  2026-11-16T08:05 -> 2026-11-16T11:14  0 stop(s)  B6 2220
      691 USD  Aer Lingus  2026-11-16T10:00 -> 2026-11-16T17:20  1 stop(s)  EI 381, EI 111
Cheapest day in the next 5: 2026-11-17 at 404 USD
```

## Quickstart (3 steps)

1. Create a free Apify account and copy your API token from [Settings → Integrations](https://console.apify.com/settings/integrations).
2. Put it in an environment variable (never in code): `export APIFY_TOKEN=your_token`
3. Run the example:

```bash
pip install -r python/requirements.txt
python python/example.py LHR JFK --days-ahead 30 --max-price 450 --calendar-days 14
```

Round trip: add `--return-after 7`. JavaScript: `cd js && npm install && node example.mjs LHR JFK`

## Examples

**Python** (`pip install "apify-client<2"`)

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("lagenuina_agency/google-flights-scraper").call(run_input={
  "origin": "LHR",
  "destination": "JFK",
  "departureDate": "30 days",
  "currency": "USD",
  "sortBy": "price"
})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item["price"], item["airlines"], item["departureTime"])
```

**JavaScript / Node.js** (`npm install apify-client`)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('lagenuina_agency/google-flights-scraper').call({ origin: 'LHR', destination: 'JFK', departureDate: '30 days', currency: 'USD' });
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);
```

**cURL / any language** – one HTTP call, results in the response:

```bash
curl -X POST "https://api.apify.com/v2/acts/lagenuina_agency~google-flights-scraper/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"origin": "MXP", "destination": "JFK", "departureDate": "2026-12-10", "returnDate": "2026-12-17", "currency": "EUR", "calendarDays": 14}'
```

All input fields are documented on the [actor page](https://apify.com/lagenuina_agency/google-flights-scraper) (Input tab).

## Use case: daily fare alert

`python/example.py` searches a route N days ahead (relative dates like `"30 days"` keep a scheduled run looking the same distance ahead), prints an ALERT for every fare at or below your threshold, Google's price verdict, and optionally the cheapest day to fly in the next N days. Run it daily from cron or use the n8n workflow.

## n8n workflow

[`n8n/workflow.json`](n8n/workflow.json): every day 07:00 → search the route 30 days ahead → a Code node keeps only fares at or below the threshold (edit `MAX_PRICE`), ready for a Slack/Gmail node.

1. In n8n: **Workflows → Import from File** and pick `n8n/workflow.json`.
2. Create a **Header Auth** credential named `Apify API token` with name `Authorization` and value `Bearer <your token>`, and select it in the *Run Apify actor* node.
3. Edit the JSON body (your route) and activate.

The `run-sync-get-dataset-items` endpoint waits up to 300 s; for bigger runs use `/runs` plus a webhook.

## Use with AI agents (MCP)

Give Claude, ChatGPT, Cursor or any MCP client this actor as a tool:

```json
{
  "mcpServers": {
    "google-flights-scraper": {
      "url": "https://mcp.apify.com/?actors=lagenuina_agency/google-flights-scraper"
    }
  }
}
```

Sign in with Apify OAuth when asked, or send `Authorization: Bearer <APIFY_TOKEN>`.

## Pricing

Per row (one itinerary or one calendar day), price insights, return flights and booking links included, no start fee:

| Apify plan | Per 1,000 rows |
|---|---|
| Free | $0.16 |
| Bronze | $0.128 |
| Silver | $0.104 |
| Gold, Platinum, Diamond | $0.08 |

See [lagenuina_agency/google-flights-scraper](https://apify.com/lagenuina_agency/google-flights-scraper). Planning the hotel too? [Google Hotels Prices API example](https://github.com/assa83/google-hotels-prices-api).

## Disclaimer

Independent, not affiliated with Google (not endorsed by Google LLC). It reads only publicly available data. Use it in line with the applicable terms and laws.

## License

[MIT](LICENSE) © Quelli di Carne Genuina
