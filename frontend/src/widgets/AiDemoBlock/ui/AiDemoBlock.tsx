import React from 'react';
import { Container, Title, Group, Box, Flex } from '@mantine/core';
import { AiDemoText } from './AiDemoText';
import { AiDemoWindow } from './AiDemoWindow';
import { useAiDemo } from '../model/useAiDemo';

export const AiDemoBlock: React.FC = () => {
  const { data, activeButton, handleButtonClick } = useAiDemo();

  return (
    <Box component="section" w="100%" p={40}>
      <Container px="md">
        <Group align="stretch" gap="xl" wrap="wrap">
          <Box flex="1 1 0" miw={300}>
            <Title order={2} mb="md">ИИ-помощник редактора</Title>
            <AiDemoText
              {...data}
              activeButton={activeButton}
              onButtonClick={handleButtonClick}
            />
          </Box>

          <Flex flex="1 1 0" miw={300}>
            <AiDemoWindow demoTitle={data.demoTitle} />
          </Flex>
        </Group>
      </Container>
    </Box>
  );
};
