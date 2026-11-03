import { Button, List, Paper, Stack, Text, Title } from '@mantine/core';

/**
 * Компонент карточки тарифа.
 *
 * Получает данные для отображения через пропсы: 
 * название тарифа (name), цена (price), период оплаты (period), особенности (features), тип (type).
 * 
 * Тип тарифа задает оформление карточки (appearance) и текст кнопки (buttonLabel)
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
  type: TariffType;
}

const tariffStyles: Record<TariffType, { border: string; buttonColour: string; buttonLabel: string }> = {
  free: { border: "1px solid #e9ecef", buttonColour: "#868e96", buttonLabel: "Текущий план" },
  pro: { border: "2px solid #229ED9", buttonColour: "#229ED9", buttonLabel: "Перейти на Pro" },
  agency: { border: "1px solid #e9ecef", buttonColour: "#101216", buttonLabel: "Перейти на Agency" },
};

export default function TariffCard(props: TariffCardProps) {
  const appearence = tariffStyles[props.type];

  return (
    <Paper
      withBorder
      radius="lg"
      p="lg"
      style={{ display: "flex", minWidth: 0, border: appearence.border }}
    >
      <Stack gap={5} style={{ flex: 1 }}>
        <Title order={3} fz={14} fw={800}>{props.name}</Title>
        <div>
          <Text fz={22} fw={800}>{props.price}</Text>
          <Text fz={11} c="#868e96">{props.period}</Text>
        </div>
        <List
          fz={11.5}
          c="#868e96"
          spacing="sm"
          icon={<Text fz={11.5} c="green">✓</Text>}
        >
          {props.features.map((feature) => (
            <List.Item key={feature}>{feature}</List.Item>
          ))}
        </List>
        <Button mt="auto" fullWidth fz={12} fw={700} radius="md" color={appearence.buttonColour}>
          {appearence.buttonLabel}
        </Button>
      </Stack>
    </Paper>
  )
}