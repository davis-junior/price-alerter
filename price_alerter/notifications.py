import sqlite3

import requests

from globals import config_dict
from db import (
    should_send_error_notification,
    should_send_target_live_notification,
    add_notification_record,
)


def notify_when_below_target_or_error(cursor: sqlite3.Cursor, results: list["dict"]):
    for result_dict in results:
        _type = ""
        message = ""

        if not result_dict["error"]:
            if result_dict["current_price"] <= result_dict["target_price"]:
                if should_send_target_live_notification(
                    cursor, result_dict["name"], result_dict["store"]
                ):
                    _type = "TARGET_LIVE"
                    message = f"Target price is live: [{result_dict['store']}] {result_dict['name']}: {result_dict['current_price']}"
        else:
            if should_send_error_notification(
                cursor, result_dict["name"], result_dict["store"]
            ):
                _type = "ERROR"
                message = f"Error getting price: [{result_dict['store']}] {result_dict['name']}: {result_dict['info']}"

        if message and _type:
            print(message)
            response = requests.post(
                f"https://ntfy.sh/{config_dict['ntfy_channel']}", data=message
            )

            if response.status_code == 200:
                add_notification_record(
                    cursor,
                    result_dict["name"],
                    result_dict["store"],
                    result_dict["url"],
                    _type,
                    message,
                )
                print("Successfully sent ntfy notificaiton")
