import { useCallback, useMemo, useState } from 'react';
import {
    ActionBarDivider,
    ActionIcon,
    Anchor,
    Breadcrumbs,
    Button,
    Divider,
    Group,
    Menu,
    Modal,
    Paper,
    Stack,
    Text,
    TextInput,
    Tooltip,
} from '@mantine/core';
import { IconArrowLeft, IconArrowRight, IconArrowUp, IconCalendarPlus, IconChevronDown, IconCube, IconCursorText, IconDots, IconDownload, IconFile, IconFile3d, IconFileArrowRight, IconFileCode, IconFileText, IconFileUpload, IconFileZip, IconFolder, IconFolderPlus, IconHome, IconMovie, IconPhoto, IconPlus, IconPrinter, IconRefresh, IconTrash } from '@tabler/icons-react';
import {
    ActionButton,
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
    // const [path, setPath] = useState<string>('/');
    const [history, setHistory] = useState<string[]>(['/']);
    const [index, setIndex] = useState(0);
    const path = history[index];

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

    // Table Columns
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

    // Path Breadcrumbs
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

    // Navigate to a new location.
    const go = useCallback(
        (newIndex: number, newHistory = history) => {
            table.clearSelectedRecords();
            table.setSearchTerm('');
            setHistory(newHistory);
            setIndex(newIndex);
        },
        [table, history],
    );

    // Opening a folder, a breadcrumb or "up": drop any forward entries and add the new path
    const navigate = (target: string) => {
        if (target !== path) {
            go(index + 1, [...history.slice(0, index + 1), target]);
        }
    };

    // Back and Forward Stacks
    const back = () => go(index - 1);
    const forward = () => go(index + 1);

    // New Folder Dialog
    const newFolder = context.forms.create({
        url: `/plugin/inventree_bambu/create_printer_directory/${encodeURIComponent(printer.pk)}`,
        title: `Create New Folder on ${printer.name}`,
        fields: {
            path: { value: path, hidden: true },
            name: {},
        },
        successMessage: 'Folder created',
        onFormSuccess: () => table.refreshTable(),
    });

    // Upload File Dialog
    const uploadFile = context.forms.create({
        url: `/plugin/inventree_bambu/upload_printer_file/${encodeURIComponent(printer.pk)}`,
        title: `Upload File to ${printer.name}`,
        fields: {
            path: { value: path, hidden: true },
            file: {},
        },
        submitText: 'Upload',
        successMessage: 'File uploaded',
        timeout: 5 * 60 * 1000,
        onFormSuccess: () => table.refreshTable(),
    });

    // Determines if the current selection can be printed (1 file, not a dir, .gcode.3mf)
    const canPrint =
    table.selectedRecords.length === 1 &&
    !table.selectedRecords[0].is_directory &&
    table.selectedRecords[0].name.toLowerCase().endsWith('.gcode.3mf');

    // Table Action Buttons
    const tableActions = useMemo(
        () => [
            <ActionButton key='back' icon={<IconArrowLeft />} tooltip='Back' disabled={index === 0} onClick={back} />,
            
            <ActionButton key='forward' icon={<IconArrowRight />} tooltip='Forward' disabled={index === history.length - 1} onClick={forward} />,

            <ActionButton variant='transparent' disabled={path === '/'} onClick={() => navigate('/')} icon={<IconHome />} tooltip='Go to Root Folder' />,
            
            <ActionButton variant='transparent' disabled={path === '/'} onClick={() => navigate(getParentPath(path))} icon={<IconArrowUp />} tooltip='Up one level' />,

            // <Divider key='divider-1' orientation='vertical' />,

            // <Menu key='file-actions' position='bottom-end'>
            //     <Menu.Target>
            //         <Tooltip label='File actions' position='left'>
            //             <ActionIcon variant='light' radius='xs' h={36} w='auto' px={2}>
            //                 <Group gap={0} wrap='nowrap'>
            //                     <IconPlus />
            //                     <IconChevronDown />
            //                 </Group>
            //             </ActionIcon>
            //         </Tooltip>
            //     </Menu.Target>

            //     <Menu.Dropdown>
            //         <Menu.Item leftSection={<IconFolderPlus color='var(--mantine-primary-color-filled)' />} onClick={() => newFolder.open()}>
            //             New Folder
            //         </Menu.Item>
            //         <Menu.Item leftSection={<IconFileUpload color='var(--mantine-primary-color-filled)' />} onClick={() => uploadFile.open()}>
            //             Upload File
            //         </Menu.Item>
            //     </Menu.Dropdown>
            // </Menu>,

            // <ActionButton variant='transparent' onClick={() => {}} icon={<IconCursorText />} tooltip='Rename' disabled={!table.hasSelectedRecords} />,

            // <ActionButton variant='transparent' onClick={() => {}} icon={<IconFileArrowRight />} tooltip='Move' disabled={!table.hasSelectedRecords} />,

            // <ActionButton variant='transparent' onClick={() => {}} icon={<IconTrash />} tooltip='Delete' color='red' disabled={!table.hasSelectedRecords} />,

            // <Divider key='divider-1' orientation='vertical' />,

            // <ActionButton variant='transparent' onClick={() => {}} icon={<IconPrinter />} tooltip='Print' disabled={!canPrint} />,

            // <ActionButton variant='transparent' onClick={() => {}} icon={<IconCalendarPlus />} tooltip='Schedule Print' disabled={!canPrint} />,
        ],
        [path, table.hasSelectedRecords, table.selectedRecords],
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
                                onClick={() => navigate(crumb.target)}
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
                            table.clearSelectedRecords();
                            navigate(joinPath(path, record.name));
                            return;
                        }

                        const isSelected = table.selectedRecords.some((r) => r.name === record.name);

                        table.setSelectedRecords(
                            isSelected
                                ? table.selectedRecords.filter((r) => r.name !== record.name)
                                : [...table.selectedRecords, record],
                        );
                    },
                    rowStyle: () => ({ cursor: 'pointer' }),
                }}
            />

            {/* {newFolder.modal}
            {uploadFile.modal} */}
        </Stack>
    );
}