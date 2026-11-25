import { useState, useRef, useEffect } from "react";
import type { Insight, EmptyStateVariant  } from "@/types/aiCabinet";

/**
 * Кастомный хук для управления бизнес-логикой блока инсайтов.
 * 
 * Реализует:
 * - Управление состоянием списка инсайтов (локальное удаление).
 * - Очередь анимации удаления (хранение ID элементов, которые находятся в процессе скрытия).
 * - Расчет вариантов пустого состояния (все прочитано vs данных нет).
 * 
 * @param initialInsights - Исходный массив инсайтов, полученный извне.
 * @returns Объект с состоянием и методами управления:
 * - `list`: текущий отображаемый список инсайтов.
 * - `deletingIds`: набор ID элементов, проходящих анимацию удаления.
 * - `handleDismiss`: функция-обработчик для запуска процесса удаления.
 * - `isEmpty`: флаг отсутствия элементов в текущем списке.
 * - `emptyStateVariant`: тип заглушки для отображения в `InsightsEmptyState`.
 */


export const useWeeklyInsights = (initialInsights: Insight[] = []) => {
  const [list, setList] = useState(initialInsights);
  const [deletingIds, setDeletingIds] = useState<Set<string | number>>(new Set());

  const timeoutsRef = useRef<Map<string | number, number>>(new Map());

  const handleDismiss = (itemId: string | number) => {
    setDeletingIds((prev) => new Set(prev).add(itemId));

    if (timeoutsRef.current.has(itemId)) {
      clearTimeout(timeoutsRef.current.get(itemId));
    }

    const timerId = setTimeout(() => {
      setList((prev) => prev.filter((_, index) => index !== itemId));
      
      setDeletingIds((prev) => {
        const next = new Set(prev);
        next.delete(itemId);
        return next;
      });

      timeoutsRef.current.delete(itemId);
    }, 250);

    timeoutsRef.current.set(itemId, timerId);
  };

 useEffect(() => {
  const timeouts = timeoutsRef.current; 

  return () => {
    timeouts.forEach((timerId) => clearTimeout(timerId));
    timeouts.clear();
  };
}, []);

  const isEmpty = list.length === 0;
  const emptyStateVariant: EmptyStateVariant =
    initialInsights.length > 0 ? "all-read" : "no-insights";

  return {
    list,
    deletingIds,
    handleDismiss,
    isEmpty,
    emptyStateVariant,
  };
};