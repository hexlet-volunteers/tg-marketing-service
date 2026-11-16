/**
 * Форматирует изменение показателя (дельту) в числовом и процентном виде.
 * 
 * Добавляет знак "+" для положительных чисел, форматирует числа согласно русской локали
 * и удаляет лишний ноль после запятой в процентах (например, "5.0%" превратится в "5%").
 *
 * @param delta - Абсолютное изменение показателя (число).
 * @param percentDelta - Относительное изменение показателя в процентах.
 * @returns Строка в формате "+1 250 · 15.5%" или "0", если данные отсутствуют.
 *
 * @example
 * deltaFormatter(1250, 15); // "+1 250 · 15%"

 * deltaFormatter(-500, -2.5); // "-500 · -2.5%"

 * deltaFormatter(100, undefined); // "+100"

 * deltaFormatter(undefined, 5); // "+5%"
 */

const deltaFormatter = (delta: number | undefined, percentDelta: number | undefined): string => {

  // Регулярное выражение для удаления .0 в конце строки процентов

  const formatPercent = (val: number) => {
    const formatted = val.toFixed(1).replace(/\.0$/, "");
    return val > 0 ? `+${formatted}%` : `${formatted}%`;
  };

  const formatValue = (val: number) => {
    const formatted = val.toLocaleString("ru-RU");
    return val > 0 ? `+${formatted}` : formatted;
  };

  // 1. Если переданы оба значения
  if (delta !== undefined && percentDelta !== undefined) {
    return `${formatValue(delta)} · ${formatPercent(percentDelta)}`;
  }

  // 2. Если передано только абсолютное изменение
  if (delta !== undefined) {
    return formatValue(delta);
  }

  // 3. Если передано только процентное изменение
  if (percentDelta !== undefined) {
    return formatPercent(percentDelta);
  }

  // 4. Фоллбэк
  return "0";
};

export default deltaFormatter;