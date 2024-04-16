# Portuguese Primatological Association website
This repository constains the source code for the Portuguese Primatological Association website server.

The website has three main goals:
- a simple set of pages presenting the association and its work
- a members management system (with a backoffice for internal use)
- a conference page that provides information about the conference and manages participants and abstract submissions (including a payment system for the registration)

The server has been implemented in [Flask 3.0](https://flask.palletsprojects.com/en/3.0.x/) and uses [fluent](https://projectfluent.org/) for i18n support. The html uses [bootstrap 5.3](https://getbootstrap.com/). The JS is vanilla, except for [Sortable.js](https://github.com/SortableJS/Sortable) library to manage the drag and drop features.