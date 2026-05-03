import { Table, Text, Badge, Progress, Container, ScrollArea, Stack } from '@mantine/core';
import { useEffect, useState } from 'react';

// Import for type checking
import { checkPluginVersion, type InvenTreePluginContext } from '@inventreedb/ui';

type ThreeDPrinter = {
    pk: string;
    name: string;
    status_text: string;
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
        const progress = getProgress(m);

        return (
            <Table.Tr key={m.pk}>
                <Table.Td>
                    <Text fw={500}>{m.name}</Text>
                </Table.Td>

                <Table.Td>
                    {/* <Text size="sm" c="dimmed">
                        {m.status_text}
                    </Text> */}
                    <Badge color={getStatusColor(m.status_text)} variant="light">
                        {m.status_text}
                    </Badge>
                </Table.Td>

                <Table.Td style={{ minWidth: 120 }}>
                    {progress !== null ? (
                        <Progress value={progress} size="sm" />
                    ) : (
                        <Text size="sm" c="dimmed">-</Text>
                    )}
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
                        <Table.Tbody>
                            {printers.length > 0 ? (
                                rows
                            ) : (
                                <Table.Tr>
                                    <Table.Td>
                                        <Text c="dimmed">
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

function getProgress(machine: ThreeDPrinter): number | null {
    const prop = machine.properties.find(
        (p) => p.key === 'Job Progress'
    );

    if (!prop || prop.value === '') return null;

    return Number(prop.value)
}

function getStatusColor(status: string): string {
    const s = status.toLowerCase();

    if (s.includes('printing')) return 'green';
    if (s.includes('paused')) return 'yellow';
    if (s.includes('error')) return 'red';

    return 'gray';
}

// Required export for InvenTree
export function renderBambuDashboardItem(context: InvenTreePluginContext) {
    checkPluginVersion(context);
    return <BambuDashboardItem context={context} />;
}