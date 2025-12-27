import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from xml.dom import minidom
import xml.etree.ElementTree as ET

# Timezone VN
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
now = datetime.now(TZ)

# Khung giờ EPG: 04:00 hôm nay → 04:00 ngày mai
start = now.replace(hour=4, minute=0, second=0, microsecond=0)
if now < start:
    start -= timedelta(days=1)
end = start + timedelta(days=1)

URL = "https://bo-apac.tv5monde.com/tvschedule/full"

def fetch(key):
    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "key": key,
        "timezone": "Asia/Ho_Chi_Minh",
        "language": "EN"
    }
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

print("Fetching TV5MONDE Style…")
style = fetch(45)

print("Fetching TV5MONDE Info…")
info = fetch(7)

tv = ET.Element("tv")

channels = {
    "tv5.style": "TV5MONDE Style",
    "tv5.info": "TV5MONDE Info"
}

# Khai báo channel
for cid, name in channels.items():
    ch = ET.SubElement(tv, "channel", id=cid)
    ET.SubElement(ch, "display-name").text = name

def add_programmes(source, channel_id):
    for p in source.get("data", []):
        st = datetime.fromisoformat(p["start"]).astimezone(TZ)
        et = datetime.fromisoformat(p["end"]).astimezone(TZ)

        prog = ET.SubElement(tv, "programme", {
            "start": st.strftime("%Y%m%d%H%M%S %z"),
            "stop": et.strftime("%Y%m%d%H%M%S %z"),
            "channel": channel_id
        })

        ET.SubElement(prog, "title").text = p.get("title", "N/A")
        ET.SubElement(prog, "desc").text = p.get("summary", "")

add_programmes(style, "tv5.style")
add_programmes(info, "tv5.info")

Path("data").mkdir(exist_ok=True)
raw = ET.tostring(tv, "utf-8")
parsed = minidom.parseString(raw)
pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")

with open("data/epg.xml", "wb") as f:
    f.write(pretty_xml)

print("Saved: data/epg.xml")

