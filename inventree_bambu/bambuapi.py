"""
BambuAPI: API methods for Bambu Lab printers.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from machine.models import MachineConfig
from machine.models import MachineSetting
from machine.serializers import MachineConfigSerializer
from stock.models import StockLocation

from .bambudata import BambuData
from .bambuftpsservice import BambuFTPSService, BambuFTPSPathError

class BambuAPI:

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_dashboard_widget_data(request):
        """Return a list of registered printers, along with their serial numbers"""

        print("[BambuAPI] Get Dashboard Widget Data")

        machines = MachineConfig.objects.filter(
            machine_type='3d-printer',
            active=True
        )

        serializer = MachineConfigSerializer(machines, many=True)

        data = serializer.data

        simplified = [
            {
                "pk": m["pk"],
                "name": m["name"],
                "status": m["status"],
                "status_text": m["status_text"],
                "progress": next(
                    (p["value"] for p in m.get("properties", []) if p["key"] == "Job Progress"),
                    None
                ),
                "file_name": next(
                    (p["value"] for p in m.get("properties", []) if p["key"] == "File Name"),
                    None
                ),
            }
            for m in data
        ]

        return Response(simplified)

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_printer_tiles_data(request):
        """Return a list of registered printers, along with the data needed to present their tile in the manufacturing 3D printing dashboard"""

        print("[BambuAPI] Get Printer Tiles Data")

        machines = MachineConfig.objects.filter(
            machine_type='3d-printer',
            active=True
        )

        serializer = MachineConfigSerializer(machines, many=True)

        data = serializer.data

        simplified = [
            {
                "pk": m["pk"],
                "serial": MachineSetting.objects.get(
                    machine_config_id=m["pk"],
                    config_type=MachineSetting.ConfigType.DRIVER,
                    key="SERIAL",
                ).value,
                "name": m["name"],
                "status": m["status"],
                "status_text": m["status_text"],
                "manufacturer": "Bambu Lab",
                "model": next(
                    (p["value"] for p in m.get("properties", []) if p["key"] == "Model"),
                    None
                ),
                "progress": next(
                    (p["value"] for p in m.get("properties", []) if p["key"] == "Job Progress"),
                    None
                ),
                "file_name": next(
                    (p["value"] for p in m.get("properties", []) if p["key"] == "File Name"),
                    None
                ),
                "remaining_time": next(
                    (p["value"] for p in m.get("properties", []) if p["key"] == "Remaining Time"),
                    None
                ),
            }
            for m in data
        ]

        return Response(simplified)

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_printer_data(request, pk):
        """Return data for a specific printer"""

        print("[BambuAPI] Get Printer Data")

        machine = MachineConfig.objects.get(
            machine_type='3d-printer',
            pk=pk,
        )

        serializer = MachineConfigSerializer(machine)
        data = serializer.data

        properties = {
            p["key"]: p["value"]
            for p in data.get("properties", [])
        }

        serial = MachineSetting.objects.get(
            machine_config_id=pk,
            key="SERIAL",
        ).value

        location = MachineSetting.objects.filter(
            machine_config_id=pk,
            key="LOCATION",
        ).values_list("value", flat=True).first()

        location_name = None

        if location:
            location_name = StockLocation.objects.filter(
                pk=location,
            ).values_list("name", flat=True).first()

        return Response({
            "pk": pk,
            "serial": serial,
            "name": data["name"],
            "manufacturer": "Bambu Lab",
            "model": properties.get("Model"),
            "location": location,
            "location_name": location_name,
            "status": data["status"],
            "status_text": data["status_text"],
            "progress": properties.get("Job Progress"),
            "layer_progress": properties.get("Layer Progress"),
            "current_layer": properties.get("Current Layer"),
            "total_layers": properties.get("Total Layers"),
            "remaining_time": properties.get("Remaining Time"),
            "file_name": properties.get("File Name"),
            "nozzle_diameter": properties.get("Nozzle Diameter"),
            "nozzle_type": properties.get("Nozzle Type"),
            "nozzle_temperature": properties.get("Nozzle Temperature"),
            "nozzle_target_temperature": properties.get("Nozzle Target Temperature"),
            "bed_temperature": properties.get("Bed Temperature"),
            "bed_target_temperature": properties.get("Bed Target Temperature"),
            "chamber_temperature": properties.get("Chamber Temperature"),
            "cooling_fan_speed": properties.get("Cooling Fan Speed"),
            "heatbreak_fan_speed": properties.get("Heatbreak Fan Speed"),
            "big_fan_1_speed": properties.get("Big Fan 1 Speed"),
            "big_fan_2_speed": properties.get("Big Fan 2 Speed"),
            "ams_units": properties.get("AMS Units"),
            "ams_active_tray": BambuData.getAMSActiveTray(pk),
            "wifi_strength": BambuData.getWifiSignal(pk),
            "sdcard": BambuData.getSDCard(pk),
            "chamber_light": BambuData.getChamberLightStatus(pk),
            "work_light": BambuData.getWorkLightStatus(pk),
            "door_open": BambuData.getDoorOpenStatus(pk),
            "camera_present": BambuData.getCameraPresent(pk),
            "camera_url": BambuData.getCameraURL(pk),
            "camera_record": BambuData.getCameraRecordStatus(pk),
            "camera_timelapse": BambuData.getCameraTimelapseStatus(pk),
            "camera_resolution": BambuData.getCameraResolution(pk),
            "skip_parts_enabled": BambuData.getSkipPartsAllowed(pk),
            "build_plate_detection_enabled": BambuData.getBuildPlateDetectionEnabled(pk),
            "first_layer_inspection_enabled": BambuData.getFirstLayerInspectionEnabled(pk),
            "print_halt_enabled": BambuData.getPrintHaltEnabled(pk),
            "print_halt_sensitivity": BambuData.getPrintHaltInspectionSensitivity(pk),
            "print_monitoring_enabled": BambuData.getPrintMonitoringEnabled(pk),
            "spaghetti_detection_enabled": BambuData.getSpaghettiDetectionEnabled(pk),
            "ams": BambuData.getAMSData(pk),
            "external_spool": BambuData.getExternalSpoolData(pk),
        })

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_printer_files(request, pk):
        """Return the files and directories within the specified directory"""

        path = request.query_params.get("path", "/")

        try:
            machine = MachineConfig.objects.get(
                machine_type="3d-printer",
                pk=pk,
                active=True,
            )
        except MachineConfig.DoesNotExist:
            return Response(
                {"error": "Printer not found"},
                status=404,
            )

        ip_address = MachineSetting.objects.get(
                    machine_config_id=pk,
                    key="IP_ADDRESS",
                ).value

        access_token = MachineSetting.objects.get(
                            machine_config_id=pk,
                            key="ACCESS_TOKEN",
                        ).value

        if not isinstance(ip_address, str) or not ip_address:
            return Response(
                {"error": "Printer IP address is not configured"},
                status=400,
            )

        if not isinstance(access_token, str) or not access_token:
            return Response(
                {"error": "Printer access token is not configured"},
                status=400,
            )

        try:
            ftps = BambuFTPSService(
                ip_address,
                access_token,
            )

            try:
                files = ftps.list_directory(path)

            except BambuFTPSPathError:
                return Response(
                    {
                        "error": "Path not found",
                        "path": path,
                    },
                    status=404,
                )

            return Response({
                "path": path,
                "files": files,
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500,
            )
        