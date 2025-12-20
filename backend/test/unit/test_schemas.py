import pytest
from pydantic import ValidationError

from appointment.database.schemas import SubscriberIn


def test_subscriber_in_strip_whitespace_username():
    """Test that whitespace is stripped from username"""
    data = SubscriberIn(username='  testuser  ', name='Valid Name')
    assert data.username == 'testuser'


def test_subscriber_in_strip_whitespace_name():
    """Test that whitespace is stripped from name"""
    data = SubscriberIn(username='validuser', name='  Test Name  ')
    assert data.name == 'Test Name'


def test_subscriber_in_username_empty_after_strip():
    """Test that username containing only whitespace fails validation"""
    with pytest.raises(ValidationError) as exc:
        SubscriberIn(username='   ')

    errors = exc.value.errors()
    assert any(e['loc'] == ('username',) and 'String should have at least 1 character' in e['msg'] for e in errors)


def test_subscriber_in_name_empty_after_strip():
    """Test that name containing only whitespace fails validation"""
    with pytest.raises(ValidationError) as exc:
        SubscriberIn(username='validuser', name='   ')

    errors = exc.value.errors()
    assert any(e['loc'] == ('name',) and 'String should have at least 1 character' in e['msg'] for e in errors)


def test_subscriber_in_mixed_whitespace():
    """Test mixed scenarios"""
    data = SubscriberIn(username='\tuser\n', name='\rname\t')
    assert data.username == 'user'
    assert data.name == 'name'
