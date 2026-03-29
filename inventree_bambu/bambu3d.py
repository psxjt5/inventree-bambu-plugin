from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

from inventree_3d.threed import ThreeDPrinterBaseDriver

class BambuLab3DPrinterDriver(ThreeDPrinterBaseDriver):
    """Base driver for 3D printer machines."""

    machine_type = '3d-printer'

    USE_BACKGROUND_WORKER = True