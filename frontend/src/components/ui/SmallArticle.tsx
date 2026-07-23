import { Badge, Box, Card, Stack, Text } from "@mantine/core";

export default function SmallArticle({
  color,
  category,
  title,
  date,
  time,
  onClick,
}: {
  color: string;
  category: string;
  title: string;
  date: string;
  time: string;
  onClick?: () => void;
}) {
  return (
    <Card withBorder radius="lg" padding={0} onClick={onClick} style={{ overflow: 'hidden' }}>
      <Box h={150} bg={color} />

      <Stack p="md" gap="xs">
        <Badge variant="light" w="fit-content">
          {category}
        </Badge>

        <Text fw={700} size="lg">
          {title}
        </Text>

        <Text c="dimmed" size="sm">
          Небольшое описание статьи в несколько строк.
        </Text>

        <Text size="xs" c="dimmed">
          {date} • {time}
        </Text>
      </Stack>
    </Card>
  );
}
