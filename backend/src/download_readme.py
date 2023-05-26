import datetime


def get_download_readme():
    """Returns the localized download readme"""
    return """
============================================
Thunderbird Appointment Data Download Readme
============================================

Time of download (UTC): {download_time}

Included in this zip is all of your user data from our system in .csv format.

============================================
How Do I View it?
============================================

You can open these .csv files in a variety applications like:
 - Microsoft Excel
 - Google Sheets
 - Numbers
 - LibreOffice Calc

============================================
What's Included?
============================================

Note: If a file is empty or blank then we don't have that type of data on record for you.

The following files are included:
 - appointments.csv : A list of Appointments from our database
 - attendees.csv : A list of Appointment Slot Attendees from our database
 - calendars.csv : A list of Calendars from our database
 - slots.csv : A list of Appointment Slots from our database.
 - subscriber.csv : The personal information we store about you from our database.
 - readme.txt : This file!
            """.format(download_time=datetime.datetime.utcnow())
