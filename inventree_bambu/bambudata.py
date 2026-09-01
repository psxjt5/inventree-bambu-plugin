"""
Provides data from the Bambu MQTT Service
"""

from django.core.cache import cache

import json
from pathlib import Path

class BambuData:

    @staticmethod
    def getStatus(serial):
        return BambuData.getPayload(serial).get("print", {}).get("gcode_state")
        
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
    def getHMSModelSeries(serial):
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
        prefix = serial[:3]
        return sn_map.get(prefix, "Unknown")

    @staticmethod
    def getAllHMSCodes(serial):
        hms = BambuData.getPayload(serial).get("print", {}).get("hms", [])
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
    def getAllHMSErrorCodes(serial):
        hms = BambuData.getPayload(serial).get("print", {}).get("hms", [])
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
    def hasHMSErrorCodes(serial):
       return bool(BambuData.getAllHMSErrorCodes(serial))

    @staticmethod
    def getHMSCodeDescription(serial, hms_code):

        series = BambuData.getHMSModelSeries(serial)

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
    def getProgress(serial):
        return BambuData.getPayload(serial).get("print", {}).get("mc_percent")
    
    @staticmethod
    def getLayerProgress(serial):
        layer = BambuData.getPayload(serial).get("print", {}).get("layer_num", 0)
        total = BambuData.getPayload(serial).get("print", {}).get("total_layer_num", 0)
        return int((layer / total) * 100) if total else 0

    @staticmethod
    def getCurrentLayer(serial):
        return BambuData.getPayload(serial).get("print", {}).get("layer_num")

    @staticmethod
    def getTotalLayers(serial):
        return BambuData.getPayload(serial).get("print", {}).get("total_layer_num")

    @staticmethod
    def getRemainingTime(serial):
        return BambuData.getPayload(serial).get("print", {}).get("mc_remaining_time")

    @staticmethod
    def getFileName(serial):
        return BambuData.getPayload(serial).get("print", {}).get("subtask_name")

    @staticmethod
    def getNozzleTemperature(serial):
        return BambuData.getPayload(serial).get("print", {}).get("nozzle_temper")

    @staticmethod
    def getNozzleTargetTemperature(serial):
        return BambuData.getPayload(serial).get("print", {}).get("nozzle_target_temper")

    @staticmethod
    def getBedTemperature(serial):
        return BambuData.getPayload(serial).get("print", {}).get("bed_temper")

    @staticmethod
    def getBedTargetTemperature(serial):
        return BambuData.getPayload(serial).get("print", {}).get("bed_target_temper")

    @staticmethod
    def getCoolingFanSpeed(serial):
        return BambuData.getPayload(serial).get("print", {}).get("cooling_fan_speed")
    
    @staticmethod
    def getHeatBreakFanSpeed(serial):
        return BambuData.getPayload(serial).get("print", {}).get("heatbreak_fan_speed")
    
    @staticmethod
    def getBigFan1Speed(serial):
        return BambuData.getPayload(serial).get("print", {}).get("big_fan1_speed")
    
    @staticmethod
    def getBigFan2Speed(serial):
        return BambuData.getPayload(serial).get("print", {}).get("big_fan2_speed")

    @staticmethod
    def getErrorCode(serial):
        return BambuData.getPayload(serial).get("print", {}).get("print_error")

    @staticmethod
    def getFailReason(serial):
        return BambuData.getPayload(serial).get("print", {}).get("fail_reason")

    @staticmethod
    def getWifiSignal(serial):
        return BambuData.getPayload(serial).get("print", {}).get("wifi_signal")

    @staticmethod
    def getLightsData(serial):
        return BambuData.getPayload(serial).get("print", {}).get("lights_report", [])

    @staticmethod
    def getCameraURL(serial):
        return BambuData.getPayload(serial).get("print", {}).get("ipcam", {}).get("rtsp_url")

    @staticmethod
    def getAMSUnitCount(serial):
        return len(BambuData.getPayload(serial).get("print", {}).get("ams", {}).get("ams", []))
    
    @staticmethod
    def getAMSActiveTray(serial):
        return BambuData.getPayload(serial).get("print", {}).get("ams", {}).get("tray_now")
    
    @staticmethod
    def getAMSData(serial):
        ams_data = BambuData.getPayload(serial).get("print", {}).get("ams", {})
        ams_list = ams_data.get("ams", {})

        result = []

        for ams in ams_list:
            trays = []

            for tray in ams.get("tray", []):
                tray_id = tray.get("id")

                trays.append({
                    "id": tray_id,
                    "type": tray.get("tray_type"),
                    "name": tray.get("tray_sub_brands"),
                    "color": BambuDataService._parse_color(tray.get("tray_color")),
                    "remaining": tray.get("remain"),
                    "state": tray.get("state"),
                    "is_active": tray_id == active_tray
                })

            result.append({
                "id": ams.get("id"),
                "temp": BambuDataService._safe_float(ams.get("temp")),
                "humidity": BambuDataService._safe_int(ams.get("humidity")),
                "trays": trays
            })

        return result



    @staticmethod
    def getRaw(serial):
        return cache.get(f"bambu:{serial}")

    @staticmethod
    def getPayload(serial):
        data = BambuData.getRaw(serial)
        return data.get("payload") if data else None