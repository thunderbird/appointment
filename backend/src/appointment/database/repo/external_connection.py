"""Module: repo.external_connection

Repository providing CRUD functions for external_connection database models.
"""

from sqlalchemy.orm import Session
from .. import models
from ..schemas import ExternalConnection


"""External Connections repository functions
"""


def create(db: Session, external_connection: ExternalConnection):
    db_external_connection = models.ExternalConnections(**external_connection.model_dump())
    db.add(db_external_connection)
    db.commit()
    db.refresh(db_external_connection)
    return db_external_connection


def update_token(
    db: Session, token: str, subscriber_id: int, type: models.ExternalConnectionType, type_id: str | None = None
):
    db_results = get_by_type(db, subscriber_id, type, type_id)
    if db_results is None or len(db_results) == 0:
        return None

    db_external_connection = db_results[0]
    db_external_connection.token = token
    db.commit()
    db.refresh(db_external_connection)
    return db_external_connection


def delete_by_type(db: Session, subscriber_id: int, type: models.ExternalConnectionType, type_id: str):
    connections = get_by_type(db, subscriber_id, type, type_id)

    # There should be one by type id, but just in case..
    for connection in connections:
        db.delete(connection)
    db.commit()

    return True


def get_by_type(
    db: Session, subscriber_id: int, type: models.ExternalConnectionType, type_id: str | None = None
) -> list[models.ExternalConnections] | None:
    """Return a subscribers external connections by type, and optionally type id"""
    query = (
        db.query(models.ExternalConnections)
        .filter(models.ExternalConnections.owner_id == subscriber_id)
        .filter(models.ExternalConnections.type == type)
    )

    if type_id is not None:
        query = query.filter(models.ExternalConnections.type_id == type_id)

    result = query.all()

    return result


def get_subscriber_by_accounts_uuid(db: Session, uuid: str):
    """Return a subscriber from an accounts uuid"""
    query = (
        db.query(models.ExternalConnections)
        .filter(models.ExternalConnections.type == models.ExternalConnectionType.accounts)
        .filter(models.ExternalConnections.type_id == uuid)
    )

    result = query.first()

    if result is not None:
        return result.owner

    return None


def get_subscriber_by_fxa_uid(db: Session, type_id: str):
    """Return a subscriber from a fxa profile uid"""
    query = (
        db.query(models.ExternalConnections)
        .filter(models.ExternalConnections.type == models.ExternalConnectionType.fxa)
        .filter(models.ExternalConnections.type_id == type_id)
    )

    result = query.first()

    if result is not None:
        return result.owner

    return None


def get_subscriber_by_zoom_user_id(db: Session, type_id: str):
    """Return a subscriber from a zoom user id"""
    query = (
        db.query(models.ExternalConnections)
        .filter(models.ExternalConnections.type == models.ExternalConnectionType.zoom)
        .filter(models.ExternalConnections.type_id == type_id)
    )

    result = query.first()

    if result is not None:
        return result.owner

    return None
