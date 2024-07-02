import os

import sentry_sdk
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks
from ..database import repo, schemas

from ..dependencies.database import get_db
from ..exceptions import validation
from ..tasks.emails import send_confirm_email
from itsdangerous import URLSafeSerializer, BadSignature
from secrets import token_bytes
from enum import Enum

router = APIRouter()


class WaitingListAction(Enum):
    CONFIRM_EMAIL = 1
    LEAVE = 2


@router.post('/join')
def join_the_waiting_list(
    data: schemas.JoinTheWaitingList, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Join the waiting list!"""
    added = repo.invite.add_to_waiting_list(db, data.email)

    # TODO: Replace our signed functionality with this
    # Not timed since we don't have a mechanism to re-send these...
    serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')
    confirm_token = serializer.dumps({'email': data.email, 'action': WaitingListAction.CONFIRM_EMAIL.value})
    decline_token = serializer.dumps({'email': data.email, 'action': WaitingListAction.LEAVE.value})

    # If they were added, send the email
    if added:
        background_tasks.add_task(send_confirm_email, to=data.email, confirm_token=confirm_token, decline_token=decline_token)

    return added


@router.post('/action')
def act_on_waiting_list(
    data: schemas.TokenForWaitingList,
    db: Session = Depends(get_db)
):
    """Perform a waiting list action from a signed token"""
    serializer = URLSafeSerializer(os.getenv('SIGNED_SECRET'), 'waiting-list')

    try:
        token_data = serializer.loads(data.token)
    except BadSignature:
        raise validation.InvalidLinkException()

    action = token_data.get('action')
    email = token_data.get('email')

    if action is None or email is None:
        raise validation.InvalidLinkException()

    if action == WaitingListAction.CONFIRM_EMAIL.value:
        success = repo.invite.confirm_waiting_list_email(db, email)
    elif action == WaitingListAction.LEAVE.value:
        success = repo.invite.remove_waiting_list_email(db, email)
    else:
        raise validation.InvalidLinkException()

    # This shouldn't happen, but just in case!
    if not success:
        exception = validation.WaitingListActionFailed()

        # Capture this issue in sentry
        sentry_sdk.capture_exception(exception)

        raise exception

    return {
        'action': action,
        'success': success,
    }
