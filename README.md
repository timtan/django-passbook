django-passbook
===============

django-passbook is an implementation of the server-side components
of iOS's PassKit. It enables you to create passes to be used in
Passbook within iOS.

A simple webservice is provided to track pass updates and changes
as they occur on the device.

This is still a work in progress and is not yet ready for an official release.
Please feel free to fork and contribute.

Currently passes can be generated and edited from within the Django Admin.


## FEATURES

* Pass creation
* Pass editing
* Web service
* Push notifications for pass updates (forthcoming)


## GETTING STARTED

* Add `'passbook'` to your `INSTALLED_APPS` in your `settings.py` file.
* Run `python manage.py syncdb` to add the passbook database tables to your database.
