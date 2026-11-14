import { NavLink, ScrollArea, Stack, ThemeIcon } from '@mantine/core';
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
import UpgradeBanner from '../ui/UpgradeBanner';

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

/**
 * Навигационная панель сайта.
 * 
 * Отображает навигационное меню с ссылками на страницы сайта,
 * а также баннер обновления тарифа.
 * 
 * Баннер вынесен в отдельный компонент.
 * Позже планируется добавить возможность скрывать баннер для пользователей с тарифом Pro и Agency.
 */

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

      <UpgradeBanner />


    </Stack>

  );
}
