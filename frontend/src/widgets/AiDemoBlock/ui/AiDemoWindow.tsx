import React from 'react';
import { Text, Paper, Flex } from '@mantine/core';
import type { AiDemoBlockProps } from '../model/types';

export const AiDemoWindow: React.FC<AiDemoBlockProps> = (props) => {
  const { demoTitle } = props;

  return (
    <Paper
      p="md"
      radius="xl"
      flex={1}
      mih="15rem"
    >
      <Flex
        w="100%"
        h="100%"
        justify="center"
        align="center"
        p={16}
        bg="muted.0"
        bdrs={8}
      >
        <Text fz={48} c="dimmed">{demoTitle || 'AI Assistant Chat'}</Text>
      </Flex>
    </Paper>
  );
};
