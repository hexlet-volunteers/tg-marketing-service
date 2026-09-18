import type { User, UserNotification } from "@/types/user";

export const mockUser: User = {
  name: 'Мария',
  lastName: 'Логинова',
  email: 'maria@example.com'
}

export const mockNotifications: UserNotification[] = [
  { label: 'Email-уведомления', defaultChecked: true },
  { label: 'AI-рекомендации', defaultChecked: true },
  { label: 'Обновления тарифов', defaultChecked: false },
];
