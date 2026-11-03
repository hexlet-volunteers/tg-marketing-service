import { Button, NavLink, Paper, Progress, ScrollArea, Stack, Text, ThemeIcon } from '@mantine/core';
import {
  IconArrowsExchange,
  IconBooks,
  IconChartBar,
  IconHome, IconLayoutGrid,
  IconNews,
  IconSettings,
  IconSparkles,
  IconUser,
} from '@tabler/icons-react';
import { router, usePage } from '@inertiajs/react';

const menu = [
  { label: 'Главная', path: '/', icon: IconHome },
  { label: 'Каталог каналов', path: '/channels/', icon: IconLayoutGrid },
  { label: 'Подборки', path: '/collections/', icon: IconBooks },
  { label: 'Дашборд канала', path: '/dashboard/', icon: IconChartBar },
  { label: 'Сравнение', path: '/compare/', icon: IconArrowsExchange },
  { label: 'AI-кабинет', path: '/ai-cabinet/', icon: IconSparkles },
  { label: 'Блог', path: '/blog/', icon: IconNews },
  { label: 'Личный кабинет', path: '/auth/profile/', icon: IconUser },
  { label: 'Админка', path: '/admin/moderation/', icon: IconSettings },
];

interface NavBarProps {
  onClose?: () => void;
}

export function NavBar({ onClose }: NavBarProps) {
  const { url } = usePage();
  const pathname = url.split('?')[0];

  return (

    <Stack h="100%" justify="space-between">
      <ScrollArea>

        <Stack gap={4}>
          {menu.map((item) => {
            const active = pathname === item.path;
            return (
              <NavLink
                key={item.label}
                label={item.label}
                leftSection={
                  <ThemeIcon
                    variant={active ? 'filled' : 'light'}
                    radius="xl"
                    size="sm"
                  >
                    <item.icon size={16} />
                  </ThemeIcon>
                }
                active={active}
                onClick={() => {
                  router.visit(item.path);
                  onClose?.();
                }}
              />
            );
          })}
        </Stack>
      </ScrollArea>

      <Paper withBorder radius="lg">
        <Stack gap="xs" p="sm">
          <Text fw={700}>Тариф Free</Text>
          <Text size="sm" c="dimmed">
            3 из 15 AI-разборов в этом месяце
          </Text>
          <Progress value={20} radius="xl" />
          <Button fullWidth radius="md">
            Улучшить тариф
          </Button>
        </Stack>
      </Paper>


    </Stack>

  );
}
