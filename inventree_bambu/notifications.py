"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model
from machine.models import MachineConfig

class Notifications:

    def test_notification(machine):
        print("[BambuLab3DPrintingNotifications] Sending Test Notification.")

        print(machine.pk, type(machine.pk))
        print(machine.uid, type(machine.uid))
        print(machine.id, type(machine.id))

        # User = get_user_model()

        # user = User.objects.filter(is_superuser=True)

        # machine = MachineConfig.objects.get(pk=machine.pk)

        # print(f"Machine UID: {getattr(machine, 'uid', None)}")

        # trigger_notification(
        #     obj=machine,
        #     category="system",
        #     targets=user,
        #     context={
        #         "name": "Test",
        #         "message": "Hello world",
        #     },
        #     check_recent=False,
        # )