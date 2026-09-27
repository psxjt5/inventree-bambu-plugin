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
    IconBox,
    IconBuildingFactory2,
    IconCarFan,
    IconCarFan1,
    IconCarFan2,
    IconCircleLetterA,
    IconCirclePercentage,
    IconClock,
    IconFile,
    IconFileStack,
    IconMapPin,
    IconPrinter,
    IconSettings,
    IconStack2,
    IconTemperature,
    IconTemperaturePlus,
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
                        value={(printer.layer_progress/printer.total_layers)*100}
                        size='md'
                        style={{ flex: 1 }}
                        animated
                    />
                    <Text size='sm' style={{
                        width: '20%',
                        textAlign: 'right',
                        flexShrink: 0,
                    }}>
                        {printer.layer_progress} / {printer.total_layers}
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
                        {printer.nozzle_temperature} / {printer.nozzle_target_temperature}
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
                        {printer.bed_temperature} / {printer.bed_target_temperature}
                    </Text>
                </Group>
            ),
        },
        {
            name: 'coolingfan',
            label: 'Cooling Fan Speed',
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
            label: 'Big Fan 1 Speed',
            icon: <IconCarFan1/>,
            value: printer.big_fan_1_speed,
        },
        {
            name: 'bigfan2',
            label: 'Big Fan 2 Speed',
            icon: <IconCarFan2/>,
            value: printer.big_fan_2_speed,
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
            </Grid>
        </Stack>
    );
}