import {
    ActionIcon,
    Box,
    Divider,
    Group,
    Indicator,
    type MantineColor,
    Paper,
    Stack,
    Tabs,
    Text,
    Tooltip,
} from '@mantine/core';
import {
    IconLayoutSidebarLeftCollapse,
    IconLayoutSidebarRightCollapse,
} from '@tabler/icons-react';
import {
    type ReactNode,
    useCallback,
    useMemo,
    useState,
} from 'react';

import {
    Boundary,
    StylishText,
    type PanelGroupType,
    type PanelIndicatorType,
    type PanelType,
} from '@inventreedb/ui';

import { t } from '@lingui/core/macro';
import { useWindowEvent } from '@mantine/hooks';
import { modals } from '@mantine/modals';

export type PanelProps = {
    panels: PanelType[];
    groups?: PanelGroupType[];
};

/**
 * Render a single panel tab within the side menu
 */
function PanelTabComponent({
    expanded,
    panel,
    selected,
}: {
    expanded: boolean;
    panel: PanelType;
    selected: boolean;
}) {
    const isDynamicDot = typeof panel.notification_dot === 'function';

    const indicatorValue: PanelIndicatorType | undefined =
        isDynamicDot
            ? undefined
            : (panel.notification_dot as PanelIndicatorType | undefined);

    const indicatorColor: MantineColor | undefined = useMemo(() => {
        switch (indicatorValue) {
            case 'info':
                return 'blue';
            case 'warning':
                return 'yellow';
            case 'danger':
                return 'red';
            default:
                return undefined;
        }
    }, [indicatorValue]);

    return (
        <Tooltip
            label={panel.label ?? panel.name}
            key={panel.name}
            disabled={expanded}
            position='right'
        >
            <Tabs.Tab
                p='xs'
                key={`panel-label-${panel.name}`}
                w='100%'
                value={panel.name}
                leftSection={
                    <Indicator
                        position='top-end'
                        disabled={!indicatorColor}
                        color={indicatorColor}
                        withBorder
                        size={14}
                    >
                        {panel.icon}
                    </Indicator>
                }
                hidden={panel.hidden}
                disabled={panel.disabled}
                style={{
                    cursor: panel.disabled ? 'unset' : 'pointer',
                    backgroundColor: selected
                        ? 'var(--mantine-primary-color-light)'
                        : undefined,
                }}
            >
                <Group justify='left' gap='xs' wrap='nowrap'>
                    {expanded && (
                        <Text size='md'>
                            {panel.label}
                        </Text>
                    )}
                </Group>
            </Tabs.Tab>
        </Tooltip>
    );
}

function BasePanelGroup({
    panels,
    groups,
    selectedPanel,
    onPanelChange,
}: Readonly<
    PanelProps & {
        selectedPanel: string;
        onPanelChange: (panel: string) => void;
    }
>): ReactNode {
    const [expanded, setExpanded] = useState<boolean>(true);

    const [allPanels, groupedPanels] = useMemo(() => {
        const _grouped_panels: PanelGroupType[] = [];
        const _panels = [...panels];
        const _allpanels: PanelType[] = [...panels];

        groups?.forEach((group) => {
            const newVal: any = { ...group, panels: [] };

            group.panelIDs?.forEach((panelID) => {
                const index = _panels.findIndex(
                    (p) => p.name === panelID
                );

                if (index !== -1) {
                    newVal.panels.push(_panels[index]);
                    _panels.splice(index, 1);
                }
            });

            _grouped_panels.push(newVal);
        });

        if (_panels.length > 0) {
            _grouped_panels.push({
                id: 'ungrouped',
                label: '',
                panels: _panels,
            });
        }

        return [_allpanels, _grouped_panels];
    }, [groups, panels]);

    const [isDirty, setIsDirty] = useState(false);

    useWindowEvent('beforeunload', (event) => {
        if (isDirty) {
            event.preventDefault();
        }
    });

    const handlePanelChange = useCallback(
        (targetPanel: string) => {
            if (isDirty) {
                modals.openConfirmModal({
                    // existing modal...
                });
                return;
            }

            onPanelChange(targetPanel);
            setIsDirty(false);
        },
        [isDirty, onPanelChange]
    );

    return (
        <Boundary label='PanelGroup'>
            <Paper p='sm' radius='xs' shadow='xs' style={{flex: 1, minHeight: 0}}>
                <Tabs
                    orientation='vertical'
                    keepMounted={false}
                    value={selectedPanel}
                    onChange={(value) => {
                        if (value) {
                            handlePanelChange(value);
                        }
                    }}
                    aria-label='panel-group'
                    style={{
                      height: '100%'
                    }}
                >
                    <Tabs.List
                        justify='left'
                        aria-label='panel-tabs'
                    >
                        {groupedPanels.map((group) => (
                            <Box
                                key={`group-${group.id}`}
                                w='100%'
                            >
                                <Text
                                    hidden={!group.label || !expanded}
                                    key={`group-label-${group.id}`}
                                    style={{
                                        paddingLeft: '10px',
                                    }}
                                >
                                    {group.label}
                                </Text>

                                {group.label && <Divider />}

                                {group.panels?.map(
                                    (panel) =>
                                        !panel.hidden && (
                                            <PanelTabComponent
                                                key={`panel-tab-${group.id}-${panel.name}`}
                                                expanded={expanded}
                                                panel={panel}
                                                selected={
                                                    selectedPanel ===
                                                    panel.name
                                                }
                                            />
                                        )
                                )}
                            </Box>
                        ))}

                        <Divider />

                        <Group wrap='nowrap' gap='xs'>
                            <Tooltip
                                position='right'
                                label={
                                    expanded
                                        ? t`Collapse panels`
                                        : t`Expand panels`
                                }
                            >
                                <ActionIcon
                                    style={{
                                        paddingLeft: '10px',
                                    }}
                                    onClick={() =>
                                        setExpanded(!expanded)
                                    }
                                    variant='transparent'
                                    size='lg'
                                >
                                    {expanded ? (
                                        <IconLayoutSidebarLeftCollapse
                                            opacity={0.75}
                                        />
                                    ) : (
                                        <IconLayoutSidebarRightCollapse
                                            opacity={0.75}
                                        />
                                    )}
                                </ActionIcon>
                            </Tooltip>
                        </Group>
                    </Tabs.List>

                    {allPanels.map(
                        (panel) =>
                            !panel.hidden && (
                                <Tabs.Panel
                                    key={`panel-${panel.name}`}
                                    value={panel.name}
                                    aria-label={`nav-panel-${panel.name}`}
                                    p='sm'
                                    style={{
                                        overflowX: 'scroll',
                                        width: '100%',
                                    }}
                                >
                                    <Stack gap='md'>
                                        {panel.showHeadline !==
                                            false && (
                                            <>
                                                <Group justify='space-between'>
                                                    <StylishText size='xl'>
                                                        {panel.label}
                                                    </StylishText>

                                                    {panel.controls && (
                                                        <Group
                                                            justify='right'
                                                            wrap='nowrap'
                                                        >
                                                            {
                                                                panel.controls
                                                            }
                                                        </Group>
                                                    )}
                                                </Group>

                                                <Divider />
                                            </>
                                        )}

                                        <Boundary
                                            label={`PanelContent-${panel.name}`}
                                        >
                                            {getPanelContent(
                                                panel.content,
                                                panel,
                                                setIsDirty
                                            )}
                                        </Boundary>
                                    </Stack>
                                </Tabs.Panel>
                            )
                    )}
                </Tabs>
            </Paper>
        </Boundary>
    );
}

function getPanelContent(
    content: ReactNode,
    panel: PanelType,
    setIsDirty?: (dirty: boolean) => void
): ReactNode {
    if (content === null) {
        return null;
    }

    if (
        panel.supportsDirty &&
        typeof content === 'object' &&
        'props' in content &&
        setIsDirty
    ) {
        return {
            ...content,
            props: {
                ...(content.props || {}),
                setDirtyCallback: setIsDirty,
            },
        };
    }

    return content;
}

export function PanelGroup(props: Readonly<PanelProps>) {
    const firstPanel =
        props.panels.find(
            (panel) => !panel.disabled && !panel.hidden
        )?.name ?? '';

    const getPanelFromPath = () => {
        const pathParts = window.location.pathname.split('/');
        const detailsIndex =
            pathParts.indexOf('3dprinterdetails');

        if (detailsIndex >= 0) {
            const panel = pathParts[detailsIndex + 2];

            if (
                panel &&
                props.panels.some(
                    (item) =>
                        item.name === panel &&
                        !item.disabled &&
                        !item.hidden
                )
            ) {
                return panel;
            }
        }

        return firstPanel;
    };

    const [selectedPanel, setSelectedPanel] =
        useState(getPanelFromPath);

    const handlePanelChange = (panel: string) => {
        const pathParts = window.location.pathname.split('/');
        const detailsIndex =
            pathParts.indexOf('3dprinterdetails');

        if (detailsIndex < 0) {
            return;
        }

        const newPath = [
            ...pathParts.slice(0, detailsIndex + 2),
            panel,
        ].join('/');

        window.history.pushState({}, '', newPath);
        setSelectedPanel(panel);
    };

    return (
        <BasePanelGroup
            {...props}
            selectedPanel={selectedPanel}
            onPanelChange={handlePanelChange}
        />
    );
}