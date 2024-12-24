import sqlite3

from db import add_pricelog_record


def record_and_output_results(cursor: sqlite3.Cursor, results: list["dict"]):
    print("Current prices:")
    for result_dict in results:
        print(
            f"[{result_dict['store']}] {result_dict['name']}: {result_dict['current_price']}"
        )

        if not result_dict["error"]:
            if result_dict["current_price"] < result_dict["target_price"]:
                status = "BELOW_TARGET"
            elif result_dict["current_price"] == result_dict["target_price"]:
                status = "AT_TARGET"
            else:
                status = "ABOVE_TARGET"
        else:
            status = "ERROR"

        add_pricelog_record(
            cursor,
            result_dict["name"],
            result_dict["store"],
            result_dict["url"],
            result_dict["target_price"],
            result_dict["current_price"],
            status,
            result_dict["info"],
        )
