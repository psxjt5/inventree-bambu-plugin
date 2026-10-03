# Inventree Bambu Plugin
Bambu Lab 3D Printing Support for InvenTree

This plugin requires the [Inventree-3D-Printing](https://github.com/psxjt5/inventree-3d-printing) plugin to be installed (which provides the ```3D Printer``` machine type).

To aid with developing 3D printer plugins for other printer types, a significant amount of the functionality of this plugin will soon be moving into the [Inventree-3D-Printing](https://github.com/psxjt5/inventree-3d-printing), enabling elements such as the dashboard widget to work across all connected printers (and not just Bambu Lab ones).

## Current Capabilities
Development of this plugin is still ongoing. Current capabilities include the ability to:
- Add a printer into InvenTree's Machine Registry (within the Admin Center).
- Continually communicate with each printer via MQTT to retrieve printer data (status etc.).
- Show each printer, it's job progress, status and current file in a dashboard widget.
- Receive notifications for various printer events (Printer Online, Printer Offline, Print Started, Print Stopped, Printer Error, Print Paused, Print Resumed, Print Finished).
- Monitor all printers in the "3D Printing" panel in under the InvenTree Manufacturing module.
- Use the "Details" buttons in the Manufacturing module to see printer details.

Admin Center Machine Registry with Bambu Lab printers connected:

<img height="300" alt="image" src="https://github.com/user-attachments/assets/72c84a69-e7bc-4ef4-8cbd-4b65db8bbd99" />

Dashboard Widget showing print status:

<img height="150" alt="image" src="https://github.com/user-attachments/assets/d8225385-75f1-4882-8000-eb61bbf372e5" />

Printer Notifications:

<img height="150" height="201" alt="image" src="https://github.com/user-attachments/assets/5bdddf9e-7702-4579-b8b6-2db164e4ffaf" />

Manufacturing Panel showing printer tiles:

<img height="300" alt="image" src="https://github.com/user-attachments/assets/3d4ec0f9-0fba-4cab-8b31-d90ecc3c6325" />

Printer details page:

<img width="1896" height="1036" alt="image" src="https://github.com/user-attachments/assets/f864cb30-121d-47d2-a6cc-589b6bf40659" />

AMS details page:

<img width="1886" height="668" alt="image" src="https://github.com/user-attachments/assets/989b8f4f-9075-4849-9701-3cc241e8f0a5" />

## Roadmap
- Additional printer details panels.
- Printer control (start and stop jobs, run maintenance tasks etc.)
- Stock updates as prints are finished.
- Ability to queue print jobs.

## Registering a Bambu Lab 3D Printer
With the plugin installed, a Bambu Lab 3D printer can be added within the Machines Page (in the Admin Centre):

<img height="400" alt="image" src="https://github.com/user-attachments/assets/a4b5f860-4262-4e7d-a1bd-6a1ee7ad8599" />

The newly-created 3D Printer machine will open in a side-pane. Fill in the required properties (IP Address, Access Code, Serial Number):

<img height="200" alt="image" src="https://github.com/user-attachments/assets/8ef3801d-31c0-46a3-b220-778a40e0af9c" />

Restart the machine (using the dots menu in the top-right corner of the pane):

<img height="300" alt="image" src="https://github.com/user-attachments/assets/2b0734f8-a57f-460b-a66d-d8a90fd6584c" />




