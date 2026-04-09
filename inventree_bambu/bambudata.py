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
    def getAMSUnitCount(serial):
        return len(BambuData.getPayload(serial).get("print", {}).get("ams", {}).get("ams", []))
    
    @staticmethod
    def getProgress(serial):
        return
    
    @staticmethod
    def getJobName(serial):
        return
    
    @staticmethod
    def getRaw(serial):
        return cache.get(f"bambu:{serial}")

    @staticmethod
    def getPayload(serial):
        data = BambuData.getRaw(serial)
        return data.get("payload") if data else None