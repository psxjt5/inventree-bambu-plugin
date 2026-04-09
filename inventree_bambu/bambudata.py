"""
Provides data from the Bambu MQTT Service
"""

from django.core.cache import cache

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
            "01P": "P1S",
            "01S": "P1P",
            "039": "A1",
            "030": "A1 Mini"
        }
        prefix = serial[:3]
        return sn_map.get(prefix, "Unknown")
    
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
    def getAMSUnitCount(serial):
        return len(BambuData.getPayload(serial).get("print", {}).get("ams", {}).get("ams", []))
    
    @staticmethod
    def getRaw(serial):
        return cache.get(f"bambu:{serial}")

    @staticmethod
    def getPayload(serial):
        data = BambuData.getRaw(serial)
        return data.get("payload") if data else None