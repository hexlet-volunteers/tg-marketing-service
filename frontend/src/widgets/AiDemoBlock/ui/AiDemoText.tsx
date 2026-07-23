import React from 'react';
import { Text, Stack, Group, ThemeIcon, Button } from '@mantine/core';
import { IconSparkles, IconPlayerPlay } from '@tabler/icons-react';
import { IconCheck } from '@tabler/icons-react';
import type { AiDemoTextProps } from '../model/types';

export const AiDemoText: React.FC<AiDemoTextProps> = (props) => {
  const {
    description,
    features = [],
    tryButton,
    demoButton,
    activeButton,
    onButtonClick,
  } = props;

  return (
    <Stack>
      {description && (
        <Text c="dimmed">{description}</Text>
      )}

      <Stack gap={8}>
        {features.map((f) => (
          <Group key={f.id} gap={8} wrap="nowrap">
            <ThemeIcon size="sm" color="green.6" variant="subtle">
              <IconCheck size={18} />
            </ThemeIcon>
            <Text size="sm" c="dimmed">{f.text}</Text>
          </Group>
        ))}
      </Stack>

      <Group gap="md" mt="md">
        {tryButton && (
          <Button
            onClick={() => onButtonClick(tryButton)}
            variant={activeButton === tryButton.label ? 'filled' : 'outline'}
            color={activeButton === tryButton.label ? 'blue.6' : 'gray'}
            leftSection={<IconSparkles size={18} />}
          >
            {tryButton.label}
          </Button>
        )}
        {demoButton && (
          <Button
            onClick={() => onButtonClick(demoButton)}
            variant={activeButton === demoButton.label ? 'filled' : 'outline'}
            color={activeButton === demoButton.label ? 'blue.6' : 'gray'}
            leftSection={<IconPlayerPlay size={18} />}
          >
            {demoButton.label}
          </Button>
        )}
      </Group>
    </Stack>
  );
};
