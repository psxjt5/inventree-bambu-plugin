import {
    Anchor,
    Badge,
    Grid,
    Group,
    Paper,
    Progress,
    Stack,
    Table,
    Text,
    Tooltip,
} from '@mantine/core';
import {
    IconActivity,
    IconAdjustmentsPause,
    IconBinoculars,
    IconBox,
    IconBuildingFactory2,
    IconBulb,
    IconCamera,
    IconCameraSpark,
    IconCameraStar,
    IconCarFan,
    IconCarFan1,
    IconCarFan2,
    IconCircleLetterA,
    IconCirclePercentage,
    IconClock,
    IconCongruentTo,
    IconDeviceSdCard,
    IconDoor,
    IconFile,
    IconFileStack,
    IconMapPin,
    IconPhotoSpark,
    IconPlayerPause,
    IconPlayerSkipForward,
    IconPrinter,
    IconQrcode,
    IconSettings,
    IconSquareNumber1,
    IconStack2,
    IconTemperature,
    IconTemperaturePlus,
    IconTooltip,
    IconVideo,
    IconWifi,
} from '@tabler/icons-react';
import {
    CopyButton, InvenTreePluginContext
} from '@inventreedb/ui';

import type { ThreeDPrinter } from '../types';

function formatRemainingTime(minutes: string | number | null): string {
    const value = Number(minutes);

    if (minutes === null || minutes === undefined || !Number.isFinite(value)) {
        return '-';
    }

    const totalMinutes = Math.max(0, Math.round(value));
    const days = Math.floor(totalMinutes / (24 * 60));
    const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
    const remainingMinutes = totalMinutes % 60;

    if (days > 0) {
        return `${days}d ${hours}h ${remainingMinutes}m`;
    }

    if (hours > 0) {
        return `${hours}h ${remainingMinutes}m`;
    }

    return `${remainingMinutes}m`;
}

function getFinishTime(minutes: string | number | null): string {
    const value = Number(minutes);

    if (minutes === null || minutes === undefined || !Number.isFinite(value)) {
        return '-';
    }

    const finishTime = new Date(Date.now() + Math.round(value) * 60 * 1000);
    const now = new Date();

    const sameDay = finishTime.toDateString() === now.toDateString();

    if (sameDay) {
        return finishTime.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
        });
    }

    return finishTime.toLocaleDateString([], {
        weekday: 'short',
    }) + ' ' + finishTime.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
    });
}

function getStatusColor(status: number): string {
    switch (Number(status)) {
        case 101: // Idle
        case 102: // Preparing
        case 103: // Printing
        case 300: // Connected
            return 'blue';

        case 104: // Paused
        case 500: // Unknown
            return 'gray';

        case 105: // Finished
            return 'green';

        case 301: // Disconnected
        case 302: // Failed
        case 303: // Error
        case 400: // Misconfigured
            return 'red';

        default:
            return 'gray';
    }
}

function getShowPrintingStats(status: number): boolean {
     switch (Number(status)) {
        case 101: // Idle
        case 300: // Connected
        case 500: // Unknown
        case 301: // Disconnected
        case 400: // Misconfigured
            return false;

        case 102: // Preparing
        case 103: // Printing
        case 302: // Failed
        case 303: // Error
        case 104: // Paused
        case 105: // Finished
            return true;

        default:
            return false;
    }
}

type DetailField = {
    name: string;
    label: string;
    value?: React.ReactNode;
    icon?: React.ReactNode;
    copy?: boolean;
};

function DetailsTableField({
    field,
}: {
    field: DetailField;
}) {
    return (
        <Table.Tr style={{ verticalAlign: 'middle' }}>
            <Table.Td
                style={{
                    width: '45%',
                    minWidth: 75,
                }}
            >
                <Group gap='xs' wrap='nowrap'>
                    {field.icon}

                    <Text size='md' pl='sm'>
                        {field.label}
                    </Text>
                </Group>
            </Table.Td>

            <Table.Td
                style={{
                    width: '45%',
                    minWidth: 100,
                    lineBreak: 'anywhere',
                }}
            >
                <Text size='sm'>
                    {field.value ?? '—'}
                </Text>
            </Table.Td>

            <Table.Td
                style={{
                    width: '4%',
                    minWidth: 40,
                    textAlign: 'center',
                    verticalAlign: 'middle',
                }}
            >
                {field.copy && (
                    <Group justify='center' align='center'>
                        <CopyButton
                            value={String(field.value ?? '')}
                            size='sm'
                        />
                    </Group>
                )}
            </Table.Td>
        </Table.Tr>
    );
}

function DetailsTable({
    fields,
}: {
    fields: DetailField[];
}) {
    return (
        <Paper
            p='xs'
            withBorder
            style={{
                overflowX: 'hidden',
                width: '100%',
                minWidth: 200,
            }}
        >
            <Table
                striped
                verticalSpacing={8}
                horizontalSpacing='sm'
            >
                <Table.Tbody>
                    {fields.map((field) => (
                        <DetailsTableField
                            key={field.name}
                            field={field}
                        />
                    ))}
                </Table.Tbody>
            </Table>
        </Paper>
    );
}

export function PrinterDetailsPanel({
    printer,
    context,
}: {
    printer: ThreeDPrinter;
    context: InvenTreePluginContext;
}) {
    const printerFields: DetailField[] = [
        {
            name: 'name',
            label: 'Name',
            icon: <IconPrinter/>,
            value: printer.name,
            copy: true
        },
        {
            name: 'manufacturer',
            label: 'Manufacturer',
            icon: <IconBuildingFactory2/>,
            value: printer.manufacturer,
            copy: true
        },
        {
            name: 'model',
            label: 'Model',
            icon: <IconBox/>,
            value: printer.model,
            copy: true
        },
        {
            name: 'amstotal',
            label: 'AMS Units',
            icon: <IconCircleLetterA/>,
            value: printer.ams_units,
            copy: true
        },
        {
            name: 'location',
            label: 'Location',
            icon: <IconMapPin/>,
            value: printer.location_name ? (
                <Anchor
                    href={`/stock/location/${printer.location}`}
                    onClick={(event) => {
                        event.preventDefault();

                        context.navigate(
                            `/stock/location/${printer.location}`,
                        );
                    }}
                >
                    {printer.location_name}
                </Anchor>
            ) : (
                '—'
            )
        },
        {
            name: 'chamberlight',
            label: 'Chamber Light',
            icon: <IconBulb/>,
            value: printer.chamber_light ? 'On' : 'Off',
        },
    ];

    const jobFields: DetailField[] = [
        {
            name: 'status',
            label: 'Status',
            icon: <IconActivity/>,
            value: (
                <Badge
                    color={getStatusColor(printer.status)}
                    variant='light'
                >
                    {printer.status_text}
                </Badge>
            ),
        },
        {
            name: 'file',
            label: 'Current Job File',
            icon: <IconFileStack/>,
            value: getShowPrintingStats(printer.status) ? printer.file_name ? (printer.file_name) : ('—') : (<Tooltip label="No active job" withArrow><span>—</span></Tooltip>),
        },
        {
            name: 'progress',
            label: 'Job Progress',
            icon: <IconCirclePercentage/>,
            value: getShowPrintingStats(printer.status) ? (
                <Group gap='xs' wrap='nowrap' style={{ width: '100%' }}>
                    <Progress
                        value={printer.progress}
                        size='md'
                        style={{ flex: 1 }}
                        animated
                    />
                    <Text size='sm' style={{
                        width: '20%',
                        textAlign: 'right',
                        flexShrink: 0,
                    }}>
                        {printer.progress}%
                    </Text>
                </Group>
            ) : (<Tooltip label="No active job" withArrow><span>—</span></Tooltip>),
        },
        {
            name: 'layers',
            label: 'Job Layers',
            icon: <IconStack2/>,
            value: getShowPrintingStats(printer.status) ? (
                <Group gap='xs' wrap='nowrap' style={{ width: '100%' }}>
                    <Progress
                        value={(printer.current_layer/printer.total_layers)*100}
                        size='md'
                        style={{ flex: 1 }}
                        animated
                    />
                    <Text size='sm' style={{
                        width: '20%',
                        textAlign: 'right',
                        flexShrink: 0,
                    }}>
                        <Tooltip label="Current Layer" withArrow><span>{printer.current_layer}</span></Tooltip> / <Tooltip label="Total Layers" withArrow><span>{printer.total_layers}</span></Tooltip>
                    </Text>
                </Group>
            ) : (<Tooltip label="No active job" withArrow><span>—</span></Tooltip>),
        },
        {
            name: 'remaining',
            label: 'Time Remaining',
            icon: <IconClock/>,
            value: getShowPrintingStats(printer.status) ? formatRemainingTime(printer.remaining_time) : (<Tooltip label="No active job" withArrow><span>—</span></Tooltip>),
        },
        {
            name: 'finishes',
            label: 'Job Finishes',
            icon: <IconClock/>,
            value: getShowPrintingStats(printer.status) ? getFinishTime(printer.remaining_time) : (<Tooltip label="No active job" withArrow><span>—</span></Tooltip>),
        },
    ];

    const statsFields: DetailField[] = [
        {
            name: 'nozzletype',
            label: 'Nozzle Type',
            icon: <IconTooltip/>,
            value: printer.nozzle_type,
        },
        {
            name: 'nozzlediameter',
            label: 'Nozzle Diameter',
            icon: <IconTooltip/>,
            value: printer.nozzle_diameter,
        },
        {
            name: 'nozzletemp',
            label: 'Nozzle Temperature',
            icon: <IconTemperature/>,
            value: (
                <Group gap='xs' wrap='nowrap' style={{ width: '100%' }}>
                    <Progress
                        value={(printer.nozzle_temperature/printer.nozzle_target_temperature)*100}
                        size='md'
                        style={{ flex: 1 }}
                    />
                    <Text size='sm' style={{
                        width: '20%',
                        textAlign: 'right',
                        flexShrink: 0,
                    }}>
                        <Tooltip label="Current Temperature" withArrow><span>{printer.nozzle_temperature}</span></Tooltip> / <Tooltip label="Target Temperature" withArrow><span>{printer.nozzle_target_temperature}</span></Tooltip>
                    </Text>
                </Group>
            ),
        },
        {
            name: 'bedtemp',
            label: 'Bed Temperature',
            icon: <IconTemperature/>,
            value: (
                <Group gap='xs' wrap='nowrap' style={{ width: '100%' }}>
                    <Progress
                        value={(printer.bed_temperature/printer.bed_target_temperature)*100}
                        size='md'
                        style={{ flex: 1 }}
                    />
                    <Text size='sm' style={{
                        width: '20%',
                        textAlign: 'right',
                        flexShrink: 0,
                    }}>
                        <Tooltip label="Current Temperature" withArrow><span>{printer.bed_temperature}</span></Tooltip> / <Tooltip label="Target Temperature" withArrow><span>{printer.bed_target_temperature}</span></Tooltip>
                    </Text>
                </Group>
            ),
        },
        {
            name: 'coolingfan',
            label: 'Part Cooling Fan Speed',
            icon: <IconCarFan/>,
            value: printer.cooling_fan_speed,
        },
        {
            name: 'heatbreakfan',
            label: 'Heatbreak Fan Speed',
            icon: <IconCarFan/>,
            value: printer.heatbreak_fan_speed,
        },
        {
            name: 'bigfan1',
            label: 'Auxiliary Fan Speed',
            icon: <IconCarFan1/>,
            value: printer.big_fan_1_speed,
        },
        {
            name: 'bigfan2',
            label: 'Chamber Fan Speed',
            icon: <IconCarFan2/>,
            value: printer.big_fan_2_speed,
        },
    ];

    const miscFields: DetailField[] = [
        {
            name: 'door',
            label: 'Door State',
            icon: <IconDoor/>,
            value: printer.door_open ? 'Open' : 'Closed',
        },
        {
            name: 'sd',
            label: 'SD/USB Installed',
            icon: <IconDeviceSdCard/>,
            value: printer.sdcard ? 'Yes' : 'No',
        },
        {
            name: 'wifistrength',
            label: 'Wifi Signal Strength',
            icon: <IconWifi/>,
            value: printer.wifi_strength,
        },
        ...(printer.camera_present
            ? [
                {
                    name: 'camtimelapse',
                    label: 'Camera Timelapse',
                    icon: <IconCamera />,
                    value: printer.camera_timelapse ? 'Yes' : 'No',
                },
                {
                    name: 'camrecord',
                    label: 'Camera Recording',
                    icon: <IconVideo />,
                    value: printer.camera_record ? 'Yes' : 'No',
                },
                {
                    name: 'camres',
                    label: 'Camera Resolution',
                    icon: <IconCameraStar />,
                    value: printer.camera_resolution,
                },
            ]
            : []),
    ];

    const aiFields: DetailField[] = [
        {
            name: 'skipparts',
            label: 'Part Skipping',
            icon: <IconPlayerSkipForward/>,
            value: printer.skip_parts_enabled ? 'Enabled' : 'Disabled',
        },
        {
            name: 'buildplatedetect',
            label: 'Build Plate Detection',
            icon: <IconQrcode/>,
            value: printer.build_plate_detection_enabled ? 'Enabled' : 'Disabled',
        },
        {
            name: 'firstlayerinspection',
            label: 'First Layer Inspection',
            icon: <IconSquareNumber1/>,
            value: printer.first_layer_inspection_enabled ? 'Enabled' : 'Disabled',
        },
        {
            name: 'printhaltenabled',
            label: 'Print Halt',
            icon: <IconPlayerPause/>,
            value: printer.print_halt_enabled ? 'Enabled' : 'Disabled',
        },
        {
            name: 'printhaltsensitivity',
            label: 'Print Halt Sensitivity',
            icon: <IconAdjustmentsPause/>,
            value: printer.print_halt_sensitivity ? printer.print_halt_sensitivity.charAt(0).toUpperCase() + printer.print_halt_sensitivity.slice(1) : '',
        },
        {
            name: 'printmonitoringenabled',
            label: 'Print Monitoring',
            icon: <IconBinoculars/>,
            value: printer.print_monitoring_enabled ? 'Enabled' : 'Disabled',
        },
        {
            name: 'spaghettidetectionenabled',
            label: 'Spaghetti Detection',
            icon: <IconCongruentTo/>,
            value: printer.spaghetti_detection_enabled ? 'Enabled' : 'Disabled',
        },
    ];

    return (
        <Stack gap='sm'>
            <Grid gap='xs'>
                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={printerFields} />
                </Grid.Col>

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={jobFields} />
                </Grid.Col>

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={statsFields} />
                </Grid.Col>

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={miscFields} />
                </Grid.Col>

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={aiFields} />
                </Grid.Col>
            </Grid>
        </Stack>
    );
}