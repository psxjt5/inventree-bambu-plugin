import { Badge, Card, Group, Progress, SimpleGrid, Stack, Text, Tooltip } from '@mantine/core';
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
};


function PrinterTile({ printer }: { printer: ThreeDPrinter }) {
    const printerStatus = STATUS_MAP[printer.status] ?? { label: 'Unknown', color: 'gray' };
    const progress = Number(printer.progress);

    return (
        <Card withBorder shadow="sm" padding="sm">
            <Stack gap="sm">
                <Group justify="space-between">
                    <Text component="h2" fw={600} size="lg">{printer.name}</Text>
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

                <Stack gap={2}>
                    <Text size="sm" c="dimmed">Status</Text>
                    <Text size="sm">{printer.status_text || '-'}</Text>
                </Stack>
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
            fetch('/plugin/inventree_bambu/get_dashboard_widget_data')
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