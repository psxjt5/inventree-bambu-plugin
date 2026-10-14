import { Badge, Group, Paper, Stack, Text } from '@mantine/core';
import {
    checkPluginVersion,
    StylishText,
    type PanelType,
    type InvenTreePluginContext,
} from '@inventreedb/ui';
import { useEffect, useState } from 'react';
import {
    IconInfoCircle,
    IconCamera,
    IconFile,
    IconPrinter,
    IconClipboardList,
    IconHistory,
    IconTool,
    IconCircleLetterA,
    IconExclamationCircle,
    IconDeviceGamepad3,
} from '@tabler/icons-react';

import { PanelGroup } from '../components/PanelGroup';
import { PrinterDetailsPanel } from '../components/PrinterDetailsPanel';
import { AMSDetailsPanel } from '../components/AMSDetailsPanel';
import { FilesPanel } from '../components/FilesPanel';

import type { ThreeDPrinter } from '../types';

import { CameraButton } from '../components/CameraModal'

function getStatusColor(status: number): string {
    switch (Number(status)) {
        case 101: // Idle
        case 102: // Preparing
        case 103: // Printing
        case 300: // Connected
            return 'blue';

        case 104: // Paused
        case 500: // Unknown
            return 'gray';

        case 105: // Finished
            return 'green';

        case 301: // Disconnected
        case 302: // Failed
        case 303: // Error
        case 400: // Misconfigured
            return 'red';

        default:
            return 'gray';
    }
}

function getShowPrintingStats(status: number): boolean {
     switch (Number(status)) {
        case 101: // Idle
        case 300: // Connected
        case 500: // Unknown
        case 301: // Disconnected
        case 400: // Misconfigured
            return false;

        case 102: // Preparing
        case 103: // Printing
        case 302: // Failed
        case 303: // Error
        case 104: // Paused
        case 105: // Finished
            return true;

        default:
            return false;
    }
}

function PrinterDetailHeader({ printer }: { printer: ThreeDPrinter }) {
    return (
        <Paper p='sm' radius='xs' shadow='xs'>
            <Group
                justify='space-between'
                gap='xs'
                wrap='nowrap'
                align='flex-start'
            >
                <Group
                    justify='space-between'
                    wrap='nowrap'
                    align='flex-start'
                    style={{ flexGrow: 1 }}
                >
                    <Group
                        justify='start'
                        wrap='nowrap'
                        align='flex-start'
                    >
                        <Stack gap='xs'>
                            <StylishText size='lg'>
                                {printer.name}
                            </StylishText>

                            {(printer.manufacturer || printer.model) && (
                                <Group gap='xs'>
                                    <Text size='sm'>
                                        {printer.manufacturer}{' '}
                                        {printer.model}
                                    </Text>
                                </Group>
                            )}
                        </Stack>
                    </Group>
                </Group>

                 <Group
                    gap={5}
                    justify='right'
                    wrap='nowrap'
                    align='center'
                    style={{ alignSelf: 'center' }}
                >
                    <Badge
                        color={getStatusColor(printer.status)}
                        variant='light'
                        size='lg'
                    >
                        {printer.status_text}
                    </Badge>
                    <CameraButton
                        printerPk={printer.pk}
                        printerName={printer.name}
                    />
                </Group>
            </Group>
        </Paper>
    );
}

function PrinterCamera() {
    return (
        <Stack gap='md'>
            <Text>Printer camera</Text>
            <Text c='dimmed'>
                Camera feed will be displayed here.
            </Text>
        </Stack>
    );
}

function PrinterControls() {
    return (
        <Stack gap='md'>
            <Text>Printer controls</Text>
            <Text c='dimmed'>
                Printer controls will be displayed here.
            </Text>
        </Stack>
    );
}

function PrinterDetailsPage({
    context: _context,
}: {
    context: InvenTreePluginContext;
}) {
    const pathParts = window.location.pathname.split('/');
    const detailsIndex = pathParts.indexOf('3dprinterdetails');
    const pk =
        detailsIndex >= 0
            ? pathParts[detailsIndex + 1]
            : undefined;

    const [printer, setPrinter] =
        useState<ThreeDPrinter | null>(null);

    useEffect(() => {
        if (!pk) {
            console.error('[Bambu] No printer PK found in URL');
            return;
        }

        const fetchLiveData = () => {
            const url =
                `/plugin/inventree_bambu/get_printer_data/${encodeURIComponent(pk)}`;

            fetch(url, {
                cache: 'no-store',
            })
                .then((res) => {
                    if (!res.ok) {
                        throw new Error(
                            `get_printer_data failed: ${res.status}`,
                        );
                    }

                    return res.json();
                })
                .then((data: ThreeDPrinter) => {
                    setPrinter(data);
                })
                .catch((error) => {
                    console.error('[Bambu] Live printer request failed:', error);
                });
        };

        // Call immediately.
        fetchLiveData();

        // Then every second.
        const interval = setInterval(fetchLiveData, 1000);

        return () => {
            clearInterval(interval);
        };
    }, [pk]);

    if (!printer) {
        return <Text>Printer not found: {pk}</Text>;
    }

    const printerPanels: PanelType[] = [
        {
            name: 'details',
            label: 'Printer Details',
            icon: <IconInfoCircle />,
            content: (
                <PrinterDetailsPanel
                    printer={printer}
                    context={_context}
                />
            ),
        },
        // {
        //     name: 'controls',
        //     label: 'Controls',
        //     icon: <IconDeviceGamepad3 />,
        //     content: <PrinterControls />,
        // },
        {
            name: 'ams',
            label: 'AMS',
            icon: <IconCircleLetterA />,
            content: (
                <AMSDetailsPanel
                    printer={printer}
                    context={_context}
                />
            ),
        },
        // {
        //     name: 'scheduledjobs',
        //     label: 'Scheduled Jobs',
        //     icon: <IconClipboardList />,
        //     content: (
        //         <PrinterDetailsPage printer={printer} />
        //     ),
        // },
        // {
        //     name: 'jobhistory',
        //     label: 'Job History',
        //     icon: <IconHistory />,
        //     content: (
        //         <PrinterDetailsPage printer={printer} />
        //     ),
        // },
        // {
        //     name: 'errorhistory',
        //     label: 'Error History',
        //     icon: <IconExclamationCircle />,
        //     content: (
        //         <PrinterDetailsPage printer={printer} />
        //     ),
        // },
        // {
        //     name: 'maintenance',
        //     label: 'Maintenance',
        //     icon: <IconTool />,
        //     content: (
        //         <PrinterDetailsPage printer={printer} />
        //     ),
        // },
        {
            name: 'files',
            label: 'Printer Files',
            icon: <IconFile />,
            content: (
                <FilesPanel
                        printer={printer}
                        context={_context}
                />
            ),
        },
        // {
        //     name: 'camera',
        //     label: 'Camera',
        //     icon: <IconCamera />,
        //     content: <PrinterCamera />,
        // },
    ];

    return (
        <Stack
            gap='md'
            style={{
                height: '100%',
            }}
        >
            <PrinterDetailHeader printer={printer} />

            <PanelGroup panels={printerPanels} />
        </Stack>
    );
}

export function render3DPrintersPanel(
    context: InvenTreePluginContext,
) {
    checkPluginVersion(context);

    return <PrinterDetailsPage context={context} />;
}