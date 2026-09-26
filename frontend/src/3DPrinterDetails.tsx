import { Group, Paper, Stack, Tabs, Text } from '@mantine/core';
import { checkPluginVersion, StylishText, type PanelType, type InvenTreePluginContext } from '@inventreedb/ui';
import { useEffect, useState } from 'react';
import { IconInfoCircle, IconCamera, IconFile, IconPlayerPlay, IconPrinter, IconClipboardList, IconHistory, IconTool, IconCircleLetterA, IconExclamationCircle, IconDeviceGamepad3} from '@tabler/icons-react';

import { PanelGroup } from '../components/PanelGroup'
import { PrinterDetailsPanel } from '../components/PrinterDetailsPanel'

type ThreeDPrinter = {
    pk: string;
    name: string;
    status: number;
    status_text: string;
    progress: number;
    file_name: string;
    manufacturer: string;
    model: string;
    remaining_time: string;
};

function PrinterDetailHeader({ printer }: { printer: ThreeDPrinter }) {
    return (
        <Paper p='xs' radius='xs' shadow='xs'>
            <Group justify='space-between' gap='xs' wrap='nowrap' align='flex-start'>
                <Group justify='space-between' wrap='nowrap' align='flex-start' style={{ flexGrow: 1 }}>
                    <Group justify='start' wrap='nowrap' align='flex-start'>
                        <Stack gap='xs'>
                            <StylishText size='lg'>{printer.name}</StylishText>

                            {(printer.manufacturer || printer.model) && (
                                <Group gap='xs'>
                                    <Text size='sm'>{printer.manufacturer} {printer.model}</Text>
                                </Group>
                            )}
                        </Stack>
                    </Group>
                </Group>

                {/* Action buttons go here */}
                <Group gap={5} justify='right' wrap='nowrap' align='center' />
            </Group>
        </Paper>
    );
}

function PrinterOverview({ printer }: { printer: ThreeDPrinter }) {
    return <PrinterDetailsPanel printer={printer} />;
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

function PrinterFiles() {
    return (
        <Stack gap='md'>
            <Text>Printer files</Text>
            <Text c='dimmed'>
                Files available on the printer will be displayed here.
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

function PrinterFilament() {
    return (
        <Stack gap='md'>
            <Text>Filament</Text>
            <Text c='dimmed'>
                AMS and filament information will be displayed here.
            </Text>
        </Stack>
    );
}

function PrinterDetails({ context }: { context: InvenTreePluginContext }) {
    const pathParts = window.location.pathname.split('/');
    const detailsIndex = pathParts.indexOf('3dprinterdetails');
    const pk = detailsIndex >= 0 ? pathParts[detailsIndex + 1] : undefined;

    const [printer, setPrinter] = useState<ThreeDPrinter | null>(null);

    useEffect(() => {
        if (!pk) {
            return;
        }

        fetch('/plugin/inventree_bambu/get_printer_tiles_data')
            .then((res) => res.json())
            .then((data: ThreeDPrinter[]) => {
                const matchingPrinter = data.find((printer) => String(printer.pk) === pk);
                setPrinter(matchingPrinter ?? null);
            })
            .catch(() => {
                setPrinter(null);
            });
    }, [pk]);

    if (!printer) {
        return <Text>Printer not found: {pk}</Text>;
    }

    const printerPanels: PanelType[] = [
    {
        name: 'overview',
        label: 'Overview',
        icon: <IconInfoCircle/>,
        content: <PrinterOverview printer={printer} />,
    },
    {
        name: 'controls',
        label: 'Controls',
        icon: <IconDeviceGamepad3/>,
        content: <PrinterControls />,
    },
    {
        name: 'ams',
        label: 'AMS',
        icon: <IconCircleLetterA/>,
        content: <PrinterFilament />,
    },
    {
        name: 'scheduledjobs',
        label: 'Scheduled Jobs',
        icon: <IconClipboardList/>,
        content: <PrinterOverview printer={printer} />,
    },
    {
        name: 'jobhistory',
        label: 'Job History',
        icon: <IconHistory/>,
        content: <PrinterOverview printer={printer} />,
    },
    {
        name: 'errorhistory',
        label: 'Error History',
        icon: <IconExclamationCircle/>,
        content: <PrinterOverview printer={printer} />,
    },
    {
        name: 'maintenance',
        label: 'Maintenance',
        icon: <IconTool/>,
        content: <PrinterOverview printer={printer} />,
    },
    {
        name: 'files',
        label: 'Printer Files',
        icon: <IconFile/>,
        content: <PrinterFiles />,
    },
    {
        name: 'camera',
        label: 'Camera',
        icon: <IconCamera/>,
        content: <PrinterCamera />,
    },
  ];

  return (
    <Stack gap='md' style={{height: '100%',}}>
        <PrinterDetailHeader printer={printer} />

        <PanelGroup panels={printerPanels}/>
    </Stack>
  );
}

export function render3DPrintersPanel(context: InvenTreePluginContext) {
    checkPluginVersion(context);

    return <PrinterDetails context={context} />;
}