import json
import pathlib
from pprint import pprint
import traceback


def make_and_get_directory_path():
    directory_path = pathlib.Path("price_alerter_config")
    directory_path.mkdir(exist_ok=True, parents=True)
    return directory_path


def get_config_file_path():
    directory_path = make_and_get_directory_path()
    return directory_path / "config.json"


def save_config(config_dict: dict):
    """Does not utilize global var"""

    file_path = get_config_file_path()

    with open(str(file_path), "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=4)


def load_config() -> dict:
    """Does not utilize global var"""

    config_dict = {"ntfy_channel": ""}

    file_path = get_config_file_path()
    if not file_path.exists():
        return config_dict

    try:
        with open(str(file_path), "r", encoding="utf-8") as f:
            config_dict = json.load(f)
    except:
        traceback.print_exc()

    return config_dict


def main():
    global config_dict
    from globals import config_dict

    print("Current config:")
    pprint(config_dict)

    for key in config_dict:
        original_value = config_dict[key]
        if original_value and original_value.strip():
            value = input(f"Enter new value for {key} ({original_value}): ")
        else:
            value = input(f"Enter new value for {key}: ")

        if value and value.strip():
            config_dict[key] = value

    print("Current config:")
    pprint(config_dict)

    save_config(config_dict)


if __name__ == "__main__":
    main()
