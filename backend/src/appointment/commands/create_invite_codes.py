import os
import uuid

from ..database import models, schemas
from ..dependencies.database import get_engine_and_session


def run(n: int = 50):
    print(f"Generating {n} new invite codes...")

    codes = [str(uuid.uuid4()) for _ in range(n)]

    _, session = get_engine_and_session()
    db = session()

    for code in codes:
        invite = schemas.Invite(code=code)
        db_invite = models.Invite(**invite.dict())
        db.add(db_invite)
        db.commit()

    db.close()

    print(f"Successfull added {len(codes)} shiny new invite codes to the database.")
