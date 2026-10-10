import { useCallback, useMemo, useState } from 'react';
import {
    ActionIcon,
    Anchor,
    Breadcrumbs,
    Group,
    Paper,
    Stack,
    Text,
    Tooltip,
} from '@mantine/core';
import { IconArrowUp, IconCube, IconFile, IconFile3d, IconFileCode, IconFileText, IconFileZip, IconFolder, IconMovie, IconPhoto, IconRefresh } from '@tabler/icons-react';
import {
    InvenTreeTable,
    useTable,
    type InvenTreePluginContext,
    type TableColumn,
} from '@inventreedb/ui';

import type { ThreeDPrinter } from '../types';

type PrinterFile = {
    name: string;
    is_directory: boolean;
    size: number | null;
    modified: string | null;
};

function joinPath(base: string, name: string): string {
    return base === '/' ? `/${name}` : `${base.replace(/\/+$/, '')}/${name}`;
}

function getParentPath(path: string): string {
    const parts = path.split('/').filter(Boolean);
    parts.pop();
    return parts.length ? `/${parts.join('/')}` : '/';
}

function formatSize(bytes: number | null): string {
    if (bytes == null) return '—';
    const units = ['B', 'KB', 'MB', 'GB'];
    let value = bytes;
    let unit = 0;
    while (value >= 1024 && unit < units.length - 1) {
        value /= 1024;
        unit++;
    }
    return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function FileIcon({ file }: { file: PrinterFile }) {
    if (file.is_directory) {
        return <IconFolder color='var(--mantine-color-yellow-6)' />;
    }

    const name = file.name.toLowerCase();

    // Check compound extensions first (e.g. "part.gcode.3mf")
    if (name.endsWith('.gcode.3mf') || name.endsWith('.3mf')) {
        return <IconFile3d color='var(--mantine-color-blue-6)' />;
    }

    const ext = name.split('.').pop() ?? '';

    switch (ext) {
        case 'gcode':
            return <IconFileCode color='var(--mantine-color-teal-6)' />;
        case 'mp4':
        case 'avi':
            return <IconMovie color='var(--mantine-color-grape-6)' />;
        case 'jpg':
        case 'jpeg':
        case 'png':
            return <IconPhoto color='var(--mantine-color-pink-6)' />;
        case 'txt':
        case 'log':
        case 'json':
            return <IconFileText color='var(--mantine-color-gray-6)' />;
        case 'zip':
            return <IconFileZip color='var(--mantine-color-orange-6)' />;
        default:
            return <IconFile color='var(--mantine-color-gray-6)' />;
    }
}

export function FilesPanel({
    printer,
    context,
}: {
    printer: ThreeDPrinter;
    context: InvenTreePluginContext;
}) {
    const [path, setPath] = useState<string>('/');

    // File names are unique within a directory, so use them as the row key
    const table = useTable('3d-printer-files', { idAccessor: 'name' });

    const url = `/plugin/inventree_bambu/get_printer_files/${encodeURIComponent(printer.pk)}`;

    // Sort by date, with folders first.
    const formatData = useCallback((data: any): PrinterFile[] => {
        const files: PrinterFile[] = Array.isArray(data?.files) ? data.files : [];
        const term = table.searchTerm.trim().toLowerCase();

        return files
        .filter((f) => !term || f.name.toLowerCase().includes(term))
        .sort((a, b) => {
            // Folders first
            if (a.is_directory !== b.is_directory) {
                return a.is_directory ? -1 : 1;
            }

            // Entries with no date go to the bottom of their group
            if (!a.modified || !b.modified) {
                if (a.modified) return -1;
                if (b.modified) return 1;
                return a.name.localeCompare(b.name);
            }

            // Newest first; same timestamp falls back to name
            const diff = Date.parse(b.modified) - Date.parse(a.modified);
            return diff !== 0 ? diff : a.name.localeCompare(b.name);
        });
    }, [table.searchTerm]);

    const columns: TableColumn<PrinterFile>[] = useMemo(
        () => [
            {
                accessor: 'name',
                title: 'Name',
                sortable: false,
                switchable: false,
                render: (record: PrinterFile) => (
                    <Group gap='xs' wrap='nowrap'>
                        <FileIcon file={record} />
                        <Text size='sm' fw={record.is_directory ? 500 : 400}>
                            {record.name}
                        </Text>
                    </Group>
                ),
            },
            {
                accessor: 'modified',
                title: 'Date Modified',
                sortable: false,
                textAlign: 'right',
                render: (record: PrinterFile) =>
                    record.modified ? new Date(record.modified).toLocaleString() : '—',
            },
            {
                accessor: 'size',
                title: 'Size',
                sortable: false,
                textAlign: 'right',
                render: (record: PrinterFile) =>
                    record.is_directory ? '—' : formatSize(record.size),
            },
        ],
        [],
    );

    const crumbs = useMemo(() => {
        const parts = path.split('/').filter(Boolean);
        return [
            { label: 'Root', target: '/' },
            ...parts.map((part, i) => ({
                label: part,
                target: `/${parts.slice(0, i + 1).join('/')}`,
            })),
        ];
    }, [path]);

    const tableActions = useMemo(
        () => [
            <Tooltip key='up' label='Up one level'>
                <ActionIcon
                    variant='transparent'
                    disabled={path === '/'}
                    onClick={() => setPath(getParentPath(path))}
                >
                    <IconArrowUp />
                </ActionIcon>
            </Tooltip>,
        ],
        [path],
    );

    return (
        <Stack gap='sm'>
            <Group justify='space-between'>
                <Breadcrumbs>
                    {crumbs.map((crumb, i) =>
                        i === crumbs.length - 1 ? (
                            <Text key={crumb.target} size='sm' fw={600}>
                                {crumb.label}
                            </Text>
                        ) : (
                            <Anchor
                                key={crumb.target}
                                size='sm'
                                onClick={() => setPath(crumb.target)}
                            >
                                {crumb.label}
                            </Anchor>
                        ),
                    )}
                </Breadcrumbs>

                {/* <Tooltip label='Refresh'>
                    <ActionIcon variant='transparent' onClick={() => table.refreshTable()}>
                        <IconRefresh />
                    </ActionIcon>
                </Tooltip> */}
            </Group>

            <InvenTreeTable
                url={url}
                tableState={table}
                columns={columns}
                context={context}
                props={{
                    params: { path },
                    dataFormatter: formatData,
                    tableActions,
                    enableSearch: true,
                    enableSelection: true,
                    enablePagination: false,
                    enableFilters: false,
                    enableDownload: false,
                    enableColumnSwitching: true,
                    enableRefresh: true,
                    detailAction: false,
                    noRecordsText: 'This folder is empty',
                    onRowClick: (record: PrinterFile) => {
                        if (record.is_directory) {
                            setPath(joinPath(path, record.name));
                        }
                    },
                    rowStyle: (record: PrinterFile) =>
                        record.is_directory ? { cursor: 'pointer' } : undefined,
                }}
            />
        </Stack>
    );
}