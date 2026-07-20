import { Text, Stack, Collapse, UnstyledButton, Flex } from '@mantine/core';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import type { FaqAccordionItemProps } from '../model/types';

export const FaqItem: React.FC<FaqAccordionItemProps> = ({
  question,
  answer,
  isOpen,
  onToggle,
}) => {
  return (
    <Stack gap={0} bd="1px solid var(--mantine-color-muted-3)">
      <UnstyledButton onClick={onToggle} w="100%" ta="left" p="12px 16px" bg="white">
        <Flex align="center" justify="space-between" w="100%">
          <Text fw={700} size="base">
            {question}
          </Text>
          {isOpen ? (
            <IconChevronUp size={16} color="var(--mantine-color-muted-5)" />
          ) : (
            <IconChevronDown size={16} color="var(--mantine-color-muted-5)" />
          )}
        </Flex>
      </UnstyledButton>
      <Collapse expanded={isOpen} transitionDuration={200}>
        <Text
          size="md"
          px={16}
          pb={12}
          pt={4}
          color="dimmed"
          ta="left"
        >
          {answer}
        </Text>
      </Collapse>
    </Stack>
  );
};
