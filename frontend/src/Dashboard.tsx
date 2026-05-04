import { Table, Text, Badge, Progress, Container, ScrollArea, Stack, Tooltip } from '@mantine/core';
import { useEffect, useState } from 'react';

// Import for type checking
import { checkPluginVersion, type InvenTreePluginContext } from '@inventreedb/ui';

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

    useEffect(() => {
        const fetchData = () => {
            fetch('/api/machine/')
                .then(res => res.json())
                .then((data: ThreeDPrinter[]) => {
                    const printers = data
                        .filter(m => m.machine_type === '3d-printer');

                    setPrinters(printers);
                })
                .catch(() => setPrinters([]));
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
                    <Text fw={500}>{m.name}</Text>
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
        <Stack>
            <Text
                variant="gradient"
                gradient={{ from: 'indigo', to: 'blue', deg: 45 }}
                size="xl"
                fw={700}
            >
                3D Printer Status
            </Text>

            <ScrollArea h={300}>
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

// Required export for InvenTree
export function renderBambuDashboardItem(context: InvenTreePluginContext) {
    checkPluginVersion(context);
    return <BambuDashboardItem context={context} />;
}