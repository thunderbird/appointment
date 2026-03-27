import logging
import os
import uuid
from datetime import datetime

import sentry_sdk
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ... import utils
from ...database import repo
from ...database.models import CalendarProvider
from ...database.schemas import CalendarConnection
from ...defines import DATETIMEFMT
from ...exceptions.calendar import (
    EventNotCreatedException,
    EventNotDeletedException,
    EventNotPatchedException,
    FreeBusyTimeException
)
from ...exceptions.google_api import GoogleScopeChanged, GoogleInvalidCredentials


class GoogleClient:
    """Authenticates with Google OAuth and allows the retrieval of Google Calendar information"""

    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/userinfo.email',
        'openid',
    ]
    client: Flow | None = None

    def __init__(self, client_id, client_secret, project_id, callback_url):
        self.config = {
            'web': {
                'client_id': client_id,
                'client_secret': client_secret,
                'project_id': project_id,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
            }
        }

        self.callback_url = callback_url
        self.client = None

    def setup(self):
        # Ignore if we're already setup!
        if self.client:
            return
        """Actually create the client, this is separate, so we can catch any errors without breaking everything"""
        self.client = Flow.from_client_config(self.config, self.SCOPES, redirect_uri=self.callback_url)

    def get_redirect_url(self):
        """Returns the redirect url for the google oauth flow"""
        if self.client is None:
            return None

        # (Url, State ID)
        return self.client.authorization_url(access_type='offline', prompt='consent')

    def get_credentials(self, code: str):
        if self.client is None:
            return None

        try:
            self.client.fetch_token(code=code)
            return self.client.credentials
        except Warning as e:
            logging.error(f'[google_client.get_credentials] Google Warning: {str(e)}')
            # This usually is the "Scope has changed" error.
            raise GoogleScopeChanged()
        except ValueError as e:
            logging.error(f'[google_client.get_credentials] Value error while fetching credentials {str(e)}')
            raise GoogleInvalidCredentials()

    def get_profile(self, token):
        """Retrieve the user's profile associated with the token"""
        if self.client is None:
            return None

        user_info_service = build('oauth2', 'v2', credentials=token)
        user_info = user_info_service.userinfo().get().execute()

        return user_info

    def list_calendars(self, token):
        """List the calendars a token has access to with the minAccessRole of writer.
        Ref: https://developers.google.com/calendar/api/v3/reference/calendarList/list"""
        response = {}
        items = []
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            request = service.calendarList().list(minAccessRole='writer')
            while request is not None:
                try:
                    response = request.execute()

                    items += response.get('items', [])
                except HttpError as e:
                    logging.warning(f'[google_client.list_calendars] Request Error: {e.status_code}/{e.error_details}')

                request = service.calendarList().list_next(request, response)

        # Sort calendars by primary first, then selected, then others
        # since primary is the most likely to be the one the user wants to use
        def calendar_sort_key(cal):
            if cal.get('primary'):
                return 0
            if cal.get('selected'):
                return 1
            return 2

        items.sort(key=calendar_sort_key)

        return items

    def get_free_busy(self, calendar_ids, time_min, time_max, token):
        """Query the free busy api
        Ref: https://developers.google.com/calendar/api/v3/reference/freebusy/query"""
        response = {}
        items = []

        import time

        perf_start = time.perf_counter_ns()
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            request = service.freebusy().query(
                body=dict(
                    timeMin=time_min, timeMax=time_max, items=[{'id': calendar_id} for calendar_id in calendar_ids]
                )
            )

            while request is not None:
                try:
                    response = request.execute()
                    errors = [calendar.get('errors') for calendar in response.get('calendars', {}).values()]

                    # Log errors and throw 'em in sentry
                    if any(errors):
                        reasons = [
                            {
                                'domain': utils.setup_encryption_engine().encrypt(error.get('domain')),
                                'reason': error.get('reason'),
                            }
                            for error in errors
                        ]
                        if os.getenv('SENTRY_DSN'):
                            ex = FreeBusyTimeException(reasons)
                            sentry_sdk.capture_exception(ex)
                        logging.warning(f'[google_client.get_free_time] FreeBusy API Error: {ex}')

                    calendar_items = [calendar.get('busy', []) for calendar in response.get('calendars', {}).values()]
                    for busy in calendar_items:
                        # Transform to datetimes to match caldav's behaviour
                        items += [
                            {
                                'start': datetime.strptime(entry.get('start'), DATETIMEFMT),
                                'end': datetime.strptime(entry.get('end'), DATETIMEFMT),
                            }
                            for entry in busy
                        ]
                except HttpError as e:
                    logging.warning(f'[google_client.get_free_time] Request Error: {e.status_code}/{e.error_details}')

                request = service.calendarList().list_next(request, response)
        perf_end = time.perf_counter_ns()

        # Capture the metric if sentry is enabled
        print(f'Google FreeBusy response: {(perf_end - perf_start) / 1000000000} seconds')
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.set_measurement('google_free_busy_time_response', perf_end - perf_start, 'nanosecond')

        return items

    def list_events(self, calendar_id, time_min, time_max, token):
        response = {}
        items = []

        # Limit the fields we request
        fields = ','.join(
            (
                'items/id',
                'items/iCalUID',
                'items/status',
                'items/summary',
                'items/description',
                'items/attendees',
                'items/start',
                'items/end',
                'items/transparency',
                # Top level stuff
                'nextPageToken',
            )
        )

        # Explicitly ignore workingLocation events
        # See: https://developers.google.com/calendar/api/v3/reference/events#eventType
        event_types = ['default', 'focusTime', 'outOfOffice']

        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            request = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                eventTypes=event_types,
                fields=fields,
            )

            while request is not None:
                try:
                    response = request.execute()
                    items += response.get('items', [])
                except HttpError as e:
                    logging.warning(f'[google_client.list_events] Request Error: {e.status_code}/{e.error_details}')
                    break

                # We need to manually paginate because the Google API's list_next() method
                # corrupts repeated query params like eventTypes on re-encoding.
                # See https://github.com/googleapis/google-api-python-client/blob/main/googleapiclient/discovery.py#L1382-L1384
                # and https://github.com/googleapis/google-api-python-client/blob/main/googleapiclient/_helpers.py#L141-L163
                page_token = response.get('nextPageToken')

                if page_token:
                    request = service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,
                        orderBy='startTime',
                        eventTypes=event_types,
                        fields=fields,
                        pageToken=page_token,
                    )
                else:
                    request = None

        return items

    def get_event(self, calendar_id, event_id, token):
        """Retrieve a single event by ID.
        Ref: https://developers.google.com/calendar/api/v3/reference/events/get"""
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                return service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            except HttpError as e:
                logging.warning(f'[google_client.get_event] Request Error: {e.status_code}/{e.error_details}')
                return None

    def save_event(self, calendar_id, body, token):
        response = None
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                response = service.events().import_(calendarId=calendar_id, body=body).execute()
            except HttpError as e:
                logging.warning(f'[google_client.save_event] Request Error: {e.status_code}/{e.error_details}')
                raise EventNotCreatedException()

        return response

    def insert_event(self, calendar_id, body, token, send_updates='all'):
        response = None
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                response = service.events().insert(
                    calendarId=calendar_id, body=body, sendUpdates=send_updates
                ).execute()
            except HttpError as e:
                logging.warning(f'[google_client.insert_event] Request Error: {e.status_code}/{e.error_details}')
                raise EventNotCreatedException()

        return response

    def patch_event(self, calendar_id, event_id, body, token, send_updates='all'):
        response = None
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                response = (
                    service.events()
                    .patch(calendarId=calendar_id, eventId=event_id, body=body, sendUpdates=send_updates)
                    .execute()
                )
            except HttpError as e:
                logging.warning(f'[google_client.patch_event] Request Error: {e.status_code}/{e.error_details}')
                raise EventNotPatchedException()

        return response

    def delete_event(self, calendar_id, event_id, token, send_updates='none'):
        response = None
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                response = (
                    service.events()
                    .delete(calendarId=calendar_id, eventId=event_id, sendUpdates=send_updates)
                    .execute()
                )
            except HttpError as e:
                logging.warning(f'[google_client.delete_event] Request Error: {e.status_code}/{e.error_details}')
                raise EventNotDeletedException()

        return response

    def watch_events(self, calendar_id, webhook_url, token):
        """Register a push notification channel for calendar event changes.
        Ref: https://developers.google.com/calendar/api/v3/reference/events/watch"""
        channel_id = str(uuid.uuid4())
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                response = service.events().watch(
                    calendarId=calendar_id,
                    body={
                        'id': channel_id,
                        'type': 'web_hook',
                        'address': webhook_url,
                    },
                ).execute()
            except HttpError as e:
                logging.error(f'[google_client.watch_events] Request Error: {e.status_code}/{e.error_details}')
                return None

        return response

    def stop_channel(self, channel_id, resource_id, token):
        """Stop a push notification channel.
        Ref: https://developers.google.com/calendar/api/v3/reference/channels/stop"""
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                service.channels().stop(
                    body={
                        'id': channel_id,
                        'resourceId': resource_id,
                    },
                ).execute()
            except HttpError as e:
                logging.warning(f'[google_client.stop_channel] Request Error: {e.status_code}/{e.error_details}')

    def list_events_sync(self, calendar_id, sync_token, token):
        """Fetch events that changed since the last sync token.
        Ref: https://developers.google.com/calendar/api/v3/reference/events/list (incremental sync)"""
        items = []
        next_sync_token = None

        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            page_token = None
            while True:
                try:
                    params = {
                        'calendarId': calendar_id,
                        'syncToken': sync_token,
                    }
                    if page_token:
                        params['pageToken'] = page_token

                    response = service.events().list(**params).execute()
                    items += response.get('items', [])
                    page_token = response.get('nextPageToken')
                    if not page_token:
                        next_sync_token = response.get('nextSyncToken')
                        break
                except HttpError as e:
                    if e.status_code == 410:
                        logging.info('[google_client.list_events_sync] Sync token expired, full sync needed')
                        return None, None
                    logging.warning(
                        f'[google_client.list_events_sync] Request Error: {e.status_code}/{e.error_details}'
                    )
                    break

        return items, next_sync_token

    def get_initial_sync_token(self, calendar_id, token):
        """Perform an initial list to obtain a sync token without fetching all events."""
        with build('calendar', 'v3', credentials=token, cache_discovery=False) as service:
            try:
                page_token = None
                while True:
                    params = {
                        'calendarId': calendar_id,
                        'maxResults': 250,
                    }
                    if page_token:
                        params['pageToken'] = page_token
                    response = service.events().list(**params).execute()
                    page_token = response.get('nextPageToken')
                    if not page_token:
                        return response.get('nextSyncToken')
            except HttpError as e:
                logging.error(
                    f'[google_client.get_initial_sync_token] Request Error: {e.status_code}/{e.error_details}'
                )
                return None

    def sync_calendars(self, db, subscriber_id: int, token, external_connection_id: int | None = None):
        # Grab all the Google calendars
        calendars = self.list_calendars(token)
        error_occurred = False

        for calendar in calendars:
            cal = CalendarConnection(
                title=calendar.get('summary'),
                color=calendar.get('backgroundColor'),
                user=calendar.get('id'),
                password='',
                url=calendar.get('id'),
                provider=CalendarProvider.google,
            )

            # add calendar
            try:
                repo.calendar.update_or_create(
                    db=db,
                    calendar=cal,
                    calendar_url=calendar.get('id'),
                    subscriber_id=subscriber_id,
                    external_connection_id=external_connection_id,
                )
            except Exception as err:
                logging.warning(
                    f'[google_client.sync_calendars] Error occurred while creating calendar. Error: {str(err)}'
                )
                error_occurred = True
        return error_occurred
