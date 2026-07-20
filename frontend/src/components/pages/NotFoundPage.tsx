import { Button, Container, Group, Stack, Text, Title } from "@mantine/core";
import { useNavigate } from 'react-router-dom';

export default function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <Container>
    <Stack align="center" gap="xs">
      <Title
        order={1}
        c="tgblue"
        fz={120}
        lh={1}
        fw={700}
      >
        404
      </Title>

      <Title order={2}>Страница не найдена</Title>

      <Text c="dimmed" ta="center" maw={520}>
        Возможно, канал удалён или ссылка устарела. Попробуйте начать с
        главной или загляните в каталог.
      </Text>

      <Group mt="md">
        <Button radius="md" onClick={() => navigate('/')}>На главную</Button>
        <Button variant="default" radius="md" onClick={() => navigate('/channels')}>
          В каталог
        </Button>
      </Group>
    </Stack>
    </Container>
  );
}
