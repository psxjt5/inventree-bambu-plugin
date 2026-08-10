"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model
from machine.models import MachineConfig
from django.db import DataError

import traceback

class Notifications:

    def test_notification(machine):
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