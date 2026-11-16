import { Button, List, Paper, Stack, Text, Title } from '@mantine/core';

/**
 * Компонент карточки тарифа.
 *
 * Получает данные для отображения через пропсы: 
 * название тарифа (name), цена (price), период оплаты (period), особенности (features), тип (type) и текст кнопки (buttonLabel).
 * 
 * Тип тарифа задает оформление карточки (appearance)
 * через заранее созданные типом TariffType и набор стилей tariffStyles.
 * 
 * Позже будет добавлена возможность перехода на выбранный тариф при нажатии кнопки соответствующей карточки.
 */

type TariffType = "free" | "pro" | "agency";

interface TariffCardProps {
  name: string;
  price: string;
  period: string;
  features: string[];
  buttonLabel: string;
  type: TariffType;
}

const tariffStyles: Record<TariffType, { border: string; buttonColour: string }> = {
  free: { border: "1px solid var(--mantine-color-muted-2)", buttonColour: "muted.5" },
  pro: { border: "2px solid var(--mantine-color-tgblue-5)", buttonColour: "tgblue.5" },
  agency: { border: "1px solid var(--mantine-color-muted-2)", buttonColour: "primary.9" },
};

export default function TariffCard(props: TariffCardProps) {
  const appearence = tariffStyles[props.type];

  return (
    <Paper
      p="lg"
      style={{ display: "flex", minWidth: 0, border: appearence.border }}
    >
      <Stack gap="xs" style={{ flex: 1 }}>
        <Title order={3} size="h4" fw="bold">{props.name}</Title>
        <div>
          <Text fz="xl" fw="bold">{props.price}</Text>
          <Text fz="xs" c="muted.5">{props.period}</Text>
        </div>
        <List
          fz="xs"
          c="muted.5"
          spacing="sm"
          icon={<Text fz="xs" c="tggreen.5">✓</Text>}
        >
          {props.features.map((feature) => (
            <List.Item key={feature}>{feature}</List.Item>
          ))}
        </List>
        <Button mt="auto" fullWidth fz="xs" fw="bold" radius="md" color={appearence.buttonColour}>
          {props.buttonLabel}
        </Button>
      </Stack>
    </Paper>
  )
}