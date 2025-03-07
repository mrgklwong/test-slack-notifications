import pandas as pd
from datetime import datetime
import requests
import os

EXCEL_FILE = "Report_Leave_requests.xlsx"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def read_events():
    try:
        df = pd.read_excel(
            EXCEL_FILE,
            parse_dates=['Date', 'StartDate', 'EndDate']
        )
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()

def check_events():
    today = datetime.now().date()
    df = read_events()

    if not df.empty:
        messages = []

        # Process Birthdays/Holidays
        bh_events = df[df['Type'].isin(['Birthday', 'Holiday'])]
        bh_events = bh_events.dropna(subset=['Date'])
        for _, event in bh_events.iterrows():
            event_date = event['Date'].date()
            if event_date.month == today.month and event_date.day == today.day:
                msg = event.get('Message') or f"Today is {event['Name']}'s {event['Type']}! 🎉"
                messages.append(msg)

        # Process Leaves
        leaves = df[df['Type'] == 'Leave']
        leaves = leaves.dropna(subset=['StartDate', 'EndDate'])
        for _, leave in leaves.iterrows():
            start = leave['StartDate'].date()
            end = leave['EndDate'].date()
            if start <= today <= end:
                days_left = (end - today).days
                msg = leave.get('Message') or (
                    f"{leave['Name']} is on leave ({start.strftime('%b %d')}-{end.strftime('%b %d')}). "
                    f"{days_left} day(s) remaining."
                )
                messages.append(msg)

        # Send all messages
        if messages:
            send_slack_message("\n".join(messages))

def send_slack_message(message):
    payload = {"text": message}
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
    check_events()