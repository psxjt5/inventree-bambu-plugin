import { Table, Text, Badge, Progress, Container, ScrollArea, Stack, Tooltip, Group } from '@mantine/core';
import { useEffect, useState } from 'react';

// Import for type checking
import { checkPluginVersion, type InvenTreePluginContext } from '@inventreedb/ui';

{/* <style>
    @keyframes pulse {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
        }
</style> */}

type ThreeDPrinter = {
    pk: string;
    name: string;
    status: number;
    machine_type: string;
    properties: {
        key: string;
        value: string;
        type: string;
        max_progress: number | null;
    }[];
};

function BambuDashboardItem({
    context: _context
}: {
    context: InvenTreePluginContext;
}) {

    const STATUS_MAP: Record<number, { label: string; color: string }> = {
        100: { label: 'Connected', color: 'blue' },
        101: { label: 'Disconnected', color: 'red' },

        200: { label: 'Idle', color: 'blue' },
        201: { label: 'Preparing', color: 'blue' },
        202: { label: 'Printing', color: 'green' },
        203: { label: 'Paused', color: 'yellow' },
        204: { label: 'Finished', color: 'teal' },
        205: { label: 'Failed', color: 'red' },

        998: { label: 'Misconfigured', color: 'red' },
        999: { label: 'Unknown', color: 'gray' }
    };

    const [printers, setPrinters] = useState<ThreeDPrinter[]>([]);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isLive, setIsLive] = useState(false);

    useEffect(() => {
        const fetchData = () => {
            fetch('/api/machine/')
                .then(res => res.json())
                .then((data: ThreeDPrinter[]) => {
                    const printers = data.filter(m => m.machine_type === '3d-printer');
                    setPrinters(printers);
                    setLastUpdated(new Date());
                    setIsLive(true);
                })
                .catch(() => {
                    setPrinters([]);
                    setIsLive(false);
                })
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, []);

    const rows = printers.map((m) => {
        const progress = Number(getProperty(m, 'Job Progress'));
        const fileName = getProperty(m, 'File Name');

        const printerStatus = STATUS_MAP[m.status] ?? {
                        label: 'Unknown',
                        color: 'gray'
                    };

        return (
            <Table.Tr key={m.pk}>
                <Table.Td>
                    <Text>{m.name}</Text>
                </Table.Td>

                <Table.Td>
                    <Badge color={printerStatus.color} variant="light">
                        {printerStatus.label}
                    </Badge>
                </Table.Td>

                <Table.Td>
                    <Text size="sm" truncate>
                        {fileName ?? '-'}
                    </Text>
                </Table.Td>

                <Table.Td style={{ minWidth: 120 }}>
                    <div style={{ minWidth: 140 }}>
                        {progress !== null ? (
                            <Tooltip label={`${progress}%`} withArrow>
                                <div>
                                    <Progress value={progress} size="sm" />
                                </div>
                            </Tooltip>
                        ) : (
                            <Text size="sm" c="dimmed">-</Text>
                        )}
                    </div>
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <Stack h="100%">
            <style>
            {`
            @keyframes pulse {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
            }
            `}
            </style>

            <Group justify="space-between" mb="xs">
                <Text
                    variant="gradient"
                    gradient={{ from: 'indigo', to: 'blue', deg: 45 }}
                    size="xl"
                    fw={700}
                >
                    3D Printer Status
                </Text>

                <Group gap="xs">
                    <Badge
                        color={isLive ? 'green' : 'red'}
                        variant="dot"
                    >
                        {isLive ? 'Live' : 'Offline'}
                    </Badge>

                    <Text size="xs" c="dimmed">
                        {getSecondsAgo(lastUpdated)}
                    </Text>
                </Group>
            </Group>

            <ScrollArea style={{ flex: 1 }}>
                <Container px={0}>
                    <Table>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Printer</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th>File Name</Table.Th>
                                <Table.Th>Progress</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {printers.length > 0 ? (
                                rows
                            ) : (
                                <Table.Tr>
                                    <Table.Td colSpan={3}>
                                        <Text ta="center" c="dimmed">
                                            No printers found
                                        </Text>
                                    </Table.Td>
                                </Table.Tr>
                            )}
                        </Table.Tbody>
                    </Table>
                </Container>
            </ScrollArea>
        </Stack>
    );
}

function getProperty(machine: ThreeDPrinter, key: string): string | null {
    const prop = machine.properties.find(p => p.key === key);

    if (!prop || prop.value === '') return null;

    return prop.value;
}

function getSecondsAgo(date: Date | null): string {
    if (!date) return '';

    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

    if (seconds < 1) return 'just now';

    return `${seconds}s ago`;
}

// Required export for InvenTree
export function renderBambuDashboardItem(context: InvenTreePluginContext) {
    checkPluginVersion(context);
    return <BambuDashboardItem context={context} />;
}