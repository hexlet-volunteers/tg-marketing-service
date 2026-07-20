import React from 'react';
import { Title, Container, SimpleGrid, Box } from '@mantine/core';
import { StepCard } from './StepCard';
import type { ProcessStepsBlocksProps } from '../model/types';
import { useProcessSteps } from '../model/useProcessSteps';

export const ProcessStepsBlocks: React.FC<ProcessStepsBlocksProps> = ({ steps: propsSteps }) => {
  const { steps: stepsFromPage } = useProcessSteps();
  const steps = propsSteps ?? stepsFromPage;

  return (
    <Box component="section" w="100%" bg="muted.0" p={48}>
      <Container px="md">
        <Title order={2} fw={700} mb="xl" ta="left">Как это работает</Title>

        <SimpleGrid cols={{ base: 1, md: 3 }} spacing="lg">
          {steps.map((step, index) => (
            <StepCard
              key={step.id}
              title={step.title}
              description={step.description}
              number={index + 1}
            />
          ))}
        </SimpleGrid>
      </Container>
    </Box>
  );
};
