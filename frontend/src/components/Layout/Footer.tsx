import { Anchor, Avatar, Badge, Box, Group, SimpleGrid, Stack, Text, Title } from '@mantine/core';
import { useNavigate } from 'react-router-dom';

const data = [
  {
    title: 'Продукт',
    links: [
      { label: 'Каталог каналов', link: '#' },
      { label: 'Подборки', link: '#' },
      { label: 'Сравнение', link: '#' },
      { label: 'AI-кабинет', link: '#' },
    ],
  },
  {
    title: 'Компания',
    links: [
      { label: 'Блог', link: '#' },
      { label: 'О сервисе', link: '#' },
      { label: 'Регистрация', link: '#' },
      { label: 'Войти', link: '#' },
    ],
  },
  {
    title: 'Правовое',
    links: [
      { label: 'Конфиденциальность', link: '#' },
      { label: 'Соглашение', link: '#' },
      { label: 'Публичная оферта', link: '#' },
    ],
  },
];

export function Footer() {
  const navigate = useNavigate();
  const groups = data.map((group) => {
    const links = group.links.map((link, index) => (
      <Anchor
        key={index}
        c="dimmed"
        href={link.link}
        size="sm"
        onClick={(event) => event.preventDefault()}
      >
        {link.label}
      </Anchor>
    ));

    return (
      <Stack gap={8} key={group.title}>
        <Text fw={700}>{group.title}</Text>
        {links}
      </Stack>
    );
  });

  return (
    <Box
      component="section"
      mt={40}
      bg="white"
      p={{ base: 24, md: 48 }}
    >
      <SimpleGrid cols={{ base: 2, sm: 2, md: 4 }}>
        <Stack gap={6}>
          <Group>
            <Avatar color="tgblue">t</Avatar>
            <Title order={4}>tgpulse</Title>
          </Group>
          <Text size="sm" c="dimmed">
            Аналитика Telegram-каналов с искусственным интеллектом.
            Знайте о своём канале больше, чем вы сами.
          </Text>
        </Stack>

        {groups}
      </SimpleGrid>

      <Group justify="space-between" mt={48} wrap="wrap" gap="md">
        <Text size="sm" c="dimmed">
          © 2026 tgpulse · Прототип
        </Text>
        <Badge variant="light" onClick={() => navigate('/nonexistent')} style={{ cursor: 'pointer' }}>
          Пример страницы 404 →
        </Badge>
      </Group>

    </Box>
  );
}
