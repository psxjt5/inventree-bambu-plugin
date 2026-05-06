import { Table, Text, Badge, Progress, Container, ScrollArea, Stack, Tooltip, Group } from '@mantine/core';
import { useEffect, useState } from 'react';

// Import for type checking
import { checkPluginVersion, type InvenTreePluginContext } from '@inventreedb/ui';

type ThreeDPrinter = {
    pk: string,
    name: string;
    status: number;
    status_text: string,
    progress: number,
    file_name: string
};

function BambuDashboardItem({
    context: _context
}: {
    context: InvenTreePluginContext;
}) {

    const STATUS_MAP: Record<number, { label: string; color: string }> = {
        101: { label: 'Idle', color: 'blue' },
        102: { label: 'Preparing', color: 'blue' },
        103: { label: 'Printing', color: 'green' },
        104: { label: 'Paused', color: 'yellow' },
        105: { label: 'Finished', color: 'teal' },

        300: { label: 'Connected', color: 'blue' },
        301: { label: 'Disconnected', color: 'red' },
        302: { label: 'Failed', color: 'red' },

        400: { label: 'Misconfigured', color: 'red' },

        500: { label: 'Unknown', color: 'gray' }
    };

    const [printers, setPrinters] = useState<ThreeDPrinter[]>([]);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isLive, setIsLive] = useState(false);

    useEffect(() => {
        const fetchData = () => {
            fetch('/plugin/inventree_bambu/get_dashboard_widget_data')
                .then(res => res.json())
                .then((data: ThreeDPrinter[]) => {
                    const printers = data;
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
        const interval = setInterval(fetchData, 1000);

        return () => clearInterval(interval);
    }, []);

    const rows = printers.map((m) => {
        const progress = Number(m.progress);
        const fileName = m.file_name;

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
                    <Tooltip label={`${m.status_text}`} withArrow>
                        <div>
                            <Badge color={printerStatus.color} variant="light">
                                {printerStatus.label}
                            </Badge>
                        </div>
                    </Tooltip>
                    
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
        <Stack style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
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

            <ScrollArea style={{ flex: 1, minHeight: 0 }}>
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