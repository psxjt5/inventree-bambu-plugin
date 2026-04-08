"""
URLs: Maintains a list of API endpoint URLs.
"""

from django.urls import path
from .api import example_endpoint

urlpatterns = [
    path("example/", example_endpoint),
]