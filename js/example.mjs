// Cheapest nonstop flights on a route, 30 days ahead, with Google's price verdict.
// Usage: node example.mjs LHR JFK
import { ApifyClient } from 'apify-client';

const token = process.env.APIFY_TOKEN;
if (!token) {
    console.error('Set APIFY_TOKEN first: https://console.apify.com/settings/integrations');
    process.exit(1);
}

const [origin = 'LHR', destination = 'JFK'] = process.argv.slice(2);
const client = new ApifyClient({ token });
const run = await client.actor('lagenuina_agency/google-flights-scraper').call({
    origin, destination, departureDate: '30 days', maxStops: '0', sortBy: 'price', currency: 'USD', maxResults: 10,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
const flights = items.filter((i) => i.type === 'flight');
if (flights[0]?.priceInsights) console.log(`Prices are ${flights[0].priceInsights.priceLevel} right now`);
flights.forEach((f) => console.log(`${f.price} ${f.currency}  ${f.airlines.join(', ')}  ${f.departureTime} -> ${f.arrivalTime}  ${f.flightNumbers.join(', ')}`));
