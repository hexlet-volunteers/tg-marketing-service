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
import { router } from '@inertiajs/react';
import { useState } from 'react';
import type { UserProfilePageProps, UserNotificationSettings } from '@/types/user';

const EMPTY_NOTIFICATIONS: UserNotificationSettings = {
  weekly_reports: false,
  trend_notifications: false,
  limit_exceeded: false,
  new_features: false,
};

type SAVABLE_NOTIFICATION_KEY =
  | 'weekly_reports'
  | 'trend_notifications'
  | 'new_features';

const NOTIFICATION_ROWS: ReadonlyArray<{ key: SAVABLE_NOTIFICATION_KEY; label: string }> = [
  { key: 'weekly_reports', label: 'Еженедельные отчёты' },
  { key: 'trend_notifications', label: 'Уведомления о трендах' },
  { key: 'new_features', label: 'Новые функции' },
];

const Profile = ({ user, notifications }: UserProfilePageProps ) => {
  const serverSettings = notifications ?? EMPTY_NOTIFICATIONS;
  const [draft, setDraft] = useState<UserNotificationSettings | null>(null);
  const [pending, setPending] = useState(false);
  const settings = draft ?? serverSettings;

  const toggleNotification = (key: SAVABLE_NOTIFICATION_KEY, checked: boolean) => {
    const next = { ...settings, [key]: checked };
    setDraft(next);
    router.post(
      '/auth/profile/',
      {
        action: 'notifications',
        weekly_reports: String(next.weekly_reports),
        trend_notifications: String(next.trend_notifications),
        new_features: String(next.new_features),
      },
      {
        forceFormData: true,
        preserveScroll: true,
        onStart: () => setPending(true),
        onFinish: () => setPending(false),
        onError: () => setDraft(null),
      },
    );
  };

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
            <BrandAvatar name={`${user.first_name} ${user.last_name}`} size={58} />
            <div>
              <Title order={4}>{user.first_name} {user.last_name}</Title>
              <Text size="sm" c="dimmed">{user.email}</Text>
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
              onClick={() => router.visit('/auth/logout/')}
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
            <Button size="sm" variant="filled" color="tgblue" onClick={() => router.visit('/')}>
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
            {NOTIFICATION_ROWS.map(({ key, label }) => (
              <Group key={key} justify="space-between">
                <Text size="sm">{label}</Text>
                <Switch
                  size="sm"
                  checked={settings[key]}
                  disabled={pending}
                  onChange={(event) => toggleNotification(key, event.currentTarget.checked)}
                />
              </Group>
            ))}
            <Group justify="space-between">
              <Text size="sm">Превышение лимитов</Text>
              <Switch size="sm" checked={settings.limit_exceeded} disabled />
            </Group>
          </Stack>
        </SectionCard>
      </SimpleGrid>
    </Container>
  );
};

export default Profile;
