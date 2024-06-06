import os

import pytest

from appointment.routes.commands import cron_lock


def test_cron_lock():
    """Test our cron lock function, this does use disk io but should clean itself up after."""
    test_lock_name = "test_cron_lock_run"
    test_lock_file_name = f"/tmp/{test_lock_name}.lock"

    # Clean up in case the lock file previously exists
    if os.path.isfile(test_lock_file_name):
        os.remove(test_lock_file_name)

    # Test that the lock works
    with cron_lock(test_lock_name):
        assert os.path.isfile(test_lock_file_name)

    # And cleans itself up
    assert not os.path.isfile(test_lock_file_name)

    # Test a lock already exists case with way too many withs.
    with open(test_lock_file_name, "w"):
        with pytest.raises(FileExistsError):
            with cron_lock(test_lock_name):
                pass

    # Remove the lock file we manually created
    os.remove(test_lock_file_name)
