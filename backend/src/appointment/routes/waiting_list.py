import os

import sentry_sdk
from slowapi import Limiter
from slowapi.util import get_remote_address
from posthog import Posthog
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from ..database import repo, schemas, models
from ..dependencies.auth import get_admin_subscriber

from ..dependencies.database import get_db
from ..dependencies.metrics import get_posthog
from ..exceptions import validation
from ..l10n import l10n
from ..tasks.emails import send_confirm_email, send_invite_account_email
from itsdangerous import URLSafeSerializer, BadSignature
from enum import Enum

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class WaitingListAction(Enum):
    CONFIRM_EMAIL = 1
    LEAVE = 2


@router.post('/join')
@limiter.limit("2/minute")
def join_the_waiting_list(
    request: Request,
    data: schemas.JoinTheWaitingList,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
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
        background_tasks.add_task(
            send_confirm_email, to=data.email, confirm_token=confirm_token, decline_token=decline_token
        )

    return added


@router.post('/action')
def act_on_waiting_list(data: schemas.TokenForWaitingList, db: Session = Depends(get_db)):
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
        # If they're a user already then tell the frontend to ship them to the settings page.
        waiting_list_entry = repo.invite.get_waiting_list_entry_by_email(db, email)

        if waiting_list_entry and waiting_list_entry.invite_id and waiting_list_entry.invite.subscriber_id:
            return {
                'action': action,
                'success': False,
                'redirectToSettings': True
            }

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


""" ADMIN ROUTES
These require get_admin_subscriber!
"""


@router.get('/', response_model=list[schemas.WaitingListAdminOut])
def get_all_waiting_list_users(db: Session = Depends(get_db), _: models.Subscriber = Depends(get_admin_subscriber)):
    """List all existing waiting list users, needs admin permissions"""
    response = db.query(models.WaitingList).all()
    return response


@router.post('/invite', response_model=schemas.WaitingListInviteAdminOut)
def invite_waiting_list_users(
    data: schemas.WaitingListInviteAdminIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    posthog: Posthog | None = Depends(get_posthog),
    admin: models.Subscriber = Depends(get_admin_subscriber),
):
    """Invites a list of ids to TBA
    For each waiting list id:
        - Retrieve the waiting list user model
        - If already invited or doesn't exist, skip to next loop iteration
        - If a subscriber with the same email exists then add error msg, and skip to the next loop iteration
        - Create new subscriber based on the waiting list user's email
        - If failed add the error msg, and skip to the next loop iteration
        - Create invite code
        - Attach the invite code to the subscriber and waiting list user
        - Send the 'You're invited' email to the new user's email
        - Done loop iteration!"""
    accepted = []
    errors = []

    for id in data.id_list:
        # Look the user up!
        waiting_list_user: models.WaitingList|None = (
            db.query(models.WaitingList).filter(models.WaitingList.id == id).first()
        )
        # If the user doesn't exist, or if they're already invited ignore them
        if not waiting_list_user or waiting_list_user.invite:
            continue

        subscriber_check = repo.subscriber.get_by_email(db, waiting_list_user.email)
        if subscriber_check:
            errors.append(l10n('wl-subscriber-already-exists', {'email': waiting_list_user.email}))
            continue

        # Create a new subscriber
        subscriber = repo.subscriber.create(
            db,
            schemas.SubscriberBase(
                email=waiting_list_user.email,
                username=waiting_list_user.email,
            ),
        )

        if not subscriber:
            errors.append(l10n('wl-subscriber-failed-to-create', {'email': waiting_list_user.email}))
            continue

        # Generate an invite for that waiting list user and subscriber
        invite_code = repo.invite.generate_codes(db, 1)[0]

        invite_code.subscriber_id = subscriber.id
        waiting_list_user.invite_id = invite_code.id

        # Update the waiting list user and invite code
        db.add(waiting_list_user)
        db.add(invite_code)
        db.commit()

        background_tasks.add_task(
            send_invite_account_email,
            date=waiting_list_user.time_created,
            to=subscriber.email,
            lang=subscriber.language
        )
        accepted.append(waiting_list_user.id)

    if posthog:
        posthog.capture(distinct_id=admin.unique_hash, event='apmt.admin.invited', properties={
            'from': 'waitingList',
            'waiting-list-ids': accepted,
            'errors-encountered': len(errors),
            'service': 'apmt'
        })

    return schemas.WaitingListInviteAdminOut(
        accepted=accepted,
        errors=errors,
    )
