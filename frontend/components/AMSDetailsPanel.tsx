import {
    Badge,
    Group,
    Paper,
    Progress,
    Stack,
    Table,
    Text,
} from '@mantine/core';
import { IconCircleLetterA } from '@tabler/icons-react';
import type { InvenTreePluginContext } from '@inventreedb/ui';

import type { ThreeDPrinter } from '../types';

export function AMSDetailsPanel({
    printer,
    context: _context,
}: {
    printer: ThreeDPrinter;
    context: InvenTreePluginContext;
}) {
    if (!printer.ams || printer.ams.length === 0) {
        return (
            <Paper p='md' withBorder>
                <Text c='dimmed'>
                    No AMS units detected.
                </Text>
            </Paper>
        );
    }

    return (
        <Stack gap='md'>
            {printer.ams.map((ams) => (
                <Paper key={ams.id} p='sm' withBorder>
                    <Stack gap='sm'>
                        <Group justify='space-between'>
                            <Group gap='xs'>
                                <IconCircleLetterA size={24} />

                                <Text fw={600}>
                                    AMS {String.fromCharCode(65 + Number(ams.id))}
                                </Text>
                            </Group>

                            <Badge variant='light'>
                                {ams.trays.length} trays
                            </Badge>
                        </Group>

                        <Table
                            striped
                            verticalSpacing='sm'
                            horizontalSpacing='sm'
                        >
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Slot</Table.Th>
                                    <Table.Th>Filament</Table.Th>
                                    <Table.Th>Type</Table.Th>
                                    <Table.Th>Remaining</Table.Th>
                                    <Table.Th>Status</Table.Th>
                                </Table.Tr>
                            </Table.Thead>

                            <Table.Tbody>
                                {ams.trays.map((tray) => (
                                    <Table.Tr key={tray.id}>
                                        <Table.Td>
                                            <Text fw={500}>
                                                {Number(tray.id) + 1}
                                            </Text>
                                        </Table.Td>

                                        <Table.Td>
                                            <Group gap='xs' wrap='nowrap'>
                                                <span
                                                    style={{
                                                        width: 18,
                                                        height: 18,
                                                        borderRadius: '50%',
                                                        backgroundColor: tray.color
                                                            ? `#${tray.color.slice(0, 6)}`
                                                            : 'transparent',
                                                        border: '1px solid var(--mantine-color-gray-4)',
                                                        flexShrink: 0,
                                                    }}
                                                />

                                                <Stack gap={0}>
                                                    <Text size='sm'>
                                                        {tray.name || 'Empty'}
                                                    </Text>

                                                    <Text
                                                        size='xs'
                                                        c='dimmed'
                                                    >
                                                        {tray.color}
                                                    </Text>
                                                </Stack>
                                            </Group>
                                        </Table.Td>

                                        <Table.Td>
                                            {tray.type || '—'}
                                        </Table.Td>

                                        <Table.Td>
                                            <Group
                                                gap='xs'
                                                wrap='nowrap'
                                                style={{
                                                    minWidth: 120,
                                                }}
                                            >
                                                <Progress
                                                    value={
                                                        tray.remaining != null
                                                            ? Math.max(0, Math.min(100, tray.remaining))
                                                            : 0
                                                    }
                                                    size='md'
                                                    style={{ flex: 1 }}
                                                />

                                                <Text
                                                    size='sm'
                                                    style={{ width: 40, textAlign: 'right' }}
                                                >
                                                    {tray.remaining != null ? `${tray.remaining}%` : '—'}
                                                </Text>
                                            </Group>
                                        </Table.Td>

                                        <Table.Td>
                                            {tray.is_active ? (
                                                <Badge color='green'>
                                                    Active
                                                </Badge>
                                            ) : (
                                                <Text
                                                    size='sm'
                                                    c='dimmed'
                                                >
                                                    —
                                                </Text>
                                            )}
                                        </Table.Td>
                                    </Table.Tr>
                                ))}
                            </Table.Tbody>
                        </Table>
                    </Stack>
                </Paper>
            ))}

            {printer.external_spool?.map((spool) => (
                <Paper key={spool.id} p='sm' withBorder>
                    <Stack gap='sm'>
                        <Group justify='space-between'>
                            <Group gap='xs'>
                                <IconCircleLetterA size={24} />

                                <Text fw={600}>
                                    External Spool
                                </Text>
                            </Group>

                            <Badge variant='light'>
                                1 slot
                            </Badge>
                        </Group>

                        <Table
                            striped
                            verticalSpacing='sm'
                            horizontalSpacing='sm'
                        >
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Slot</Table.Th>
                                    <Table.Th>Filament</Table.Th>
                                    <Table.Th>Type</Table.Th>
                                    <Table.Th>Remaining</Table.Th>
                                    <Table.Th>Status</Table.Th>
                                </Table.Tr>
                            </Table.Thead>

                            <Table.Tbody>
                                <Table.Tr>
                                    <Table.Td>
                                        <Text fw={500}>
                                            1
                                        </Text>
                                    </Table.Td>

                                    <Table.Td>
                                        <Group gap='xs' wrap='nowrap'>
                                            <span
                                                style={{
                                                    width: 18,
                                                    height: 18,
                                                    borderRadius: '50%',
                                                    backgroundColor:
                                                        spool.color &&
                                                        spool.color !== '00000000'
                                                            ? `#${spool.color.slice(0, 6)}`
                                                            : 'transparent',
                                                    border:
                                                        '1px solid var(--mantine-color-gray-4)',
                                                    flexShrink: 0,
                                                }}
                                            />

                                            <Stack gap={0}>
                                                <Text size='sm'>
                                                    {spool.name || 'Empty'}
                                                </Text>

                                                <Text size='xs' c='dimmed'>
                                                    {spool.color || '—'}
                                                </Text>
                                            </Stack>
                                        </Group>
                                    </Table.Td>

                                    <Table.Td>
                                        {spool.type || '—'}
                                    </Table.Td>

                                    <Table.Td>
                                        <Group
                                            gap='xs'
                                            wrap='nowrap'
                                            style={{
                                                minWidth: 120,
                                            }}
                                        >
                                            <Progress
                                                value={
                                                    spool.remaining != null
                                                        ? Math.max(
                                                            0,
                                                            Math.min(
                                                                100,
                                                                spool.remaining,
                                                            ),
                                                        )
                                                        : 0
                                                }
                                                size='md'
                                                style={{ flex: 1 }}
                                            />

                                            <Text
                                                size='sm'
                                                style={{
                                                    width: 40,
                                                    textAlign: 'right',
                                                }}
                                            >
                                                {spool.remaining != null
                                                    ? `${spool.remaining}%`
                                                    : '—'}
                                            </Text>
                                        </Group>
                                    </Table.Td>

                                    <Table.Td>
                                        {spool.is_active ? (
                                            <Badge color='green'>
                                                Active
                                            </Badge>
                                        ) : (
                                            <Text size='sm' c='dimmed'>
                                                —
                                            </Text>
                                        )}
                                    </Table.Td>
                                </Table.Tr>
                            </Table.Tbody>
                        </Table>
                    </Stack>
                </Paper>
            ))}
        </Stack>
    );
}