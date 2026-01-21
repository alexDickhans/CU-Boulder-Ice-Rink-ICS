import requests
import json
import datetime
from ics import Calendar, Event
import time

# --- CONFIGURATION ---
DAYS_TO_FETCH = 30
# Main page URL (to get cookies)
BASE_URL = "https://ems.colorado.edu/BrowseEvents.aspx"
# API URL (to get data)
API_URL = "https://ems.colorado.edu/ServerApi.aspx/CustomBrowseEvents"

CALENDARS = {
    'rec_skate': {'file': 'rec_skate.ics', 'keywords': ['Rec Skate'], 'cal_object': Calendar()},
    'club_figure_skating': {'file': 'club_figure_skating.ics', 'keywords': ['Club Figure Skating'], 'cal_object': Calendar()},
    'ice_skating_club': {'file': 'ice_skating_club.ics', 'keywords': ['Ice Skating Club'], 'cal_object': Calendar()},
    'figure_skating': {'file': 'figure_skating.ics', 'keywords': ['Figure Skate', 'Figure Skating'], 'cal_object': Calendar()}
}

# Mimic a real Chrome browser so the server doesn't block us
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://ems.colorado.edu',
    'Referer': 'https://ems.colorado.edu/CustomBrowseEvents.aspx',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_session():
    """
    Creates a session and visits the homepage to get fresh cookies.
    """
    s = requests.Session()
    s.headers.update(HEADERS)
    
    print("Visiting homepage to initialize session...", end=" ")
    try:
        # This 'get' request works like opening the page in your browser.
        # It automatically populates s.cookies with ASP.NET_SessionId etc.
        s.get(BASE_URL, timeout=10)
        print("Success! Cookies acquired.")
        return s
    except Exception as e:
        print(f"Failed to initialize session: {e}")
        return None

def fetch_events_for_date(session, date_obj):
    date_str = date_obj.strftime("%Y-%m-%d 00:00:00")
    payload = {
        "date": date_str,
        "data": {
            "BuildingId": -1, "GroupTypeId": -1, "GroupId": -1, "EventTypeId": -1,
            "RoomId": 508, "StatusId": -1, "ZeroDisplayOnWeb": 1, 
            "HeaderUrl": "", "Title": "Ice Rink Schedule", "Format": 0,
            "Rollup": 0, "PageSize": 250, "DropEventsInPast": False
        }
    }
    try:
        # Note: We use 'session.post' instead of 'requests.post'
        response = session.post(API_URL, json=payload)
        response.raise_for_status()
        
        outer_json = response.json()
        inner_json_str = outer_json.get('d', '{}')
        data = json.loads(inner_json_str)
        return data.get('DailyBookingResults', [])
    except Exception as e:
        print(f"Failed to fetch {date_str}: {e}")
        return []

def main():
    # 1. Initialize the session (Auto-Login)
    session = get_session()
    if not session:
        return

    start_date = datetime.datetime.now()
    seen_ids = set()
    total_added = 0
    
    print(f"Fetching schedule for {DAYS_TO_FETCH} days...")
    
    for i in range(DAYS_TO_FETCH):
        current_date = start_date + datetime.timedelta(days=i)
        events = fetch_events_for_date(session, current_date)
        
        for event in events:
            event_id = event.get('Id')
            if event_id in seen_ids:
                continue
            
            event_name = event.get('EventName', '').strip()
            name_lower = event_name.lower()
            
            # Sorting Logic
            target_key = None
            if 'club figure skating' in name_lower:
                target_key = 'club_figure_skating'
            elif 'ice skating club' in name_lower:
                target_key = 'ice_skating_club'
            elif 'rec skate' in name_lower:
                target_key = 'rec_skate'
            elif 'figure skate' in name_lower or 'figure skating' in name_lower:
                target_key = 'figure_skating'
            
            if target_key:
                e = Event()
                e.name = event_name
                e.location = event.get('Location', 'CU Ice Rink')
                
                if event.get('GmtStart') and event.get('GmtEnd'):
                    try:
                        start_dt = datetime.datetime.fromisoformat(event['GmtStart'])
                        end_dt = datetime.datetime.fromisoformat(event['GmtEnd'])
                        e.begin = start_dt.replace(tzinfo=datetime.timezone.utc)
                        e.end = end_dt.replace(tzinfo=datetime.timezone.utc)
                        
                        CALENDARS[target_key]['cal_object'].events.add(e)
                        seen_ids.add(event_id)
                        total_added += 1
                    except ValueError:
                        pass
        time.sleep(0.5)

    print(f"\nProcessed {total_added} events total.")
    for key, data in CALENDARS.items():
        with open(data['file'], 'w') as f:
            f.writelines(data['cal_object'].serialize())
        print(f"Saved {data['file']}")

if __name__ == "__main__":
    main()