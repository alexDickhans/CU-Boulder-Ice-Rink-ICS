# CU Boulder Ice Rink Calendars

This project automatically scrapes the [CU Boulder EMS schedule](https://ems.colorado.edu/CustomBrowseEvents.aspx) and generates synchronized `.ics` files. This allows you to see Rec Skate and Club times directly in your personal calendar without checking the website manually.

## 📅 Subscription Links ![Update Status](https://github.com/alexDickhans/CU-Boulder-Ice-Rink-ICS/actions/workflows/update.yml/badge.svg)

**Important:** Do not download the files. Instead, **right-click** the links below and select **"Copy Link Address"** to use in the subscription steps below.

* [⛸️ Rec Skate](https://skating.dickhans.net/rec_skate.ics)
* [🏆 Club Figure Skating](https://skating.dickhans.net/club_figure_skating.ics)
* [🤝 Ice Skating Club](https://skating.dickhans.net/ice_skating_club.ics)
* [❄️ Figure Skating (General)](https://skating.dickhans.net/figure_skating.ics)

---

## 🛠 How to Add to Your Calendar

### Google Calendar (Web & Android)
1.  Open [Google Calendar](https://calendar.google.com) on a computer.
2.  On the left sidebar, find **"Other calendars"** and click the **+** icon.
3.  Select **"From URL"**.
4.  Paste the link you copied above.
5.  Click **"Add calendar"**.
*Note: Google Calendar can take up to 24 hours to sync changes from the source.*

### Apple Calendar (iPhone & Mac)
**On iPhone/iPad:**
1.  Open the **Settings** app.
2.  Go to **Calendar** > **Accounts** > **Add Account**.
3.  Select **Other** > **Add Subscribed Calendar**.
4.  Paste the URL and tap **Next**.

**On Mac:**
1.  Open the **Calendar** app.
2.  Go to **File** > **New Calendar Subscription...**
3.  Paste the URL and click **Subscribe**.
4.  Set the "Location" to **iCloud** if you want it to show up on your iPhone too.

### Outlook (Web & Desktop)
1.  Go to [Outlook Calendar](https://outlook.live.com/calendar).
2.  Click **Add Calendar** in the left navigation pane.
3.  Select **Subscribe from web**.
4.  Paste the URL, give the calendar a name (e.g., "CU Rec Skate"), and click **Import**.

---

## 🤖 How it Works
This repository uses **GitHub Actions** to run a Python script every morning at 6:00 AM. 
1. The script initializes a session to fetch fresh cookies from the EMS portal.
2. It queries the `ServerApi.aspx` endpoint for the next 30 days of data.
3. It deduplicates events using their internal EMS unique IDs.
4. It sorts events into specific categories based on keywords.
5. It pushes the updated `.ics` files to this repository, which are then hosted via GitHub Pages.

---
*Disclaimer: This is an independent project and is not officially affiliated with the University of Colorado Boulder. Schedule accuracy depends on the data provided by the EMS system.*