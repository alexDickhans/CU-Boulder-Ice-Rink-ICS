import requests
import json
import datetime
from ics import Calendar, Event
import time

# --- CONFIGURATION ---
DAYS_TO_FETCH = 30
URL = "https://ems.colorado.edu/ServerApi.aspx/CustomBrowseEvents"

# Define the output files and their matching keywords
# Order matters! We check specific matches (like "Club Figure Skating") 
# before generic ones (like "Figure Skating") to prevent double-categorizing.
CALENDARS = {
    'rec_skate': {
        'file': 'rec_skate.ics',
        'keywords': ['Rec Skate'],
        'cal_object': Calendar()
    },
    'club_figure_skating': {
        'file': 'club_figure_skating.ics',
        'keywords': ['Club Figure Skating'], 
        'cal_object': Calendar()
    },
    # "Ice Skating Club" might be a synonym, but we create a specific cal for it as requested
    'ice_skating_club': {
        'file': 'ice_skating_club.ics',
        'keywords': ['Ice Skating Club'], 
        'cal_object': Calendar()
    },
    # Generic "Figure Skating" (catches "Figure Skate" but excludes "Club" via logic below)
    'figure_skating': {
        'file': 'figure_skating.ics',
        'keywords': ['Figure Skate', 'Figure Skating'], 
        'cal_object': Calendar()
    }
}

HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/json; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'origin': 'https://ems.colorado.edu',
    'referer': 'https://ems.colorado.edu/CustomBrowseEvents.aspx',
    # UPDATE THIS COOKIE IF SCRIPT FAILS
    'cookie': '_scid=myNSw7ukcj1RVQzMvKSLGLA4HkHead88; ASP.NET_SessionId=gwdzaoodsctiftorhzbh1ydg; __AntiXsrfToken=d958f863d28d4b0fa61fe02d68ca1f00;' 
}

def fetch_events_for_date(date_obj):
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
        response = requests.post(URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        outer_json = response.json()
        inner_json_str = outer_json.get('d', '{}')
        data = json.loads(inner_json_str)
        return data.get('DailyBookingResults', [])
    except Exception as e:
        print(f"Failed to fetch {date_str}: {e}")
        return []

def main():
    start_date = datetime.datetime.now()
    seen_ids = set()
    total_added = 0
    
    print(f"Fetching schedule for {DAYS_TO_FETCH} days...")
    
    for i in range(DAYS_TO_FETCH):
        current_date = start_date + datetime.timedelta(days=i)
        events = fetch_events_for_date(current_date)
        
        for event in events:
            event_id = event.get('Id')
            if event_id in seen_ids:
                continue
            
            event_name = event.get('EventName', '').strip()
            # Normalize for checking
            name_lower = event_name.lower()
            
            # --- SORTING LOGIC ---
            target_key = None
            
            # 1. Check for Club Figure Skating FIRST (most specific)
            if 'club figure skating' in name_lower:
                target_key = 'club_figure_skating'
            
            # 2. Check for Ice Skating Club
            elif 'ice skating club' in name_lower:
                target_key = 'ice_skating_club'

            # 3. Check for Rec Skate
            elif 'rec skate' in name_lower:
                target_key = 'rec_skate'
                
            # 4. Check for generic Figure Skating (if not caught by Club above)
            elif 'figure skate' in name_lower or 'figure skating' in name_lower:
                target_key = 'figure_skating'
            
            # If we found a matching category, create the event
            if target_key:
                e = Event()
                e.name = event_name
                e.location = event.get('Location', 'CU Ice Rink')
                
                # Timezone Handling (UTC)
                if event.get('GmtStart') and event.get('GmtEnd'):
                    try:
                        start_dt = datetime.datetime.fromisoformat(event['GmtStart'])
                        end_dt = datetime.datetime.fromisoformat(event['GmtEnd'])
                        e.begin = start_dt.replace(tzinfo=datetime.timezone.utc)
                        e.end = end_dt.replace(tzinfo=datetime.timezone.utc)
                        
                        # Add to the specific calendar
                        CALENDARS[target_key]['cal_object'].events.add(e)
                        
                        seen_ids.add(event_id)
                        total_added += 1
                    except ValueError:
                        pass
        time.sleep(0.5) # Be polite

    # --- SAVE ALL FILES ---
    print(f"\nProcessed {total_added} events total.")
    for key, data in CALENDARS.items():
        filename = data['file']
        cal = data['cal_object']
        with open(filename, 'w') as f:
            f.writelines(cal.serialize())
        print(f"Saved {filename} ({len(cal.events)} events)")

if __name__ == "__main__":
    main()