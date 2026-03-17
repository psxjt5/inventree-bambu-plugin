import type { InvenTreePluginContext } from '@inventreedb/ui';
import { Alert, Button, Text } from '@mantine/core';
import { notifications } from '@mantine/notifications';

function PluginSettingsDisplay({
    context: _context
}: {
    context: InvenTreePluginContext;
}) {

    return (
        <Alert color='blue' title='Hello World'>
            <Text>This is a custom settings page for the InvenTreeBambuLabMachines plugin!</Text>
            <Text>Custom UI elements can be rendered here</Text>
            <Button color="blue" onClick={() => {
                notifications.show({
                    title: 'Hello World',
                    message: 'This is a custom notification from the InvenTreeBambuLabMachines plugin!',
                    color: 'blue',
                });
            }}>
                Click Me!
            </Button>
        </Alert>
    )

}


export function renderPluginSettings(context: InvenTreePluginContext) {
    return (
        <PluginSettingsDisplay context={context} />
    );
}