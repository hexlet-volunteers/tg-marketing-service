import { Alert } from "@mantine/core";
import { IconInfoCircle, IconSparkles } from "@tabler/icons-react";

import type { InsightsEmptyStateProps } from "@/types/aiCabinet";

/**
 * Компонент пустого состояния для блока «Инсайты недели».
 *
 * Отображает одно из двух сообщений:
 * - `all-read` — все доступные инсайты прочитаны.
 * - `no-insights` — инсайты пока отсутствуют.
 */
export const InsightsEmptyState = ({ variant }: InsightsEmptyStateProps) => {
 if (variant === "all-read") {
  return (
   <Alert
    variant="light"
    color="gray"
    title="Отличная работа!"
    icon={<IconSparkles size={16} />}
   >
    Вы прочитали все инсайты на этой неделе.
   </Alert>
  );
 }

 return (
  <Alert
   variant="light"
   color="blue"
   title="Пока нет инсайтов"
   icon={<IconInfoCircle size={16} />}
  >
   AI анализирует данные вашего канала. Первые рекомендации появятся здесь после
   публикации новых постов.
  </Alert>
 );
};

