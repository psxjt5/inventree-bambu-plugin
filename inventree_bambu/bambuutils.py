from machine.registry import registry

class PrinterNotFound(Exception):
    """Raised when a printer cannot be found"""

class PrinterFTPSServiceNotFound(Exception):
    """Raised when a printer's FTPS Service cannot be found"""

class PrinterCameraServiceNotFound(Exception):
    """Raised when a printer's Camera Service cannot be found"""

class BambuUtils:
    @staticmethod
    def get_printer_ftps_service(pk):
        
        machine = registry.get_machine(pk)
        
        if machine is None:
            raise PrinterNotFound

        controller = getattr(machine.driver, "printerControllers", {}).get(machine.pk)

        if controller is None or controller.ftps_service is None:
            raise PrinterFTPSServiceNotFound

        return controller.ftps_service

    @staticmethod
    def get_printer_camera_service(pk):

        machine = registry.get_machine(pk)

        if machine is None:
            raise PrinterNotFound()

        controller = getattr(machine.driver, "printerControllers", {}).get(machine.pk)

        if controller is None or controller.camera_service is None:
            raise PrinterCameraServiceNotFound

        return controller.camera_service