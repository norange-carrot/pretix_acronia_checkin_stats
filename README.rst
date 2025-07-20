Pretix Acronia Check-in View
============================

This is a plugin for `pretix`_ that creates an extra page under "Check-In" in the pretix admin frontend to show the number of check-ins per product/person compared to the number of booked helper add-ons.

Features
--------

* Display check-in statistics for each order position/person
* Summary statistics giving an overview of missing and completed duties
* Search functionality to filter by order code, attendee name, email, product, or number of missing/completed duties
* Pagination for large events
* Direct links to order details
* Export functionality to export the current filtered data as CSV
* Fully localized in German and English

Installation
------------
For developers, see the `Development setup`_ section below.
1. Clone this repository into your pretix plugins directory
   (usually `src/pretix/plugins/`).
2. Add this to 'your setup.py' or `settings.py` file:
   ```python
    setup(
        args...,
        entry_points="""
    [pretix.plugin]
    pretix_paypal=pretix_paypal:PretixPluginMeta"
)
  ```python
   (or add it to your `plugins` setting in `settings.py` if you are not using a setup.py file directly
3. Start the server.
4. Enable the plugin in your pretix installation
5. The plugin will automatically appear in the event control panel navigation und "Check-In"

Usage
-----

1. Navigate to your event in the pretix admin interface
2. Go to "Check-In"
3. You will see a new "Check-in Helper Statistics" menu item in the navigation
4. Click on it to view the check-in statistics for the event

The page displays:

* **Summary section**: Gives an overview of total number of tickets in the check-in list and number of tickets with completed or uncompleted duties
* **Export functionality**: Export the current filtered data as CSV. If no fiters are chosen, it will export all data.
* **Search functionality**: Filter results by order code, attendee name, email, product name, number of missing duties and number of completed duties
* **Detailed table**: Shows each person's check-in count with direct links to order details
* **Visual indicators**: Different colored badges for missing vs. completed duties

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
