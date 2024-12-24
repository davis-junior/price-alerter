from collections import defaultdict
from datetime import datetime
import pathlib

import matplotlib.pyplot as plt
import sqlite3

from db import get_rows_for_graphs


def create_graphs(cursor: sqlite3.Cursor) -> list["str"]:
    graphs_path = pathlib.Path("price_alerter") / "graphs"
    graphs_path.mkdir(parents=True, exist_ok=True)

    files = []

    rows = get_rows_for_graphs(cursor)

    # We'll store data in a dictionary keyed by product.
    # Each entry will hold a list of (date, price) tuples.
    data_by_product = defaultdict(list)

    for product_name, store, current_price, timestamp_added in rows:
        key = product_name + store
        data_by_product[key].append(
            (product_name, store, timestamp_added, current_price)
        )

    # Now we have all data grouped by product.
    # For each product, we will create a separate figure and plot.

    for key, data_points in data_by_product.items():
        # Separate dates and prices
        timestamps = [
            datetime.strptime(timestamp_added, "%Y-%m-%d %H:%M:%S")
            for product_name, store, timestamp_added, current_price in data_points
        ]
        prices = [
            current_price
            for product_name, store, timestamp_added, current_price in data_points
        ]

        product_name = data_points[0][0]
        store = data_points[0][1]

        # Create a new figure for this product
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the data
        ax.scatter(timestamps, prices)

        # Set plot title and labels
        ax.set_title(f"Price History for {product_name} ({store})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")

        # Format the date labels
        fig.autofmt_xdate()

        # Optionally add a grid
        ax.grid(True)

        # plt.show()

        filename = f"{product_name}_{store}_price_history.png"
        filename = filename.replace('"', "").replace("'", "")
        graph_image_path = graphs_path / filename
        plt.savefig(str(graph_image_path), dpi=300, bbox_inches="tight")
        plt.close(fig)

        files.append(filename)

    return files
