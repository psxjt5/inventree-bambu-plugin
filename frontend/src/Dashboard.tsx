import { Table, Title, Text, Badge, Progress } from '@mantine/core';
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
            <tr key={m.pk}>
                <td>
                    <Text fw={500}>{m.name}</Text>
                </td>

                <td>
                    <Badge color={getStatusColor(m.status_text)} variant="light">
                        {m.status_text}
                    </Badge>
                </td>

                <td style={{ minWidth: 120 }}>
                    {progress !== null ? (
                        <Progress value={progress} size="sm" />
                    ) : (
                        <Text size="sm" c="dimmed">-</Text>
                    )}
                </td>
            </tr>
        );
    });

    return (
        <>
            <Title order={4} mb="sm">
                3D Printer Status
            </Title>

            {printers.length === 0 ? (
                <Text c="dimmed">No printers found</Text>
            ) : (
                <Table striped highlightOnHover>
                    <thead>
                        <tr>
                            <th>Printer</th>
                            <th>Status</th>
                            <th>Progress</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </Table>
            )}
        </>
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