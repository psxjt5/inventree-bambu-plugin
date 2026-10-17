"""
BambuAPI: API methods for Bambu Lab printers.
"""

import tempfile

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import FileResponse, HttpResponse, StreamingHttpResponse

from machine.models import MachineConfig
from machine.models import MachineSetting
from machine.serializers import MachineConfigSerializer
from stock.models import StockLocation

from .bambudata import BambuData
from .bambuftpsservice import BambuFTPSService, BambuFTPSPathError
from .bambuutils import BambuUtils, PrinterNotFound, PrinterFTPSServiceNotFound, PrinterCameraServiceNotFound

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

        # Get the file path from the query string.
        path = request.query_params.get("path", "/")

        try:
            files = BambuUtils.get_printer_ftps_service(pk).list_directory(path)

        except BambuFTPSPathError:
            return Response({"error": "Path not found", "path": path}, status=404)

        except PrinterNotFound:
            return Response({"error": "Printer not found", "path": path}, status=404)

        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found", "path": path}, status=404)

        return Response({
            "path": path,
            "files": files,
        })

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_printer_directories(request, pk):

        """Return all printer directories"""

        try:
            return Response({"directories": BambuUtils.get_printer_ftps_service(pk).list_all_directories()})

        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)

        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found"}, status=404)

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def download_printer_files(request, pk):
        """Download the selected files (one file as-is, several as a zip)."""
        path = request.query_params.get("path", "/")
        names = request.query_params.getlist("names")

        if not names:
            return Response({"error": "No files selected"}, status=400)

        try:
            ftps = BambuUtils.get_printer_ftps_service(pk)
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)
        except PrinterFTPSServiceNotFound:
            return Response({"error": "Printer FTPS Service not found"}, status=404)

        # Temporary file on the server; deleted automatically once the response is sent
        temp = tempfile.TemporaryFile()
        ftps.download_files(path, names, temp)
        temp.seek(0)

        filename = names[0] if len(names) == 1 else "printer-files.zip"
        return FileResponse(temp, as_attachment=True, filename=filename)

    @api_view(["GET"])
    @permission_classes([IsAuthenticated])
    def get_camera_stream(request, pk):
        print(f"[BambuAPI] get_camera_stream {pk}")
        """ Returns the technology used for the printer's camera (MP4/MJPEG) """
        try:
            camera = BambuUtils.get_printer_camera_service(pk)
            use_video = request.query_params.get("stream") != "mjpeg" and camera.supports_video()
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=503)
        except PrinterCameraServiceNotFound:
            return Response({"error": "Printer camera not available"}, status=503)
        except ConnectionError as e:
            return Response({"error": str(e)}, status=503)

        if use_video:
            response = StreamingHttpResponse(camera.stream_mp4(), content_type="video/mp4")
        else:
            response = StreamingHttpResponse(
                camera.stream_mjpeg(),
                content_type="multipart/x-mixed-replace; boundary=frame",
            )

        response["Cache-Control"] = "no-store"
        return response

    # Printer Commands
    @api_view(["POST"])
    @permission_classes([IsAuthenticated])
    def stop_print(request, pk):
        """Stops the current print."""
        try:
            mqtt = BambuUtils.get_printer_mqtt_service(pk)  # however you look up the controller
        except PrinterNotFound:
            return Response({"error": "Printer not found"}, status=404)

        mqtt.request_stop_print()
        return Response(status=202)