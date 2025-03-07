import pandas as pd
from datetime import datetime
import requests
import os

EXCEL_FILE = "leaves.xlsx"  # Your Excel file name
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def read_leaves():
    try:
        df = pd.read_excel(
            EXCEL_FILE,
            parse_dates=['Start date', 'Finish date'],
            date_format='%m/%d/%Y'
        )
        return df.dropna(subset=['Start date', 'Finish date'])
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()

def check_leaves():
    today = datetime.now().date()
    df = read_leaves()

    if not df.empty:
        messages = []

        for _, row in df.iterrows():
            start = row['Start date'].date()
            end = row['Finish date'].date()

            if start <= today <= end:
                employee = row['Employee']
                leave_type = row['Time off / Non billable']
                description = row.get('Description', '')
                days_total = (end - start).days + 1
                days_remaining = (end - today).days

                message = (
                    f":palm_tree: {employee} is on {leave_type}\n"
                    f"- Dates: {start.strftime('%b %d')} to {end.strftime('%b %d')}\n"
                    f"- Duration: {days_total} days\n"
                    f"- Days remaining: {days_remaining}\n"
                    f"- Notes: {description}"
                )
                messages.append(message)

        if messages:
            header = ":warning: *Today's Leave Notifications* :warning:\n\n"
            send_slack_message(header + "\n\n".join(messages))

def send_slack_message(message):
    payload = {
        "text": message,
        "username": "Leave Bot",
        "icon_emoji": ":date:"
    }
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Slack message: {e}")

if __name__ == "__main__":
    check_leaves()