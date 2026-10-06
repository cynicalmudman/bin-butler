"""Fetch Elmbridge's current feed without publishing property identifiers."""
import json
import os
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

class ScheduleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = None
        self.sections = []
    def handle_starttag(self, tag, attrs):
        if tag == "h4":
            self.heading = ""
        elif tag == "br" and self.sections:
            self.sections[-1][1] += "\n"
    def handle_data(self, text):
        if self.heading is not None:
            self.heading += text
        elif self.sections:
            self.sections[-1][1] += text
    def handle_endtag(self, tag):
        if tag == "h4" and self.heading is not None:
            self.sections.append([self.heading.strip(), ""])
            self.heading = None

def parse_schedule(html, today):
    parser = ScheduleParser()
    parser.feed(html)
    collections = []
    for heading, text in parser.sections:
        date = datetime.strptime(heading, "%A %d %B %Y").date()
        if date < today:
            continue
        if (date - today).days > 90:
            raise ValueError("Unexpected collection date")
        services = []
        for phrase, label in [
            ("Domestic waste collection service", "Refuse"),
            ("Recycling collection service", "Recycling"),
            ("Food waste collection service", "Food waste"),
            ("Garden waste collection service", "Garden waste (*)"),
        ]:
            if phrase in text:
                services.append(label)
        if not services or not any(s in services for s in ["Refuse", "Recycling"]):
            raise ValueError("Incomplete collection record")
        if "every week" in html and "small electrical" in html:
            services.append("Clothes, textiles and small electricals")
        collections.append({"day": date.strftime("%A"), "date": date.strftime("%d/%m/%Y"), "services": services})
    collections.sort(key=lambda record: datetime.strptime(record["date"], "%d/%m/%Y"))
    if len(collections) < 2:
        raise ValueError("Insufficient future collections")
    if len({record["date"] for record in collections}) != len(collections):
        raise ValueError("Duplicate collection dates")
    return collections

def main():
    uprn = os.environ.get("ELMBRIDGE_UPRN", "")
    if not uprn.isdigit() or not 8 <= len(uprn) <= 12:
        raise ValueError("ELMBRIDGE_UPRN secret is missing or invalid")
    url = "https://edocs.elmbridge.gov.uk/ebcexplorer/default.aspx?uprn=%27" + uprn + "%27"
    with urlopen(Request(url), timeout=60) as response:
        html = response.read(2_000_000).decode("utf-8-sig")
    today = datetime.now(ZoneInfo("Europe/London")).date()
    records = parse_schedule(html, today)
    output = Path("data/schedule.json")
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps({
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "timezone": "Europe/London",
        "collections": records,
    }, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(f"Validated {len(records)} upcoming collection dates.")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never log HTTP exceptions: they may contain the private property URL.
        print("Schedule refresh failed; previous schedule retained. Check the secret and council feed.", file=sys.stderr)
        sys.exit(1)
