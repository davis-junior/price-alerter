# Description
Scrapes various store prices on given products and alerts via ntfy when prices are below target price. All products are scanned hourly and scraped price data is saved into a SQLite database.

If a price is below target price, a notification is sent to the ntfy channel. Though the product is continually monitored and data is saved to the database. If a price alert was already sent out, it will not be sent out again for 24 hours if it is still the same price. Similarally, detected errors are notified via ntfy, but they are sent a maximum of 1 per 8 hours per product and store combination.

# TODO
- Decouple internal list of dictionaries of products to external YAML config or similar
- Implement polling interval as YAML argument
- Implement argparse with arguments for the YAML config file, SQLite database file, and ntfy channel
