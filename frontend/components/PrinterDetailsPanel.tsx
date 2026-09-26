import {
    Grid,
    Group,
    Paper,
    Stack,
    Table,
    Text,
} from '@mantine/core';
import {
    IconActivity,
    IconBox,
    IconClock,
    IconFile,
    IconPrinter,
    IconSettings,
} from '@tabler/icons-react';
import {
    CopyButton,
} from '@inventreedb/ui';

import type { ThreeDPrinter } from '../types';

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
                    minWidth: 75,
                    width: '50%',
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
                    lineBreak: 'anywhere',
                    minWidth: 100,
                    width: field.copy ? '45%' : '50%',
                }}
            >
                <Text size='sm'>
                    {field.value ?? '—'}
                </Text>
            </Table.Td>

            {field.copy && (
                <Table.Td
                    style={{
                        width: '5%',
                        textAlign: 'right',
                        verticalAlign: 'middle'
                    }}
                >
                    <Group justify='center' align='center'>
                        <CopyButton
                            value={String(field.value ?? '')}
                            size='sm'
                        />
                    </Group>
                </Table.Td>
            )}
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
}: {
    printer: ThreeDPrinter;
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
            icon: <IconPrinter/>,
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
    ];

    const printFields: DetailField[] = [
        {
            name: 'status',
            label: 'Status',
            icon: <IconActivity/>,
            value: printer.status_text,
        },
        {
            name: 'file',
            label: 'File',
            icon: <IconFile/>,
            value: printer.file_name,
        },
        {
            name: 'progress',
            label: 'Progress',
            icon: <IconActivity/>,
            value: `${printer.progress}%`,
        },
        {
            name: 'remaining',
            label: 'Remaining',
            icon: <IconClock/>,
            value: printer.remaining_time,
        },
    ];

    const connectionFields: DetailField[] = [
        {
            name: 'manufacturer',
            label: 'Manufacturer',
            icon: <IconClock/>,
            value: printer.manufacturer,
        },
        {
            name: 'model',
            label: 'Model',
            icon: <IconBox/>,
            value: printer.model,
        },
        {
            name: 'status',
            label: 'Status',
            icon: <IconActivity/>,
            value: printer.status_text,
        },
    ];

    return (
        <Stack gap='sm'>
            <Grid gap='xs'>
                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={printerFields} />
                </Grid.Col>

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={printFields} />
                </Grid.Col>

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DetailsTable fields={connectionFields} />
                </Grid.Col>
            </Grid>
        </Stack>
    );
}