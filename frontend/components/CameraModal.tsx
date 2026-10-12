import { useEffect, useState } from 'react';
import { ActionIcon, Alert, Center, Loader, Modal, Stack, Text, Tooltip } from '@mantine/core';
import { IconCamera } from '@tabler/icons-react';
import { StylishText } from '@inventreedb/ui';

const POLL_INTERVAL = 1000; // ms between frames
const MAX_FAILURES = 15;    // consecutive failures before showing an error

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
    const [frameUrl, setFrameUrl] = useState<string | null>(null);
    const [failed, setFailed] = useState(false);

    const [useVideo, setUseVideo] = useState(true);
    const [videoPlaying, setVideoPlaying] = useState(false);

    // RTSP Printers
    useEffect(() => {
        if (opened) {
            setUseVideo(true);
            setVideoPlaying(false);
        }
    }, [opened]);

    // JPEG Printers
    useEffect(() => {
        // Only poll while the modal is open, so the printer's camera connection
        // times out on the server once nobody is watching
        if (!opened || useVideo) return;

        const url = `/plugin/inventree_bambu/get_camera_frame/${encodeURIComponent(printerPk)}`;
        let cancelled = false;
        let timer: ReturnType<typeof setTimeout>;
        let failures = 0;
        let currentUrl: string | null = null;

        const poll = async () => {
            try {
                const response = await fetch(url, { cache: 'no-store' });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const blob = await response.blob();
                if (cancelled) return;

                const nextUrl = URL.createObjectURL(blob);
                setFrameUrl(nextUrl);
                if (currentUrl) URL.revokeObjectURL(currentUrl);
                currentUrl = nextUrl;

                failures = 0;
                setFailed(false);
            } catch {
                // 503 = camera still connecting; keep trying, but give up eventually
                failures++;
                if (failures >= MAX_FAILURES) setFailed(true);
            }

            // Schedule the next frame only after this one finishes, so requests never pile up
            if (!cancelled) timer = setTimeout(poll, POLL_INTERVAL);
        };

        poll();

        return () => {
            cancelled = true;
            clearTimeout(timer);
            if (currentUrl) URL.revokeObjectURL(currentUrl);
            setFrameUrl(null);
            setFailed(false);
        };
    }, [opened, useVideo, printerPk]);

    return (
        <Modal opened={opened} onClose={onClose} title={<StylishText size='xl'>{`${printerName} - Live Camera`}</StylishText>} size='xl' centered>
            {useVideo ? (
                <div style={{ position: 'relative' }}>
                    <video
                        src={`/plugin/inventree_bambu/get_camera_video/${encodeURIComponent(printerPk)}`}
                        autoPlay
                        muted
                        playsInline
                        onPlaying={() => setVideoPlaying(true)}
                        onError={() => setUseVideo(false)} // P1/A1 camera, or browser can't play it
                        style={{ width: '100%', display: 'block', borderRadius: 4 }}
                    />
                    {!videoPlaying && (
                        <Center pos='absolute' inset={0}>
                            <Loader />
                        </Center>
                    )}
                </div>
            ): failed ? (
                <Alert color='red' title='Camera unavailable'>
                    Could not get a picture from the printer. Check that it's online and that LAN
                    Live View is enabled.
                </Alert>
            ) : frameUrl ? (
                <img
                    src={frameUrl}
                    alt={`${printerName} camera`}
                    style={{ width: '100%', display: 'block', borderRadius: 4 }}
                />
            ) : (
                <Center h={300}>
                    <Stack align='center' gap='xs'>
                        <Loader />
                        <Text size='sm' c='dimmed'>Connecting to camera…</Text>
                    </Stack>
                </Center>
            )}
        </Modal>
    );
}

export function CameraButton({ printerPk, printerName }: { printerPk: string; printerName: string }) {
    const [opened, setOpened] = useState(false);

    return (
        <>
            <Tooltip label='Live Camera'>
                <ActionIcon
                    variant='light'
                    size='lg'
                    onClick={(e) => {
                        e.stopPropagation(); // don't trigger a clickable tile or row underneath
                        setOpened(true);
                    }}
                >
                    <IconCamera />
                </ActionIcon>
            </Tooltip>

            <CameraModal
                printerPk={printerPk}
                printerName={printerName}
                opened={opened}
                onClose={() => setOpened(false)}
            />
        </>
    );
}