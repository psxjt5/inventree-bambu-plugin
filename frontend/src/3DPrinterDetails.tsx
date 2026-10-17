import { Alert, Badge, Divider, Group, Paper, Stack, Text } from '@mantine/core';
import {
    checkPluginVersion,
    StylishText,
    type PanelType,
    type InvenTreePluginContext,
    ActionButton,
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
    IconPlayerStop,
    IconPlayerPause,
} from '@tabler/icons-react';

import { PanelGroup } from '../components/PanelGroup';
import { PrinterDetailsPanel } from '../components/PrinterDetailsPanel';
import { AMSDetailsPanel } from '../components/AMSDetailsPanel';
import { FilesPanel } from '../components/FilesPanel';
import { CameraFeedPanel } from '../components/CameraFeedPanel';

import type { ThreeDPrinter } from '../types';

import { CameraModal } from '../components/CameraModal'
import { notifications } from '@mantine/notifications';

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

function printerStoppable(status: number): boolean {
    switch (Number(status)) {
        case 102: // Preparing
        case 103: // Printing
        case 104: // Paused
        case 303: // Error
            return true;
        default:
            return false;
    }
}

function printerPausable(status: number): boolean {
    switch (Number(status)) {
        case 102: // Preparing
        case 103: // Printing
            return true;
        default:
            return false;
    }
}

function PrinterDetailHeader({ printer, context, onOpenCamera, cameraDisabled,  }: { printer: ThreeDPrinter; context: InvenTreePluginContext; onOpenCamera: () => void; cameraDisabled: boolean;}) {

    // Stop Print Confirmation
    const stopPrint = context.forms.delete({
        url: `/plugin/inventree_bambu/stop_print/${encodeURIComponent(printer.pk)}`,
        method: 'POST',
        title: `Stop Current Print on ${printer.name}`,
        preFormContent: (
            <Alert color='red' title='This cannot be undone'>
                Stop the current print on this printer?
            </Alert>
        ),
        successMessage: 'Stopped',
    });

    // Pause Print Request
    const pausePrint = () => {
        context.api
            .post(`/plugin/inventree_bambu/pause_print/${encodeURIComponent(printer.pk)}`)
            .then(() => {
                notifications.show({
                    title: 'Pause requested',
                    message: `Pause command sent to ${printer.name}`,
                    color: 'green',
                });
            })
            .catch((error) => {
                notifications.show({
                    title: 'Could not pause print',
                    message: error.response?.data?.error ?? 'The request failed',
                    color: 'red',
                });
            });
    };

    return (
        <Paper p='sm' radius='xs' shadow='xs'>
            <Group justify='space-between' gap='xs' wrap='nowrap' align='flex-start'>
                <Group justify='space-between' wrap='nowrap' align='flex-start' style={{ flexGrow: 1 }}>
                    <Group justify='start' wrap='nowrap' align='flex-start'>
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

                <Group gap={5} justify='right' wrap='nowrap' align='center' style={{ alignSelf: 'center' }}>
                    <Badge color={getStatusColor(printer.status)} variant='light' size='lg'>
                        {printer.status_text}
                    </Badge>

                    <ActionButton variant='light' icon={<IconCamera />} tooltip='View Printer Camera' disabled={cameraDisabled} tooltipAlignment='bottom' onClick={onOpenCamera}/>

                    <Divider key='divider-1' orientation='vertical' />
                    
                    <ActionButton variant='light' color='#FFA500' icon={<IconPlayerPause />} tooltip='Pause Current Print' disabled={!printerPausable(printer.status)} tooltipAlignment='bottom' onClick={() => pausePrint()}/>
                    <ActionButton variant='light' color='#FF0000' icon={<IconPlayerStop />} tooltip='Stop Current Print' disabled={!printerStoppable(printer.status)} tooltipAlignment='bottom' onClick={() => stopPrint.open()}/>
                </Group>
            </Group>

            {stopPrint.modal}
        </Paper>
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

    const [printer, setPrinter] = useState<ThreeDPrinter | null>(null);
    const [cameraOpened, setCameraOpened] = useState(false);
    const [activePanel, setActivePanel] = useState<string>('');

    useEffect(() => {
        if (!pk) {
            console.error('[Bambu] No printer PK found in URL');
            return;
        }

        const fetchLiveData = () => {
            const url = `/plugin/inventree_bambu/get_printer_data/${encodeURIComponent(pk)}`;

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
            content: <PrinterDetailsPanel printer={printer} context={_context}/>,
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
            content: <AMSDetailsPanel printer={printer} context={_context} />,
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
            content: <FilesPanel printer={printer} context={_context} />,
        },
        {
            name: 'camera',
            label: 'Live Camera',
            icon: <IconCamera />,
            content: <CameraFeedPanel printer={printer} context={_context} />,
        },
    ];

    return (
        <Stack
            gap='md'
            style={{
                height: '100%',
            }}
        >
            <PrinterDetailHeader printer={printer} context={_context} onOpenCamera={() => setCameraOpened(true)} cameraDisabled={activePanel === 'camera'} />

            <PanelGroup panels={printerPanels} onPanelChange={setActivePanel} />

            <CameraModal printerPk={printer.pk} printerName={printer.name} opened={cameraOpened} onClose={() => setCameraOpened(false)}/>
        </Stack>
    );
}

export function render3DPrintersPanel(
    context: InvenTreePluginContext,
) {
    checkPluginVersion(context);

    return <PrinterDetailsPage context={context} />;
}