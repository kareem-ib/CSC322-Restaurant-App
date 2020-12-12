# CSC322-Restaurant-App
# Team I's Restaurant and Delivery Service Web-App
## Installing virtualenv
1) Type ```pip install virtualenv``` in cmd.
## Setting Up the virtualenv
1) Navigate to CSC322-Restaurant-App directory in cmd.
1) To create the virtual environment directory, type ```virtualenv venv```.
1) Type ```venv\Scripts\activate```.
1) In the virtual environment, type the following: ```pip install -r requirements.txt```.
1) To run the server, type ```py manage.py runserver``` in the virtual environment.
1) To access the website, type ```localhost:8000``` into your web browser.
## Creating an Admin and Using the System
1) In order to create another superuser, in the venv, type ```py manage.py createsuperuser``` and fill in the required fields.
1) Navigate to ```localhost:8000/admin``` in your web browser with the server running to access the admin page if you are logged in as an admin or to sign in as an admin if you are not. Here, the admin can browse through and edit all models.
1) To create a designated chef, give an existing chef the restaurant|dish|can add/delete/change/view permissions (Note: gramsay is a preexisting designated chef). To give the permissions, click on the desired user, scroll to the permissions field, and ctrl-click the four permissions.
1) Note for the instructor: the password for all existing users is the same as the class's Zoom meeting password.

## Note: The home and about pages have been left empty intentionally. Everything else mentioned in the specifications is functioning.

#### Note: Sometimes Windows will throw a ConnectionAbortedError [WinError 10053]. This error does not affect the system. You can proceed with testing normally if this error appears in the console.
