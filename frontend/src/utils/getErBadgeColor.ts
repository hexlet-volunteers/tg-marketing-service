/** Возможные названия цветовых токенов для ER */
export type ErColorToken = "tggreen" | "tgorange" | "tgred";
/**
 * Определяет цвет индикатора/бейджа на основе показателя вовлеченности (ER).
 *
 * @param er - Значение Engagement Rate в процентах (например, 31.2).
 * @returns Название цвета: "tggreen" (>= 25%), "tgorange" (>= 15%), "tgred" (< 15%).
 *
 * @example const color = getErBadgeColor(26); // "tggreen"
 **/
const getErBadgeColor = (er: number): ErColorToken => {
  switch (true) {
    case er >= 25:
      return "tggreen";
    case er >= 15:
      return "tgorange";
    default:
      return "tgred";
  }
};

export default getErBadgeColor;