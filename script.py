import urllib.request
import sys
import json
from collections import namedtuple

URL_STRING = "https://iperdrive.iper.it/spesa-online/SlotDisplayView?sync=1&catalogId=&langId=-4&storeId=10159&pdrId=8"
try: page_html = urllib.request.urlopen(URL_STRING).read().decode("utf-8")
except urllib.error.URLError as e:
    sys.exit(f"Server error: {e}")
except urllib.error.HTTPError as e:
    sys.exit(f"Cannot reach server: {e}")

START_TOKEN = "StoreLocatorJS.initOrari("
start_idx = page_html.find(START_TOKEN)
if start_idx < 0:
    sys.exit("Cannot find data inside HTML content")

end_idx = page_html.find(");", start_idx)
if end_idx < 0:
    sys.exit("Cannot find data inside HTML content")

json_string = page_html[start_idx+len(START_TOKEN):end_idx]
json = json.loads(json_string)

Slot = namedtuple("Slot", "day timeframe")
available_slots = []

for day in json["orario"]:
    for slot in day["slots"]:
        is_available = slot["active"]
        if is_available:
            available_slots.append(Slot(day=day["dayDate"], timeframe=slot["title"]))

if not available_slots:
    print("No slots available")
    sys.exit()

TELEGRAM_BOT_TOKEN = "1086038513:AAFZWXrGI8JzFwcpycBfMt-vgCbjBMtw6FY"
TELEGRAM_CHAT_ID = "751571062"

text = f"{len(available_slots)} slot disponibili:"
for slot in available_slots:
    text += f"\n• {slot.day} {slot.timeframe}"

data = { "chat_id": TELEGRAM_CHAT_ID, "text": text }
data = urllib.parse.urlencode(data).encode()
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
req = urllib.request.Request(url, data=data)
urllib.request.urlopen(req)