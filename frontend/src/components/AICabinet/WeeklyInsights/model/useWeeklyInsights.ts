import { useState } from "react";
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
    const [deletingIds, setDeletingIds] = useState<Set<string | number>>(
        new Set(),
    );

    const handleDismiss = (itemId: string | number) => {
        setDeletingIds((prev) => new Set(prev).add(itemId));

        setTimeout(() => {
            setList((prev) => prev.filter((_, index) => index !== itemId));
            setDeletingIds((prev) => {
                const next = new Set(prev);
                next.delete(itemId);
                return next;
            });
        }, 250);
    };

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