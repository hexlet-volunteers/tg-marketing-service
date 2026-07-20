import React from 'react';
import { Paper, Text } from '@mantine/core';

type InsightColor = 'green' | 'blue' | 'purple' | 'orange';

const colorMap: Record<InsightColor, { bg: string; border: string; text: string }> = {
  green:  { bg: 'var(--mantine-color-tggreen-0)', border: 'var(--mantine-color-tggreen-5)', text: 'var(--mantine-color-tggreen-5)' },
  blue:   { bg: 'var(--mantine-color-tgblue-0)', border: 'var(--mantine-color-tgblue-6)', text: 'var(--mantine-color-tgblue-6)' },
  purple: { bg: 'var(--mantine-color-tgpurple-0)', border: 'var(--mantine-color-tgpurple-5)', text: 'var(--mantine-color-tgpurple-5)' },
  orange: { bg: 'var(--mantine-color-tgorange-0)', border: 'var(--mantine-color-tgorange-6)', text: 'var(--mantine-color-tgorange-6)' },
};

interface InsightCardProps {
  color: InsightColor;
  label?: string;
  children: React.ReactNode;
}

export const InsightCard: React.FC<InsightCardProps> = ({ color, label, children }) => {
  const palette = colorMap[color];

  return (
    <Paper
      p="sm"
      radius="md"
      bg={palette.bg}
      styles={{
        root: {
          borderLeft: '4px solid',
          borderLeftColor: palette.border,
          borderRadius: '0 8px 8px 0',
        },
      }}
    >
      {label && (
        <Text
          fz="10px"
          fw={800}
          mb={4}
          lts="0.5px"
          c={palette.text}
        >
          {label}
        </Text>
      )}
      {children}
    </Paper>
  );
};
