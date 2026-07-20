import React from 'react';
import { Group, Paper, Title } from '@mantine/core';
import type { MantineSpacing } from '@mantine/core';

interface SectionCardProps {
  title: string;
  titleOrder?: 1 | 2 | 3 | 4 | 5 | 6;
  action?: React.ReactNode;
  padding?: MantineSpacing;
  children: React.ReactNode;
}

export const SectionCard: React.FC<SectionCardProps> = ({
  title,
  titleOrder = 3,
  action,
  padding = 'lg',
  children,
}) => {
  return (
    <Paper withBorder p={padding} radius="md">
      <Group justify="space-between" mb="md">
        <Title order={titleOrder}>{title}</Title>
        {action}
      </Group>
      {children}
    </Paper>
  );
};
