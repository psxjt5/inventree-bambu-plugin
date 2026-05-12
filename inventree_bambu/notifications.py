"""
Notifications: Delivers system notifications
"""

from common.notifications import trigger_notification
from django.contrib.auth import get_user_model

User = get_user_model()

class Notifications:

    def test_notification(machine):
        users = User.objects.filter(is_active=True)

        trigger_notification(
            obj=machine,
            category="machine.bambu",
            context={
                "name": "Test Notification",
                "message": f"Test Notification Text",
            },
        )