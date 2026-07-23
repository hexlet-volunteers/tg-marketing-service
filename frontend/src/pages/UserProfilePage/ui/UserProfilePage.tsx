import { BrandAvatar } from '@/components/ui/BrandAvatar';
import { SectionCard } from '@/components/ui/SectionCard';
import {
  Badge,
  Box,
  Button,
  Container,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Switch,
  Text,
  Title,
} from '@mantine/core';
import { IconEdit, IconLogout, IconPlus } from '@tabler/icons-react';
import React from 'react';
import { useNavigate } from 'react-router-dom';

const notifications = [
  { label: 'Email-уведомления', defaultChecked: true },
  { label: 'AI-рекомендации', defaultChecked: true },
  { label: 'Обновления тарифов', defaultChecked: false },
];

const UserProfilePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container>
      <Box mb="md">
        <Title order={2}>Личный кабинет</Title>
        <Text c="dimmed">Управление аккаунтом и подпиской</Text>
      </Box>
      <SimpleGrid cols={{ base: 1, md: 2 }}>
        <Paper withBorder p="lg" radius="md">
          <Title order={3} mb="md">Профиль</Title>
          <Group gap="md" mb="lg">
            <BrandAvatar name="Алексей Иванов" size={58} />
            <div>
              <Title order={4}>Алексей Иванов</Title>
              <Text size="sm" c="dimmed">alexey@example.com</Text>
            </div>
          </Group>
          <Group gap="sm">
            <Button size="sm" leftSection={<IconEdit size={14} />}>
              Редактировать
            </Button>
            <Button
              size="sm"
              color="tgred"
              leftSection={<IconLogout size={14} />}
              onClick={() => navigate('/auth')}
            >
              Выйти
            </Button>
          </Group>
        </Paper>

        <SectionCard
          title="Подписка"
          action={<Badge size="lg" color="gray">Free</Badge>}
        >
          <Paper p="md" radius="md" bg="tgblue.0" mb="md">
            <Text size="sm" fw={600} mb="xs">Получите больше возможностей</Text>
            <Text size="xs" c="dimmed" mb="sm">AI-инсайты, сравнение каналов, экспорт данных</Text>
            <Button size="sm" variant="filled" color="tgblue" onClick={() => navigate('/')}>
              Перейти на Pro
            </Button>
          </Paper>
          <Button size="sm" variant="subtle" color="tgblue">
            История платежей
          </Button>
        </SectionCard>
      </SimpleGrid>

      <SimpleGrid cols={{ base: 1, md: 2 }} mt="lg">
        <SectionCard
          title="Мои каналы и группы"
          action={
            <Button size="xs" color="tgblue" leftSection={<IconPlus size={12} />}>
              Добавить
            </Button>
          }
        >
          <Text c="dimmed" size="sm">У вас пока нет добавленных каналов</Text>
        </SectionCard>

        <SectionCard title="Уведомления">
          <Stack>
            {notifications.map((n, i) => (
              <Group key={i} justify="space-between">
                <Text size="sm">{n.label}</Text>
                <Switch size="sm" defaultChecked={n.defaultChecked} />
              </Group>
            ))}
          </Stack>
        </SectionCard>
      </SimpleGrid>
    </Container>
  );
};

export default UserProfilePage;
