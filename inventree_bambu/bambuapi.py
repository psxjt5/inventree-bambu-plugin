"""
BambuAPI: API methods for Bambu Lab printers.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .bambudata import BambuData

class BambuAPI:

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_printer_data(request, machine_serial):
        """Return data for a specific printer"""

        print("[BambuAPI] Get Printer Data")

        data = {
            "serial": machine_serial,
            "model": BambuData.getModel(machine_serial),
            "status": BambuData.getStatus(machine_serial),
            "progress": BambuData.getProgress(machine_serial),
            "layer_progress": BambuData.getLayerProgress(machine_serial),
            "current_layer": BambuData.getCurrentLayer(machine_serial),
            "total_layers": BambuData.getTotalLayers(machine_serial),
            "remaining_time": BambuData.getRemainingTime(machine_serial),
            "file_name": BambuData.getFileName(machine_serial),
            "nozzle_temperature": BambuData.getNozzleTemperature(machine_serial),
            "nozzle_target_temperature": BambuData.getNozzleTargetTemperature(machine_serial),
            "bed_temperature": BambuData.getBedTemperature(machine_serial),
            "bed_target_temperature": BambuData.getBedTargetTemperature(machine_serial),
            "cooling_fan_speed": BambuData.getCoolingFanSpeed(machine_serial),
            "heatbreak_fan_speed": BambuData.getHeatBreakFanSpeed(machine_serial),
            "big_fan_1_speed": BambuData.getBigFan1Speed(machine_serial),
            "big_fan_2_speed": BambuData.getBigFan2Speed(machine_serial),
            "ams_count": BambuData.getAMSUnitCount(machine_serial)
        }

        return Response(data)



