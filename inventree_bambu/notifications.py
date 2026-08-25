"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model
from machine.models import MachineConfig
from django.db import DataError

import traceback

class Notifications:

    @staticmethod
    def setup_group_notification(plugin_config):
        print("[BambuLab3DPrintingNotifications] Sending Group Setup Notification.")
        
        User = get_user_model()

        user = User.objects.filter(is_superuser=True)

        # Temporary workaround for InvenTree UUID NotificationEntry issue.
        # Remove once upstream fix is available.
        try:
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
        except DataError as exc:
            if "integer out of range" not in str(exc):
                raise

            print(
                "[BambuLab3DPrintingNotifications] "
                "Notification delivered, but InvenTree NotificationEntry "
                "tracking failed due to UUID/integer incompatibility."
            )

    def test_notification(self, machine):
        print("[BambuLab3DPrintingNotifications] Sending Test Notification.")

        User = get_user_model()

        user = User.objects.filter(is_superuser=True)

        machine = MachineConfig.objects.get(pk=machine.pk)

        # Temporary workaround for InvenTree UUID NotificationEntry issue.
        # Remove once upstream fix is available.
        try:
            trigger_notification(
                obj=machine,
                category="machine.3dprinting.bambu_lab",
                targets=user,
                context={
                    "name": "Test",
                    "message": "Hello world",
                    "link": "/web/"
                },
                check_recent=False,
            )
        except DataError as exc:
            if "integer out of range" not in str(exc):
                raise

            print(
                "[BambuLab3DPrintingNotifications] "
                "Notification delivered, but InvenTree NotificationEntry "
                "tracking failed due to UUID/integer incompatibility."
            )