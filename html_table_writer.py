
def write_html_table(headers, rows, title):
    """Returns formatted HTML table from header and rows.
    Example usage:
    headers = ["Name", "Age", "City"]
    rows = [["Alice", 30, "Boston"], ["Bob", 27, "Chicago"]]
    html_str = write_html_table("report.html", headers, rows, title="Employee Report")

    Args:
        headers (list of str): List of column headers.
        rows (list of list of str): List of rows, where each row is a list of cell values.
        title (str): Title for the HTML table.

    Returns:
        str: Formatted HTML table as a string.
    """
    def esc(s):
        return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

    return_str = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>{esc(title)}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        :root {{
          --border: #e5e7eb;
          --bg-alt: #fafafa;
          --th-bg: #f5f5f5;
        }}
        body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; padding: 24px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid var(--border); padding: 8px; }}
        th {{ background: var(--th-bg); text-align: left; }}
        tr:nth-child(even) td {{ background: var(--bg-alt); }}
        caption {{ caption-side: top; font-weight: 600; margin-bottom: 8px; }}
        .home-btn {{
          display: inline-block;
          margin-bottom: 16px;
          padding: 8px 16px;
          background: #0078d4;
          color: #fff;
          text-decoration: none;
          border-radius: 4px;
          font-weight: 500;
          transition: background 0.2s;
        }}
        .home-btn:hover {{
          background: #005fa3;
        }}
      </style>
    </head>
    <body>
      <a href="/" class="home-btn">Home</a>
      <table>
        <caption>{esc(title)}</caption>
        <thead>
          <tr>"""
    for h in headers:
        return_str += f"\n        <th>{esc(h)}</th>"
    return_str += """
          </tr>
        </thead>
        <tbody>"""
    for row in rows:
        return_str += f"\n      <tr>"
        for cell in row:
            return_str += f"\n        <td>{esc(cell)}</td>"
        return_str += "\n      </tr>"
    return_str += """
        </tbody>
      </table>
    </body>
    </html>"""
    return return_str