import { useEffect, useState } from 'react';
import { ActionIcon, Alert, Center, Loader, Modal, Stack, Tooltip, Text } from '@mantine/core';
import { IconCamera } from '@tabler/icons-react';
import { StylishText } from '@inventreedb/ui';

export function CameraModal({
    printerPk,
    printerName,
    opened,
    onClose,
}: {
    printerPk: string;
    printerName: string;
    opened: boolean;
    onClose: () => void;
}) {
    const [mode, setMode] = useState<'video' | 'mjpeg'>('video');
    const [failed, setFailed] = useState(false);

    // Start fresh each time the modal opens: try video first
    useEffect(() => {
        if (opened) {
            setMode('video');
            setFailed(false);
        }
    }, [opened]);

    const streamUrl =
        `/plugin/inventree_bambu/get_camera_stream/${encodeURIComponent(printerPk)}`

    const mediaStyle = {
        position: 'relative' as const, // sits above the loader once the picture arrives
        width: '100%',
        display: 'block',
        borderRadius: 4,
    };

    return (
        <Modal opened={opened} onClose={onClose} title={<StylishText size='xl'>{`${printerName} - Live Camera`}</StylishText>} size='xl'>
            {failed ? (
                <Alert color='red' title='Camera unavailable'>
                    Failed to connect to the printer's camera.
                </Alert>
            ) : (
                <div style={{ position: 'relative', minHeight: 300 }}>
                    <Center pos='absolute' inset={0}>
                        <Stack align='center' gap='xs'>
                            <Loader />
                            <Text size='sm' c='dimmed'>Connecting to the printer's camera…</Text>
                        </Stack>
                    </Center>

                    {mode === 'video' ? (
                        // On failure, switch to JPEG
                        <video key='video' src={streamUrl} autoPlay muted playsInline onError={() => setMode('mjpeg')} style={mediaStyle}/>
                    ) : (
                        // On failure, display an error message
                        <img key='mjpeg' src={streamUrl} alt={`${printerName} camera`} onError={() => setFailed(true)} style={mediaStyle}/>
                    )}
                </div>
            )}
        </Modal>
    );
}