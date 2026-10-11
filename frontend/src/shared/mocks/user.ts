import type { User, UserNotification } from "@/types/user";

export const mockUser: User = {
  first_name: 'Мария',
  last_name: 'Логинова',
  email: 'maria@example.com'
}

export const mockNotifications: UserNotification[] = [
  { label: 'Email-уведомления', defaultChecked: true },
  { label: 'AI-рекомендации', defaultChecked: true },
  { label: 'Обновления тарифов', defaultChecked: false },
];
