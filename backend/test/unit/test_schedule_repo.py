import uuid
from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from appointment.database import repo
from defines import TEST_USER_ID


class TestScheduleSlug:
    def test_slug_taken_returns_false_when_unused(self, with_db):
        with with_db() as db:
            assert repo.schedule.slug_taken(db, 'unused01') is False

    def test_slug_taken_returns_true_when_slug_is_in_use(self, with_db, make_schedule):
        make_schedule(slug='taken001')

        with with_db() as db:
            assert repo.schedule.slug_taken(db, 'taken001') is True

    def test_slug_available_for_schedule_allows_unchanged_slug(self, with_db, make_schedule):
        schedule = make_schedule(slug='taken001')

        with with_db() as db:
            assert repo.schedule.slug_available_for_schedule(db, 'taken001', schedule.id) is True

    def test_slug_available_for_schedule_rejects_other_schedule_slug(self, with_db, make_schedule):
        make_schedule(slug='taken001')
        other = make_schedule(slug='other001')

        with with_db() as db:
            assert repo.schedule.slug_available_for_schedule(db, 'taken001', other.id) is False

    def test_get_by_slug_is_scoped_to_owner(
        self, with_db, make_schedule, make_pro_subscriber, make_caldav_calendar
    ):
        slug = 'scoped01'
        make_schedule(slug=slug)

        other_subscriber = make_pro_subscriber()
        make_caldav_calendar(subscriber_id=other_subscriber.id, connected=True)

        with with_db() as db:
            assert repo.schedule.get_by_slug(db, slug, TEST_USER_ID) is not None
            assert repo.schedule.get_by_slug(db, slug, other_subscriber.id) is None
            assert repo.schedule.slug_taken(db, slug) is True

    def test_generate_slug_returns_existing_slug(self, with_db, make_schedule):
        schedule = make_schedule(slug='existing1')

        with with_db() as db:
            result = repo.schedule.generate_slug(db, schedule.id)

        assert result == 'existing1'

    def test_generate_slug_assigns_unique_slug(self, with_db, make_schedule):
        schedule = make_schedule(slug=None)

        with with_db() as db:
            result = repo.schedule.generate_slug(db, schedule.id)

        assert result is not None
        assert len(result) == 8

        with with_db() as db:
            saved = repo.schedule.get(db, schedule.id)
            assert saved.slug == result

    def test_generate_slug_avoids_cross_owner_collision(
        self, with_db, make_schedule, make_pro_subscriber, make_caldav_calendar
    ):
        make_schedule(slug='deadbeef')

        other_subscriber = make_pro_subscriber()
        other_calendar = make_caldav_calendar(subscriber_id=other_subscriber.id, connected=True)
        other_schedule = make_schedule(slug=None, calendar_id=other_calendar.id)

        collision_uuid = uuid.UUID('00000000-0000-0000-0000-0000deadbeef')
        unique_uuid = uuid.UUID('00000000-0000-0000-0000-0000cafebabe')

        with patch('appointment.database.repo.schedule.uuid.uuid4') as mock_uuid:
            mock_uuid.side_effect = [collision_uuid, unique_uuid]

            with with_db() as db:
                result = repo.schedule.generate_slug(db, other_schedule.id)

        assert result == 'cafebabe'

    def test_generate_slug_returns_none_when_all_attempts_collide(self, with_db, make_schedule):
        make_schedule(slug='deadbeef')
        schedule = make_schedule(slug=None)

        collision_uuid = uuid.UUID('00000000-0000-0000-0000-0000deadbeef')

        with patch('appointment.database.repo.schedule.uuid.uuid4', return_value=collision_uuid):
            with with_db() as db:
                result = repo.schedule.generate_slug(db, schedule.id)

        assert result is None

    def test_generate_slug_retries_on_integrity_error(self, with_db, make_schedule):
        schedule = make_schedule(slug=None)
        unique_uuid = uuid.UUID('00000000-0000-0000-0000-0000cafebabe')

        with patch('appointment.database.repo.schedule.slug_taken', return_value=False):
            with patch('appointment.database.repo.schedule.uuid.uuid4', return_value=unique_uuid):
                with with_db() as db:
                    real_commit = db.commit
                    attempts = 0

                    def commit_once_then_succeed():
                        nonlocal attempts
                        attempts += 1
                        if attempts == 1:
                            raise IntegrityError('insert', {}, Exception('duplicate key'))
                        return real_commit()

                    with patch.object(db, 'commit', side_effect=commit_once_then_succeed):
                        result = repo.schedule.generate_slug(db, schedule.id)

        assert result == 'cafebabe'
        assert attempts == 2
