export type ThreeDPrinter = {
    pk: string;
    name: string;
    manufacturer: string;
    model: string | null;
    serial: string;

    location: string | null;
    location_name: string | null;

    status: number;
    status_text: string;

    progress: number | null;
    layer_progress: number | null;
    current_layer: number | null;
    total_layers: number | null;
    remaining_time: string | null;
    file_name: string | null;

    nozzle_diameter: number | null;
    nozzle_type: string | null;
    nozzle_temperature: number | null;
    nozzle_target_temperature: number | null;

    bed_temperature: number | null;
    bed_target_temperature: number | null;
    chamber_temperature: number | null;

    cooling_fan_speed: number | null;
    heatbreak_fan_speed: number | null;
    big_fan_1_speed: number | null;
    big_fan_2_speed: number | null;

    ams_units: number | null;
    ams_active_tray: number | null;
    ams: unknown;

    wifi_strength: number | null;
    sdcard: unknown;

    chamber_light: boolean | null;
    work_light: string | null;

    camera_present: boolean;
    camera_url: string | null;
    camera_record: boolean;
    camera_timelapse: boolean;
    camera_resolution: string | null;

    skip_parts_enabled: boolean;
    build_plate_detection_enabled: boolean;
    first_layer_inspection_enabled: boolean;

    print_halt_enabled: boolean;
    print_halt_sensitivity: number | null;
    print_monitoring_enabled: boolean;
    spaghetti_detection_enabled: boolean;
};