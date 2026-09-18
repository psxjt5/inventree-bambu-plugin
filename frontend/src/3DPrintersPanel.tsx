import { Badge, Card, Group, Progress, SimpleGrid, Stack, Text, ActionIcon, Button, Tooltip } from '@mantine/core';
import { IconPlayerPlay, IconArrowRight, IconCamera, IconBulb } from '@tabler/icons-react';
import { useEffect, useState } from 'react';

import {
    checkPluginVersion,
    type InvenTreePluginContext,
} from '@inventreedb/ui';

const STATUS_MAP: Record<number, { label: string; color: string }> = {
    101: { label: 'Idle', color: 'blue' },
    102: { label: 'Preparing', color: 'blue' },
    103: { label: 'Printing', color: 'green' },
    104: { label: 'Paused', color: 'yellow' },
    105: { label: 'Finished', color: 'teal' },
    300: { label: 'Connected', color: 'blue' },
    301: { label: 'Disconnected', color: 'red' },
    302: { label: 'Stopped', color: 'red' },
    400: { label: 'Misconfigured', color: 'red' },
    500: { label: 'Unknown', color: 'gray' },
};

type ThreeDPrinter = {
    pk: string;
    name: string;
    status: number;
    status_text: string;
    progress: number;
    file_name: string;
    manufacturer: string;
    model: string;
    remaining_time: string;
};

function formatRemainingTime(minutes: number | null): string {
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

function getFinishTime(minutes: number | null): string {
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

function PrinterTile({ printer }: { printer: ThreeDPrinter }) {
    const printerStatus = STATUS_MAP[printer.status] ?? { label: 'Unknown', color: 'gray' };
    const progress = Number(printer.progress);

    return (
        <Card withBorder shadow="sm" padding="sm">
            <Stack gap="none">
                <Group justify="space-between" align="flex-start">
                    <Stack gap={0}>
                        <Text component="h2" fw={600} size="lg">{printer.name}</Text>
                        <Text component="h3" size="sm" c="dimmed">{printer.manufacturer} {printer.model}</Text>
                    </Stack>

                    <Tooltip label={printer.status_text} withArrow>
                        <Badge color={printerStatus.color} variant="light">{printerStatus.label}</Badge>
                    </Tooltip>
                </Group>
                
                <Stack gap={2}>
                    <Text size="sm" c="dimmed">Current Print</Text>
                    <Text fw={500} truncate>{printer.file_name || '-'}</Text>
                </Stack>

                <Stack gap="xs">
                    <Group justify="space-between">
                        <Text size="sm" c="dimmed">Progress</Text>
                        <Text size="sm" fw={500}>{Number.isFinite(progress) ? `${progress}%` : '-'}</Text>
                    </Group>

                    <Progress value={Number.isFinite(progress) ? progress : 0} size="sm" />
                </Stack>

                <Group justify="space-between">
                    <Stack gap={0}>
                        <Text size="sm" c="dimmed">Remaining</Text>
                        <Text size="sm" fw={500}>{formatRemainingTime(printer.remaining_time)}</Text>
                    </Stack>

                    <Stack gap={0} align="flex-end">
                        <Text size="sm" c="dimmed">Finishes</Text>
                        <Text size="sm" fw={500}>{getFinishTime(printer.remaining_time)}</Text>
                    </Stack>
                </Group>

                {/* <Stack gap={2}>
                    <Text size="sm" c="dimmed">Status</Text>
                    <Text size="sm" fw={500}>{printer.status_text || '-'}</Text>
                </Stack> */}

                <Group justify="space-between">
                    <Group gap="xs">
                        <Tooltip label="Live Camera" withArrow>
                            <ActionIcon variant="light" size="lg" onClick={() => console.log('Camera', printer.pk)}>
                                <IconCamera size={18} />
                            </ActionIcon>
                        </Tooltip>
                        <Tooltip label="Run Job" withArrow>
                            <ActionIcon variant="light" size="lg" onClick={() => console.log('Camera', printer.pk)}>
                                <IconPlayerPlay size={18} />
                            </ActionIcon>
                        </Tooltip>
                        <Tooltip label="Toggle Chamber Light" withArrow>
                            <ActionIcon variant="light" size="lg" onClick={() => console.log('Camera', printer.pk)}>
                                <IconBulb size={18} />
                            </ActionIcon>
                        </Tooltip>
                    </Group>

                    <Button rightSection={<IconArrowRight size={25} />} onClick={() => console.log('Details', printer.pk)}>
                        Details
                    </Button>
                </Group>
            </Stack>
        </Card>
    );
}

function ThreeDPrintersPanel({
    context: _context,
}: {
    context: InvenTreePluginContext;
}) {
    const [printers, setPrinters] = useState<ThreeDPrinter[]>([]);

    useEffect(() => {
        const fetchData = () => {
            fetch('/plugin/inventree_bambu/get_printer_tiles_data')
                .then((res) => res.json())
                .then((data: ThreeDPrinter[]) => {
                    setPrinters(data);
                })
                .catch(() => {
                    setPrinters([]);
                });
        };

        fetchData();

        const interval = setInterval(fetchData, 1000);

        return () => clearInterval(interval);
    }, []);

    return (
        <SimpleGrid
            cols={{ base: 1, sm: 2, md: 3, lg: 4 }}
            spacing="md"
        >
            {printers.map((printer) => (
                <PrinterTile
                    key={printer.pk}
                    printer={printer}
                />
            ))}
        </SimpleGrid>
    );
}


export function render3DPrintersPanel(
    context: InvenTreePluginContext,
) {
    checkPluginVersion(context);

    return (
        <ThreeDPrintersPanel context={context} />
    );
}