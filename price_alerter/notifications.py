import sqlite3

import requests

from globals import config_dict
from db import should_send_error_notification, should_send_target_live_notification


def notify_when_below_target(cursor: sqlite3.Cursor, results: list["dict"]):
    for result_dict in results:
        message = ""
        if not result_dict["error"]:
            if result_dict["current_price"] <= result_dict["target_price"]:
                if should_send_target_live_notification(
                    cursor, result_dict["name"], result_dict["store"]
                ):
                    message = f"Target price is live: [{result_dict['store']}] {result_dict['name']}: {result_dict['current_price']}"
        else:
            if should_send_error_notification(
                cursor, result_dict["name"], result_dict["store"]
            ):
                message = f"Error getting price: [{result_dict['store']}] {result_dict['name']}: {result_dict['info']}"

        if message:
            print(message)
            response = requests.post(f"https://ntfy.sh/{config_dict['ntfy_channel']}", data=message)
            if response.status_code == 200:
                print("Successfully sent ntfy notificaiton")
