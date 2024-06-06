from ..database import repo
from ..dependencies.database import get_engine_and_session


def run(n: int):
    print(f"Generating {n} new invite codes...")

    _, session = get_engine_and_session()
    db = session()

    codes = repo.invite.generate_codes(db, n)

    db.close()

    print(f"Successfull added {len(codes)} shiny new invite codes to the database.")
