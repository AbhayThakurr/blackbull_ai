import datetime
import os
import webbrowser
from typing import Any, List, Optional

from langchain.tools import tool

# Pre-declare google module variables with Any so the type checker is happy.
# They get overwritten with real types when the import succeeds.
Request: Any = None
Credentials: Any = None
InstalledAppFlow: Any = None
build: Any = None
GOOGLE_API_AVAILABLE = False

try:
    from google.auth.transport.requests import Request as _Request
    from google.oauth2.credentials import Credentials as _Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow as _InstalledAppFlow
    from googleapiclient.discovery import build as _build

    Request = _Request
    Credentials = _Credentials
    InstalledAppFlow = _InstalledAppFlow
    build = _build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    pass

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")

# ---------------------------------------------------------------------------
# In-memory pending OAuth flows (keyed by user_id for multi-user support)
# Stored between the URL-generation step and the code-exchange step.
# ---------------------------------------------------------------------------
_pending_auth_flows: dict = {}


class NeedsReauthError(Exception):
    """Raised when Google Calendar OAuth needs user re-authentication."""

    pass


def get_calendar_service(user_id: str = "default"):
    """Gets the Google Calendar API service instance, handling OAuth2 token
    loading and refresh.

    If the token is expired AND cannot be refreshed (e.g. the Google Cloud
    OAuth app is in Testing mode and the refresh token has expired), this
    raises ``NeedsReauthError`` with instructions so the caller can return a
    user-friendly message instead of blocking on a browser-based flow.
    """
    if not GOOGLE_API_AVAILABLE:
        raise ImportError(
            "Google API client libraries are not installed. "
            "Please install packages listed in requirements.txt."
        )

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as refresh_err:
                print(
                    f"[Calendar Tools] Token refresh failed for {user_id}: {refresh_err}"
                )
                creds = None

        if not creds:
            # Instead of blocking on run_console() / run_local_server(),
            # raise a specific error so tools can return a helpful message.
            raise NeedsReauthError(
                "My access to your Google Calendar has expired. "
                "Please ask me to **reauthenticate my Google Calendar** "
                "and I will send you a link to authorize access."
            )

        # Save refreshed/new credentials
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# Re-authentication tools (two-step headless OAuth flow)
# ---------------------------------------------------------------------------


@tool
def reauthenticate_google_calendar(user_id: str = "default") -> str:
    """Starts Google Calendar re-authentication and returns an authorization URL.

    Use this tool when the user's Google Calendar token has expired and needs
    to be refreshed.  The user must visit the returned URL in their browser,
    sign in, and grant calendar access.  After authorizing they will receive a
    code that they should pass to the *complete_google_calendar_auth* tool.
    """
    if not GOOGLE_API_AVAILABLE:
        return (
            "Google API client libraries are not installed. "
            "Please install packages listed in requirements.txt."
        )

    if not os.path.exists(CREDENTIALS_PATH):
        return (
            f"OAuth credentials file not found at '{CREDENTIALS_PATH}'. "
            "Please download credentials.json from your Google Cloud Console "
            "(Desktop App type) and place it in the app/tools/calendar directory."
        )

    # Remove the stale token so get_calendar_service() doesn't keep trying it
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
        print(f"[Calendar Tools] Deleted stale token.json for {user_id}")

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    # Store the flow so we can exchange the code later
    _pending_auth_flows[user_id] = flow

    return (
        "Alright, let's get your Google Calendar re-authorized! 🗓️\n\n"
        "**Step 1:** Open this link in your browser:\n"
        f"{auth_url}\n\n"
        "**Step 2:** Sign in with your Google account and grant calendar access.\n"
        "**Step 3:** After authorizing, Google will show you a **code**. "
        "Copy that code and tell me:\n"
        f'> *"My auth code is <PASTE THE CODE HERE>"*\n\n'
        "I'll take it from there and save the new credentials."
    )


@tool
def complete_google_calendar_auth(auth_code: str, user_id: str = "default") -> str:
    """Completes Google Calendar OAuth by exchanging an authorization code for tokens.

    Call this *after* the user has visited the URL from `reauthenticate_google_calendar`
    and obtained an authorization code from Google.
    """
    flow = _pending_auth_flows.pop(user_id, None)
    if flow is None:
        return (
            "No pending authentication request found. Please start again by asking me "
            "to **reauthenticate my Google Calendar** first."
        )

    try:
        flow.fetch_token(code=auth_code.strip())
        creds = flow.credentials

        # Persist the credentials
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

        expiry = (
            creds.expiry.strftime("%Y-%m-%d %I:%M %p UTC") if creds.expiry else "N/A"
        )
        return (
            "✅ **Google Calendar re-authentication successful!**\n\n"
            f"Your new credentials have been saved and will be valid until **{expiry}**.\n"
            "You can now ask me to check your schedule or manage your events again!"
        )
    except Exception as e:
        print(f"[Calendar Tools] Auth code exchange failed for {user_id}: {e}")
        return (
            f"❌ Failed to complete authentication: {e}\n\n"
            "Please try again by asking me to **reauthenticate my Google Calendar** "
            "and make sure you copy the full code from Google."
        )


# ---------------------------------------------------------------------------
# Date / time helpers
# ---------------------------------------------------------------------------


def parse_date_time(date_str: str, time_str: str) -> datetime.datetime:
    now = datetime.datetime.now().astimezone()

    # Parse date
    if not date_str or date_str.lower() == "today":
        target_date = now.date()
    elif date_str.lower() == "tomorrow":
        target_date = (now + datetime.timedelta(days=1)).date()
    else:
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = now.date()

    # Parse time
    target_time = None
    if time_str:
        time_str_clean = time_str.strip()
        for fmt in ["%I:%M %p", "%H:%M", "%I %p", "%I:%M%p", "%H:%M:%S"]:
            try:
                target_time = datetime.datetime.strptime(time_str_clean, fmt).time()
                break
            except ValueError:
                continue

    if not target_time:
        target_time = (now + datetime.timedelta(hours=1)).time()

    return datetime.datetime.combine(target_date, target_time, tzinfo=now.tzinfo)


# ---------------------------------------------------------------------------
# Calendar tools exposed to agents
# ---------------------------------------------------------------------------


@tool
def check_calendar_schedule(date_str: Optional[str] = None) -> str:
    """
    Checks the user's upcoming meeting schedule on Google Calendar, including Google Meet links.
    Pass a date string like 'today', 'tomorrow', or 'YYYY-MM-DD'.
    """
    try:
        service = get_calendar_service()
    except NeedsReauthError as e:
        return f"⚠️ {e}"
    except Exception as e:
        return f"Google Calendar Authentication/Setup Error: {str(e)}"

    now = datetime.datetime.now(datetime.timezone.utc)
    if not date_str or date_str.lower() == "today":
        start_time = now.isoformat()
        end_time = (now.replace(hour=23, minute=59, second=59)).isoformat()
    elif date_str.lower() == "tomorrow":
        tmr = now + datetime.timedelta(days=1)
        start_time = tmr.replace(hour=0, minute=0, second=0).isoformat()
        end_time = tmr.replace(hour=23, minute=59, second=59).isoformat()
    else:
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(
                tzinfo=datetime.timezone.utc
            )
            start_time = dt.isoformat()
            end_time = dt.replace(hour=23, minute=59, second=59).isoformat()
        except ValueError:
            start_time = now.isoformat()
            end_time = (now + datetime.timedelta(days=1)).isoformat()

    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_time,
                timeMax=end_time,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return f"Google Calendar Schedule for {date_str or 'today'}: No upcoming meetings found."

        result_lines = [f"Google Calendar Schedule for {date_str or 'today'}:"]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            try:
                dt_obj = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                time_display = dt_obj.strftime("%I:%M %p")
            except Exception:
                time_display = start

            summary = event.get("summary", "Untitled Event")
            meet_link = event.get("hangoutLink", "No Google Meet link")
            result_lines.append(
                f"- {time_display}: {summary} (Google Meet: {meet_link})"
            )

        return "\n".join(result_lines)
    except Exception as e:
        return f"Failed to fetch calendar events from Google Calendar API: {str(e)}"


@tool
def schedule_google_meet(
    title: str, date_str: str, time_str: str, attendees: Optional[List[str]] = None
) -> str:
    """
    Schedules a new meeting on Google Calendar and generates a Google Meet link.
    Provide the meeting title, date (e.g. 'today', 'tomorrow', 'YYYY-MM-DD'),
    time (e.g. '03:00 PM'), and optional list of attendee emails.
    """
    try:
        service = get_calendar_service()
    except NeedsReauthError as e:
        return f"⚠️ {e}"
    except Exception as e:
        return f"Google Calendar Authentication/Setup Error: {str(e)}"

    try:
        start_dt = parse_date_time(date_str, time_str)
        end_dt = start_dt + datetime.timedelta(minutes=45)

        event_body = {
            "summary": title,
            "start": {
                "dateTime": start_dt.isoformat(),
            },
            "end": {
                "dateTime": end_dt.isoformat(),
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{int(datetime.datetime.now().timestamp())}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }

        if attendees:
            event_body["attendees"] = [{"email": email.strip()} for email in attendees]

        event_result = (
            service.events()
            .insert(calendarId="primary", body=event_body, conferenceDataVersion=1)
            .execute()
        )

        meet_link = event_result.get("hangoutLink", "No Google Meet link generated")
        att_str = f" with attendees {', '.join(attendees)}" if attendees else ""
        return f"Successfully scheduled '{title}' on {date_str} at {time_str}{att_str}.\nGoogle Meet Link: {meet_link}"
    except Exception as e:
        return f"Failed to schedule meeting via Google Calendar API: {str(e)}"


@tool
def open_google_meet(meet_url: str, browser_name: Optional[str] = None) -> str:
    """
    Opens/launches a Google Meet meeting URL directly in the user's browser so they can join.
    Provide the full Google Meet URL (e.g. 'https://meet.google.com/abc-defg-hij').
    If the user explicitly specifies a browser (e.g. 'firefox', 'chrome', 'brave'), pass it in browser_name.
    """
    try:
        if not meet_url.startswith(("http://", "https://")):
            meet_url = "https://" + meet_url

        if browser_name:
            b_map = {"firefox": "firefox", "chrome": "google-chrome", "brave": "brave"}
            target = b_map.get(browser_name.lower(), browser_name.lower())
            try:
                webbrowser.get(target).open(meet_url)
                return f"Successfully opened {browser_name} and launched Google Meet: {meet_url}"
            except webbrowser.Error:
                webbrowser.open(meet_url)
                return f"Opened default browser (could not find {browser_name}) and launched Google Meet: {meet_url}"
        else:
            webbrowser.open(meet_url)
            return f"Successfully opened default browser and launched Google Meet: {meet_url}"
    except Exception as e:
        return f"Failed to open Google Meet URL: {str(e)}"
