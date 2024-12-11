--------------
Updating Legal
--------------

Legal documents are not hand-built but transformed from markdown to html via a backend command. Originally this was to automatically grab the latest privacy policy and terms of service documents from Mozilla's legal repository.

Requirements
------------

* Ensure you have both ``TBA_PRIVACY_POLICY_LOCATION`` and ``TBA_TERMS_OF_USE_LOCATION`` set in your .env or system environment.
* Ensure you have the backend setup as per the backend's readme file.

Updating Local Legal Markdown
-----------------------------

If you're tasked with updating a legal document that's not on a remote server you'll need to download the Google Document as a markdown file and place it in `appointment/legal`. If the file is not already hooked up with one of the two env variables above please do so.


Downloading And Rendering The Latest Documents
----------------------------------------------

Run the following command from the backend folder:

.. code-block:: shell

  run-command main download-legal

This will download / render the markdown files to html and place them in ``appointment/backend/tmp/legal/en/*.html``.

Updating The Frontend Legal Html Files
--------------------------------------

Once you've downloaded and rendered the markdown files to html you can copy the files directly to the frontend's legal assest folder located in: `appointment/frontend/src/assets/legal/en`.
