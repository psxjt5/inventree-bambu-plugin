import {
    Alert,
    Center,
    Loader,
    Stack,
    Text,
} from '@mantine/core';
import { type InvenTreePluginContext } from '@inventreedb/ui';

import type { ThreeDPrinter } from '../types';
import { useState } from 'react';

export function CameraFeedPanel({
    printer,
    context: _context,
}: {
    printer: ThreeDPrinter;
    context: InvenTreePluginContext;
}) {
    const [mode, setMode] = useState<'video' | 'mjpeg'>('video');
    const [failed, setFailed] = useState(false);

    const streamUrl =
            `/plugin/inventree_bambu/get_camera_stream/${encodeURIComponent(printer.pk)}`
    
    const mediaStyle = {
        position: 'relative' as const, // sits above the loader once the picture arrives
        width: '100%',
        display: 'block',
        borderRadius: 4,
    };

    return (
        <Stack gap = "md">
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
                        <img key='mjpeg' src={streamUrl} alt={`${printer.name} camera`} onError={() => setFailed(true)} style={mediaStyle}/>
                    )}
                </div>
            )}
        </Stack>
    )
}