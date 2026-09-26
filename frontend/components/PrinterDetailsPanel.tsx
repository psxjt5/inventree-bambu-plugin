import {
    Grid,
    Paper,
    Stack,
    Table,
    Text,
} from '@mantine/core';

import type { ThreeDPrinter } from '../types';

type DetailField = {
    name: string;
    label: string;
    value?: React.ReactNode;
};

function DetailsTableField({
    field,
}: {
    field: DetailField;
}) {
    return (
        <Table.Tr style={{ verticalAlign: 'top' }}>
            <Table.Td
                style={{
                    minWidth: 75,
                    width: '50%',
                }}
            >
                <Text fw={600} size='md'>
                    {field.label}
                </Text>
            </Table.Td>

            <Table.Td
                style={{
                    lineBreak: 'anywhere',
                    minWidth: 100,
                    width: '50%',
                }}
            >
                <Text size='md'>
                    {field.value ?? '—'}
                </Text>
            </Table.Td>
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
            value: printer.name,
        },
        {
            name: 'manufacturer',
            label: 'Manufacturer',
            value: printer.manufacturer,
        },
        {
            name: 'model',
            label: 'Model',
            value: printer.model,
        },
    ];

    const printFields: DetailField[] = [
        {
            name: 'status',
            label: 'Status',
            value: printer.status_text,
        },
        {
            name: 'file',
            label: 'File',
            value: printer.file_name,
        },
        {
            name: 'progress',
            label: 'Progress',
            value: `${printer.progress}%`,
        },
        {
            name: 'remaining',
            label: 'Remaining',
            value: printer.remaining_time,
        },
    ];

    const connectionFields: DetailField[] = [
        {
            name: 'manufacturer',
            label: 'Manufacturer',
            value: printer.manufacturer,
        },
        {
            name: 'model',
            label: 'Model',
            value: printer.model,
        },
        {
            name: 'status',
            label: 'Status',
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

// export function PrinterDetailsPanel({
//     printer,
// }: {
//     printer: ThreeDPrinter;
// }) {
//     return (
//         <Stack gap='sm'>
//             <Grid gap='sm'>
//                 <Grid.Col span={{ base: 12, md: 6 }}>
//                     <DetailsTable>
//                         <DetailRow
//                             label='Name'
//                             value={printer.name}
//                         />

//                         <DetailRow
//                             label='Manufacturer'
//                             value={printer.manufacturer}
//                         />

//                         <DetailRow
//                             label='Model'
//                             value={printer.model}
//                         />
//                     </DetailsTable>
//                 </Grid.Col>

//                 <Grid.Col span={{ base: 12, md: 6 }}>
//                     <DetailsTable>
//                         <DetailRow
//                             label='Status'
//                             value={printer.status_text}
//                         />

//                         <DetailRow
//                             label='File'
//                             value={printer.file_name}
//                         />

//                         <DetailRow
//                             label='Progress'
//                             value={`${printer.progress}%`}
//                         />

//                         <DetailRow
//                             label='Remaining'
//                             value={printer.remaining_time}
//                         />
//                     </DetailsTable>
//                 </Grid.Col>

//                 <Grid.Col span={{ base: 12, md: 6 }}>
//                     <DetailsTable>
//                         <DetailRow
//                             label='Name'
//                             value={printer.name}
//                         />

//                         <DetailRow
//                             label='Manufacturer'
//                             value={printer.manufacturer}
//                         />

//                         <DetailRow
//                             label='Model'
//                             value={printer.model}
//                         />
//                     </DetailsTable>
//                 </Grid.Col>
//             </Grid>
//         </Stack>
//     );
// }