Pretix Acronia Check-in View
============================

This is a plugin for `pretix`_ that creates an extra page under "checkins" in the pretix admin frontend to show the number of check-ins per person.

Features
--------

* Display check-in statistics for each order position/person
* Summary statistics showing total persons with check-ins and total check-ins
* Highlight persons with multiple check-ins
* Search functionality to filter by order code, attendee name, email, or product
* Pagination for large events
* Direct links to order and position details
* Fully localized in German and English

Installation
------------

1. Install the plugin from the pretix marketplace or manually
2. Enable the plugin in your pretix installation
3. The plugin will automatically appear in the event control panel navigation

Usage
-----

1. Navigate to your event in the pretix admin interface
2. Go to "Orders" → "Check-ins" 
3. You will see a new "Check-in Statistics" option in the navigation
4. Click on it to view the check-in statistics for your event

The page displays:

* **Summary section**: Total persons with check-ins, total check-ins, and persons with multiple check-ins
* **Search functionality**: Filter results by order code, attendee name, email, or product name
* **Detailed table**: Shows each person's check-in count with direct links to order details
* **Visual indicators**: Different colored badges for single vs. multiple check-ins

Development setup
-----------------

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.

This plugin has CI set up to enforce a few code style rules. To check locally, you need these packages installed::

    pip install flake8 isort black

To check your plugin for rule violations, run::

    black --check .
    isort -c .
    flake8 .

You can auto-fix some of these issues by running::

    isort .
    black .

To automatically check for these issues before you commit, you can run ``.install-hooks``.


License
-------

Copyright 2025 Nora Küchler

Released under the terms of the proprietary pretix Enterprise license.

.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html



.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html
