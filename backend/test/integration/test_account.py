import os
from uuid import uuid4
from appointment.database.models import ExternalConnectionType
from defines import auth_headers, TEST_USER_ID


class TestAccount:
    def test_account_get_external_connections(self, with_client, make_external_connections):
        # add a couple of external connections to our test user
        type_id = str(uuid4())
        zoom_ec = make_external_connections(TEST_USER_ID, type=ExternalConnectionType.zoom, type_id=type_id)
        assert zoom_ec.type_id == type_id
        google_ec = make_external_connections(TEST_USER_ID, type=ExternalConnectionType.google, type_id=type_id)
        assert google_ec.type_id == type_id

        # now get the list of our external connections and verify
        response = with_client.get('/account/external-connections', headers=auth_headers)

        assert response.status_code == 200, response.text
        ext_connections = response.json()
        zoom_connections = ext_connections.get('zoom', None)
        assert len(zoom_connections) == 1
        assert zoom_connections[0]['owner_id'] == TEST_USER_ID
        assert zoom_connections[0]['name'] == zoom_ec.name
        google_connections = ext_connections.get('google', None)
        assert len(google_connections) == 1
        assert google_connections[0]['owner_id'] == TEST_USER_ID
        assert google_connections[0]['name'] == google_ec.name

    def test_account_available_emails(self, with_client, make_external_connections):
        # currently we have one email available
        test_user_email = os.environ.get('TEST_USER_EMAIL')
        user_email_list = [test_user_email]

        # get available emails and confirm
        response = with_client.get('/account/available-emails', headers=auth_headers)

        assert response.status_code == 200, response.text
        email_list_ret = response.json()
        assert email_list_ret == user_email_list

        # now add another email/name via a google connection
        type_id = str(uuid4())
        google_ec = make_external_connections(TEST_USER_ID, type=ExternalConnectionType.google, type_id=type_id)
        user_email_list.append(google_ec.name)

        # get available emails again and confirm new one was added
        response = with_client.get('/account/available-emails', headers=auth_headers)

        assert response.status_code == 200, response.text
        email_list_ret = response.json()
        assert email_list_ret == user_email_list
