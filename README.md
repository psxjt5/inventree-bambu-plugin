# Inventree Bambu Plugin
Bambu Lab 3D Printing Support for InvenTree

This plugin requires the [Inventree-3D-Printing](https://github.com/psxjt5/inventree-3d-printing) plugin to be installed (which provides the ```3D Printer``` machine type).

To aid with developing 3D printer plugins for other printer types, a significant amount of the functionality of this plugin will soon be moving into the [Inventree-3D-Printing](https://github.com/psxjt5/inventree-3d-printing), enabling elements such as the dashboard widget to work across all connected printers (and not just Bambu Lab ones).

## Current Capabilities
Development of this plugin is still ongoing. Current capabilities include the ability to:
- Add a printer into InvenTree's Machine Registry (within the Admin Center).
- Continually communicate with each printer via MQTT to retrieve printer data (status etc.).
- Show each printer, it's job progress, status and print file in a dashboard widget.

Admin Center Machine Registry with Bambu Lab printers connected:

<img height="300" alt="image" src="https://github.com/user-attachments/assets/72c84a69-e7bc-4ef4-8cbd-4b65db8bbd99" />

Dashboard Widget showing print status:

<img height="150" alt="image" src="https://github.com/user-attachments/assets/d8225385-75f1-4882-8000-eb61bbf372e5" />

## Roadmap
- Printer status notifications.
- Ability to manage and control printers through a panel in the Manufacturing module of InvenTree.
- Ability to queue print jobs.
- Stock updates as prints are finished.

## Registering a Bambu Lab 3D Printer
With the plugin installed, a Bambu Lab 3D printer can be added within the Machines Page (in the Admin Centre):

<img height="400" alt="image" src="https://github.com/user-attachments/assets/a4b5f860-4262-4e7d-a1bd-6a1ee7ad8599" />

The newly-created 3D Printer machine will open in a side-pane. Fill in the required properties (IP Address, Access Code, Serial Number):

<img height="200" alt="image" src="https://github.com/user-attachments/assets/8ef3801d-31c0-46a3-b220-778a40e0af9c" />

Restart the machine (using the dots menu in the top-right corner of the pane):

<img height="300" alt="image" src="https://github.com/user-attachments/assets/2b0734f8-a57f-460b-a66d-d8a90fd6584c" />




