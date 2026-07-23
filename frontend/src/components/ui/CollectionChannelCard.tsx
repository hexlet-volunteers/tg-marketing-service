import { Avatar, Grid, Group, Paper, Stack, Text } from "@mantine/core";

export default function CollectionChannelCard(props: {
  initials: string;
  color: string;
  name: string;
  username: string;
  subs: string;
  er: string;
  growth: string;
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
          {props.initials}
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
            {props.subs}
          </Text>
        </Grid.Col>

        <Grid.Col span={4}>
          <Text size="xs" c="dimmed">
            ER
          </Text>

          <Text fw={700} c="tggreen">
            {props.er}
          </Text>
        </Grid.Col>

        <Grid.Col span={4}>
          <Text size="xs" c="dimmed" ta="right">
            30д
          </Text>

          <Text fw={700} c="tggreen" ta="right">
            {props.growth}
          </Text>
        </Grid.Col>
      </Grid>
    </Paper>
  );
}
