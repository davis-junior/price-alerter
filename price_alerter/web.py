import pathlib
import textwrap


def create_html(graph_filenames: list["str"]):
    html = get_html_header_boilerplate("Price Tracker")
    html += "<h1>Price Tracker</h1>"

    for filename in graph_filenames:
        html += f"<img src='graphs/{filename}' width='800' alt='{filename}'>"
        html += "<br><br>"

    html += get_html_footer_boilerplate()
    html = textwrap.dedent(html).strip()

    root_path = pathlib.Path("price_alerter")
    root_path.mkdir(parents=True, exist_ok=True)

    html_file_path = root_path / "price_alerter.html"

    with open(str(html_file_path), "w", encoding="utf-8") as html_file:
        html_file.write(html)

    return html


def get_html_header_boilerplate(title: str):
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{title}</title>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <style>
                    img:hover {{
                        width: 100%
                    }}
                </style>
            </head>
            <body>
    """


def get_html_footer_boilerplate():
    return """
            </body>
        </html>
    """
