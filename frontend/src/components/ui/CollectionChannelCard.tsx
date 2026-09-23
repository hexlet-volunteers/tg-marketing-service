import { Avatar, Grid, Group, Paper, Stack, Text } from "@mantine/core";
import { formatNumberShortEn } from "@/utils/formatNumberShort";
import { initials } from "@/utils/initials";

export default function CollectionChannelCard(props: {
  color: string;
  name: string;
  username: string;
  subscribers: number;
  er: number;
  growth30d: number;
}) {
  return (
    <Paper withBorder shadow="xs" p="md">
      <Group align="flex-start" mb="lg">
        <Avatar
          radius="lg"
          color="white"
          bg={props.color}
          fw={700}
        >
          {initials(props.name)}
        </Avatar>

        <Stack gap={0}>
          <Text fw={700} size="lg">
            {props.name}
          </Text>

          <Text size="sm" c="dimmed">
            {props.username}
          </Text>
        </Stack>
      </Group>

      <Grid gap="md">
        <Grid.Col span={4}>
          <Text size="xs" c="dimmed">
            Подписчики
          </Text>

          <Text fw={700} size="xl">
            {formatNumberShortEn(props.subscribers)}
          </Text>
        </Grid.Col>

        <Grid.Col span={4}>
          <Text size="xs" c="dimmed">
            ER
          </Text>

          <Text fw={700} c="tggreen">
            {`${props.er.toFixed(1).replace(/\.0$/, '')}%`}
          </Text>
        </Grid.Col>

        <Grid.Col span={4}>
          <Text size="xs" c="dimmed" ta="right">
            30д
          </Text>

          <Text fw={700} c={props.growth30d ? 'tggreen' : 'tgred'} ta="right">
            {props.growth30d > 0 
              ? `+${props.growth30d.toLocaleString('ru-RU')}` 
              : props.growth30d.toLocaleString('ru-RU')
            }
          </Text>
        </Grid.Col>
      </Grid>
    </Paper>
  );
}
