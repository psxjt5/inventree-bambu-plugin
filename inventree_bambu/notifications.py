"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model
from machine.models import MachineConfig

import traceback

class Notifications:

    def test_notification(machine):
        print("[BambuLab3DPrintingNotifications] Sending Test Notification.")

        User = get_user_model()

        user = User.objects.filter(is_superuser=True)

        machine = MachineConfig.objects.get(pk=machine.pk)

        try:
            trigger_notification(
                obj=machine,
                category="system",
                targets=user,
                context={
                    "name": "Test",
                    "message": "Hello world",
                },
                check_recent=False,
            )
        except Exception:
            print("[BambuLab3DPrintingNotifications] NOTIFICATION FAILED")
            traceback.print_exc()
            raise