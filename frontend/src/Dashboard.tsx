import { Table, Title, Text } from '@mantine/core';
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
                <td>{m.name}</td>
                <td>{m.status_text}</td>
                <td>{progress !== null ? `${progress}%` : '-'}</td>
            </tr>
        );
    });

    return (
        <>
            <Title order={1} mb="md">
                3D Printer Status
            </Title>

            {printers.length === 0 ? (
                <Text>No printers found</Text>
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


// Required export for InvenTree
export function renderBambuDashboardItem(context: InvenTreePluginContext) {
    checkPluginVersion(context);
    return <BambuDashboardItem context={context} />;
}