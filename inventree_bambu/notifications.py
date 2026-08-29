"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model
from machine.models import MachineConfig
from plugin import registry
from django.db import DataError

import traceback

class Notifications:

    # Gets the user recipients for 3D Printing Notifications (Member of the 3D printing group and notification enabled in user settings).
    @staticmethod
    def _get_notification_users(notificationName):
        print("[BambuLab3DPrintingNotifications] Getting Notification Users")

        plugin = registry.get_plugin('inventree_bambu')

        # Get the THREED_GROUP plugin setting.
        group_id = plugin.get_setting('THREED_GROUP')

        # Return if not set.
        if not group_id:
            return []

        # Get the users in the THREED_GROUP
        users = get_user_model().objects.filter(
            is_active=True,
            groups__pk=group_id,
        ).distinct()

        # Filter down to the users in the group, with the notification enabled.
        users = [
            user for user in users
            if plugin.get_user_setting(
                notificationName,
                user,
                backup_value=True,
            )
        ]

        return users

    @staticmethod
    def print_started_notification(machine):
        print(f"[BambuLab3DPrintingNotifications] Sending Print Started Notification for {machine.name}.")

        users = Notifications._get_notification_users("NOTIFY_PRINT_START")
        
        machine = MachineConfig.objects.get(pk=machine.pk)

        trigger_notification(
            obj=machine,
            category="machine.3dprinting.bambu_lab.print_started",
            targets=users,
            context={
                "name": f"Print Started - {machine.name}",
                "message": "A print has been started.",
                "link": "/"
            },
            check_recent=False,
        )

    @staticmethod
    def print_error_notification(machine):
        print(f"[BambuLab3DPrintingNotifications] Sending Print Error Notification for {machine.name}.")
        
        users = Notifications._get_notification_users("NOTIFY_PRINT_ERROR")
        
        machine = MachineConfig.objects.get(pk=machine.pk)

        trigger_notification(
            obj=machine,
            category="machine.3dprinting.bambu_lab.print_error",
            targets=users,
            context={
                "name": f"Print Error - {machine.name}",
                "message": "A print error has occurred.",
                "link": "/"
            },
            check_recent=False,
        )

    @staticmethod
    def print_finished_notification(machine):
        print(f"[BambuLab3DPrintingNotifications] Sending Print Finished Notification for {machine.name}.")
        
        users = Notifications._get_notification_users("NOTIFY_PRINT_FINISHED")
        
        machine = MachineConfig.objects.get(pk=machine.pk)

        trigger_notification(
            obj=machine,
            category="machine.3dprinting.bambu_lab.print_started",
            targets=users,
            context={
                "name": f"Print Finished - {machine.name}",
                "message": "A print has finished.",
                "link": "/"
            },
            check_recent=False,
        )

    @staticmethod
    def printer_online_notification(machine):
        print(f"[BambuLab3DPrintingNotifications] Sending Printer Online Notification for {machine.name}.")
    
        users = Notifications._get_notification_users("NOTIFY_PRINTER_ONLINE")
        
        machine = MachineConfig.objects.get(pk=machine.pk)

        trigger_notification(
            obj=machine,
            category="machine.3dprinting.bambu_lab.printer_online",
            targets=users,
            context={
                "name": f"Printer Online - {machine.name}",
                "message": "A printer has come online.",
                "link": "/"
            },
            check_recent=False,
        )

    @staticmethod
    def printer_offline_notification(machine):
        print(f"[BambuLab3DPrintingNotifications] Sending Printer Offline Notification for {machine.name}.")
        
        users = Notifications._get_notification_users("NOTIFY_PRINTER_OFFLINE")
        
        machine = MachineConfig.objects.get(pk=machine.pk)

        trigger_notification(
            obj=machine,
            category="machine.3dprinting.bambu_lab.printer_offline",
            targets=users,
            context={
                "name": f"Printer Offline - {machine.name}",
                "message": "A printer has gone offline.",
                "link": "/"
            },
            check_recent=False,
        )

    # Notifies superusers that a 3D printing group needs to be defined.
    @staticmethod
    def setup_group_notification(plugin_config):
        print("[BambuLab3DPrintingNotifications] Sending Group Setup Notification.")
        
        User = get_user_model()

        user = User.objects.filter(is_superuser=True)

        trigger_notification(
            obj=plugin_config,
            category="machine.3dprinting.bambu_lab.setup",
            targets=user,
            context={
                "name": "Setup 3D Printing Group",
                "message": "Define a 3D Printing Group in settings.",
                "link": "/web/settings/admin/plugin/inventree_bambu/"
            },
            check_recent=False,
        )