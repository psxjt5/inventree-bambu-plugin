from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _

from inventree_3d.threed import ThreeDPrinterBaseDriver

class BambuLab3DPrinterDriver(ThreeDPrinterBaseDriver):
    """BambuLab 3D Printing machine driver."""

    SLUG = "bambu-lab-3d-printer"
    NAME = "Bambu Lab 3D Printer"
    DESCRIPTION = "Bambu Lab 3D Printer driver for InvenTree"