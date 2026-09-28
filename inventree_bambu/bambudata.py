"""
Provides data from the Bambu MQTT Service
"""

from django.core.cache import cache

import json
import math
from pathlib import Path

class BambuData:

    @staticmethod
    def getStatus(pk):
        return BambuData.getPayload(pk).get("print", {}).get("gcode_state")
        
    @staticmethod
    def getModel(serial):
        sn_map = {
            "31B": "H2C",
            "094": "H2D",
            "239": "H2D Pro",
            "093": "H2S",
            "00M": "X1C",
            "03W": "X1E",
            "20P": "X2D",
            "01P": "P1S",
            "01S": "P1P",
            "22E": "P2S",
            "039": "A1",
            "030": "A1 Mini",
            "26A": "A2L"
        }
        prefix = serial[:3]
        return sn_map.get(prefix, "Unknown")


    @staticmethod
    def getHMSModelSeries(pk):
        sn_map = {
            "31B": "31B",
            "094": "094",
            "239": "239",
            "093": "093",
            "00M": "20P",
            "03W": "20P",
            "20P": "20P",
            "01P": "22E",
            "01S": "22E",
            "22E": "22E",
            "039": "26A",
            "030": "26A",
            "26A": "26A"
        }
        prefix = pk[:3]
        return sn_map.get(prefix, "Unknown")

    @staticmethod
    def getAllHMSCodes(pk):
        hms = BambuData.getPayload(pk).get("print", {}).get("hms", [])
        codes = []

        for error in hms:
            attr = error.get("attr")
            code = error.get("code")

            if not attr or not code:
                continue

            hms_code = (
                f"HMS_{attr >> 16:04X}-"
                f"{attr & 0xFFFF:04X}-"
                f"{code >> 16:04X}-"
                f"{code & 0xFFFF:04X}"
            )

            codes.append(hms_code)

        return codes

    @staticmethod
    def getAllHMSErrorCodes(pk):
        hms = BambuData.getPayload(pk).get("print", {}).get("hms", [])
        codes = []

        for error in hms:
            attr = error.get("attr")
            code = error.get("code")

            if not attr or not code:
                continue

            severity = code >> 16

            if severity not in (1, 2):
                continue

            hms_code = (
                f"HMS_{attr >> 16:04X}-"
                f"{attr & 0xFFFF:04X}-"
                f"{code >> 16:04X}-"
                f"{code & 0xFFFF:04X}"
            )

            codes.append(hms_code)

        return codes

    @staticmethod
    def hasHMSErrorCodes(pk):
       return bool(BambuData.getAllHMSErrorCodes(pk))

    @staticmethod
    def getHMSCodeDescription(pk, hms_code):

        series = BambuData.getHMSModelSeries(pk)

        if series == "Unknown":
            return ""

        # Expected format:
        # HMS_XXXX-XXXX-XXXX-XXXX
        if not hms_code.startswith("HMS_"):
            return ""

        parts = hms_code[4:].split("-")

        if len(parts) != 4 or any(len(part) != 4 for part in parts):
            return ""

        ecode = "".join(parts)

        database_file = Path(__file__).parent / "hms_codes.json"

        try:
            with database_file.open("r", encoding="utf-8") as file:
                database = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return ""

        series_database = database.get(series, {})

        ecode = hms_code.removeprefix("HMS_").replace("-", "")

        return series_database.get(ecode, "")


    @staticmethod
    def getProgress(pk):
        return BambuData.getPayload(pk).get("print", {}).get("mc_percent")
    
    @staticmethod
    def getLayerProgress(pk):
        layer = BambuData.getPayload(pk).get("print", {}).get("layer_num", 0)
        total = BambuData.getPayload(pk).get("print", {}).get("total_layer_num", 0)
        return int((layer / total) * 100) if total else 0

    @staticmethod
    def getCurrentLayer(pk):
        return BambuData.getPayload(pk).get("print", {}).get("layer_num")

    @staticmethod
    def getTotalLayers(pk):
        return BambuData.getPayload(pk).get("print", {}).get("total_layer_num")

    @staticmethod
    def getRemainingTime(pk):
        return BambuData.getPayload(pk).get("print", {}).get("mc_remaining_time")

    @staticmethod
    def getFileName(pk):
        return BambuData.getPayload(pk).get("print", {}).get("subtask_name")


    @staticmethod
    def getNozzleTemperature(pk):
        return math.ceil(BambuData.getPayload(pk).get("print", {}).get("nozzle_temper"))

    @staticmethod
    def getNozzleTargetTemperature(pk):
        return math.ceil(BambuData.getPayload(pk).get("print", {}).get("nozzle_target_temper"))

    @staticmethod
    def getBedTemperature(pk):
        return math.ceil(BambuData.getPayload(pk).get("print", {}).get("bed_temper"))

    @staticmethod
    def getBedTargetTemperature(pk):
        return math.ceil(BambuData.getPayload(pk).get("print", {}).get("bed_target_temper"))

    @staticmethod
    def getChamberTemperature(pk):
        chamber_temp = BambuData.getPayload(pk).get("print", {}).get("chamber_temper")
        if (chamber_temp == None):
            chamber_temp = 0
        return math.ceil(chamber_temp)


    @staticmethod
    def getNozzleDiameter(pk):
        return BambuData.getPayload(pk).get("print", {}).get("nozzle_diameter")

    @staticmethod
    def getNozzleType(pk):
        return BambuData.getPayload(pk).get("print", {}).get("nozzle_type")

    @staticmethod
    def getCoolingFanSpeed(pk):
        return BambuData.getPayload(pk).get("print", {}).get("cooling_fan_speed")
    
    @staticmethod
    def getHeatBreakFanSpeed(pk):
        return BambuData.getPayload(pk).get("print", {}).get("heatbreak_fan_speed")
    
    @staticmethod
    def getBigFan1Speed(pk):
        return BambuData.getPayload(pk).get("print", {}).get("big_fan1_speed")
    
    @staticmethod
    def getBigFan2Speed(pk):
        return BambuData.getPayload(pk).get("print", {}).get("big_fan2_speed")


    @staticmethod
    def getErrorCode(pk):
        return BambuData.getPayload(pk).get("print", {}).get("print_error")

    @staticmethod
    def getFailReason(pk):
        return BambuData.getPayload(pk).get("print", {}).get("fail_reason")


    @staticmethod
    def getWifiSignal(pk):
        return BambuData.getPayload(pk).get("print", {}).get("wifi_signal")
    
    @staticmethod
    def getSDCard(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("sdcard"))

    @staticmethod
    def getChamberLightStatus(pk):
        chamber_light_mode = next(
            (
                light.get("mode")
                for light in BambuData.getPayload(pk).get("print", {}).get("lights_report", [])
                if light.get("node") == "chamber_light"
            ),
            None,
        )        
        return chamber_light_mode == "on"

    @staticmethod
    def getWorkLightStatus(pk):
        work_light_mode = next(
            (
                light.get("mode")
                for light in BambuData.getPayload(pk).get("print", {}).get("lights_report", [])
                if light.get("node") == "work_light"
            ),
            None,
        )        
        return work_light_mode


    @staticmethod
    def getCameraPresent(pk):
        return BambuData.getPayload(pk).get("print", {}).get("ipcam", {}).get("ipcam_dev") == "1"

    @staticmethod
    def getCameraURL(pk):
        return BambuData.getPayload(pk).get("print", {}).get("ipcam", {}).get("rtsp_url")

    @staticmethod
    def getCameraRecordStatus(pk):
        return BambuData.getPayload(pk).get("print", {}).get("ipcam", {}).get("ipcam_record")

    @staticmethod
    def getCameraTimelapseStatus(pk):
        return BambuData.getPayload(pk).get("print", {}).get("ipcam", {}).get("timelapse")

    @staticmethod
    def getCameraResolution(pk):
        return BambuData.getPayload(pk).get("print", {}).get("ipcam", {}).get("resolution")


    @staticmethod
    def getSkipPartsAllowed(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("allow_skip_parts"))

    @staticmethod
    def getBuildPlateDetectionEnabled(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("buildplate_marker_detector"))

    @staticmethod
    def getFirstLayerInspectionEnabled(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("first_layer_inspector"))

    @staticmethod
    def getPrintHaltInspectionSensitivity(pk):
        return BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("halt_print_sensitivity")

    @staticmethod
    def getPrintHaltEnabled(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("print_halt"))

    @staticmethod
    def getPrintMonitoringEnabled(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("printing_monitor"))

    @staticmethod
    def getSpaghettiDetectionEnabled(pk):
        return bool(BambuData.getPayload(pk).get("print", {}).get("xcam", {}).get("spaghetti_detector"))


    @staticmethod
    def getAMSUnitCount(pk):
        return len(BambuData.getPayload(pk).get("print", {}).get("ams", {}).get("ams", []))
    
    @staticmethod
    def getAMSActiveTray(pk):
        # 0-253 = Tray ID
        # 254 = External Spool
        # 255 = No filament loaded

        return BambuData.getPayload(pk).get("print", {}).get("ams", {}).get("tray_now")
    
    @staticmethod
    def getAMSData(pk):
        ams_data = BambuData.getPayload(pk).get("print", {}).get("ams", {})
        ams_list = ams_data.get("ams", {})
        active_tray = BambuData.getAMSActiveTray(pk)

        result = []

        for ams in ams_list:
            trays = []

            for tray in ams.get("tray", []):
                tray_id = tray.get("id")

                trays.append({
                    "id": tray_id,
                    "type": tray.get("tray_type"),
                    "name": tray.get("tray_sub_brands"),
                    "color": tray.get("tray_color"),
                    "remaining": tray.get("remain"),
                    # "state": tray.get("state"), - see https://github.com/greghesp/ha-bambulab/blob/0e027ff135a6d9265cb756d3e246747954c76722/custom_components/bambu_lab/pybambu/const.py#L323
                    "is_active": tray_id == active_tray
                })

            result.append({
                "id": ams.get("id"),
                # "temp": BambuDataService._safe_float(ams.get("temp")),
                # "humidity": BambuDataService._safe_int(ams.get("humidity")),
                "trays": trays
            })

        return result



    @staticmethod
    def getRaw(pk):
        return cache.get(f"3dprinter:{pk}")

    @staticmethod
    def getPayload(pk):
        data = BambuData.getRaw(pk)
        return data.get("payload") if data else None