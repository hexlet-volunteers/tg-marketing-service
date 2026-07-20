import { Badge, Button, Card, Flex, Group, Stack, Text } from '@mantine/core';
import React from 'react';
import type { Tariff } from '../model/types';

interface TariffCardProps extends Tariff {
  onClick?: () => void;
}

export const TariffCard: React.FC<TariffCardProps> = ({
  name,
  period,
  monthlyPrice,
  features,
  button,
  isHighlighted,
  isPopular,
  onClick,
}) => {
  return (
    <Card
      onClick={onClick}
      padding="xl"
      radius="lg"
      pos="relative"
      withBorder
      bd={isHighlighted ? "1px solid var(--mantine-color-tgblue-5)" : "1px solid var(--mantine-color-gray-3)"}
      styles={{ root: { overflow: 'visible', transition: 'border 150ms ease, box-shadow 150ms ease' } }}
    >
      {isPopular && (
        <Badge
          pos="absolute"
          top={-10}
          left={80}
          bg="tgblue.5"
          c="white"
          p="4px 14px"
          bdrs={12}
        >
          Популярный
        </Badge>
      )}

      <Flex direction="column" justify="space-between" h="100%">
        <Stack flex={1}>
          <Text size="md" fw={800} c="primary">{name}</Text>

          <Stack gap={2}>
            <Text fw={800} c="primary" lh={1.1} fz="34px">
              {monthlyPrice === 0 ? '0 ₽' : `${monthlyPrice} ₽`}
            </Text>
            <Text size="xs" c="gray.5">
              {period}
            </Text>
          </Stack>

          <Stack gap="sm" mt="md" mb="xl">
            {features.map((feat) => (
              <Group key={feat.id} gap={8} wrap="nowrap" align="flex-start">
                <Text size="sm" fw={600} c="tggreen.5">✓</Text>
                <Text size="sm" c="muted">{feat.text}</Text>
              </Group>
            ))}
          </Stack>
        </Stack>

        <Button
          size="md"
          color="tgblue"
          fw={700}
          h={44}
          mt="auto"
          styles={{ root: { visibility: isHighlighted ? 'visible' : 'hidden' } }}
        >
          {button.label}
        </Button>
      </Flex>
    </Card>
  );
};
