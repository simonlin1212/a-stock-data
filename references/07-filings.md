# Layer 7: 公告层

## 7.1 巨潮公告（直连 cninfo.com.cn）

```python
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def cninfo_announcements(code: str, page_size: int = 30) -> list[dict]:
    """
    巨潮公告全文检索。
    返回: [{title, type, date, url}]
    """
    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    if code.startswith("6"):
        plate = "sh"
    elif code.startswith("8"):
        plate = "bj"
    else:
        plate = "sz"

    payload = {
        "stock": f"{code},{plate}",
        "tabName": "fulltext",
        "pageSize": str(page_size),
        "pageNum": "1",
        "column": plate.upper() + "E",
        "category": "",
        "plate": "",
        "seDate": "",
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.cninfo.com.cn/new/disclosure",
        "Origin": "https://www.cninfo.com.cn",
    }
    r = requests.post(url, data=payload, headers=headers, timeout=15)
    d = r.json()
    return [{
        "title": item.get("announcementTitle", ""),
        "type": item.get("announcementTypeName", ""),
        "date": item.get("announcementTime", ""),
        "url": f"https://www.cninfo.com.cn/new/disclosure/detail?annoId={item.get('announcementId', '')}",
    } for item in d.get("announcements", []) or []]
```

---

## 7.2 mootdx F10 公告摘要

```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')
text = client.F10(symbol='688017', name='最新提示')
# 包含最近的公告 / 分红 / 股东大会决议等摘要
```
