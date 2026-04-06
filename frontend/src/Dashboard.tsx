import { Table, Title, Text } from '@mantine/core';
import { useEffect, useState } from 'react';

// Import for type checking
import { checkPluginVersion, type InvenTreePluginContext } from '@inventreedb/ui';

type Machine = {
    id: number;
    name: string;
    state: string;
    progress: number | null;
};

function BambuDashboardItem({
    context: _context
}: {
    context: InvenTreePluginContext;
}) {

    const [machines, setMachines] = useState<Machine[]>([]);

    useEffect(() => {
        const fetchData = () => {
            fetch('/api/plugin/bambu/status/')
                .then(res => res.json())
                .then(setMachines)
                .catch(() => setMachines([]));
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);

        return () => clearInterval(interval);
    }, []);

    const rows = machines.map((m) => (
        <tr key={m.id}>
            <td>{m.name}</td>
            <td>{m.state}</td>
            <td>{m.progress !== null ? `${m.progress}%` : '-'}</td>
        </tr>
    ));

    return (
        <>
            <Title order={1} mb="md">
                3D Printer Status
            </Title>

            {machines.length === 0 ? (
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


// Required export for InvenTree
export function renderbambuDashboardItem(context: InvenTreePluginContext) {
    checkPluginVersion(context);
    return <BambuDashboardItem context={context} />;
}