"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model
from machine.models import MachineConfig

User = get_user_model()

class Notifications:

    def test_notification(machine):
        print("[BambuLab3DPrintingNotifications] Sending Test Notification.")

        users = User.objects.filter(is_active=True)

        # trigger_notification(
        #     obj=machine,
        #     category="machine.bambu",
        #     targets=users,
        #     context={
        #         "name": "Test Notification",
        #         "message": f"Test Notification Text",
        #     },
        # )

        machine = MachineConfig.objects.get(pk=machine.pk)

        trigger_notification(
            obj=machine,
            category="system",
            targets=User.objects.filter(is_superuser=True),
            context={
                "name": "HELLO",
                "message": "If you see this, pipeline works",
            },
        )