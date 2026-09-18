import type { Collection } from "@/types/collection";

const collections: Collection[] = [
  {
    id: 1,
    title: "Топ IT-каналов",
    description: "Технологии, разработка и цифровые продукты",
    author: "Редакция tgpulse",
    channels: 3,
    editorial: true,
  },
  {
    id: 2,
    title: "Маркетинг и SMM",
    description: "Продвижение, реклама и контент",
    author: "Редакция tgpulse",
    channels: 1,
    editorial: true,
  },
  {
    id: 3,
    title: "Крипта без шума",
    description: "Аналитика рынка без хайпа",
    author: "@crypta_daily",
    channels: 1,
  },
  {
    id: 4,
    title: "Стартапы и венчур",
    description: "Истории, разборы и деньги",
    author: "Редакция tgpulse",
    channels: 2,
    editorial: true,
  },
  {
    id: 5,
    title: "Дизайн и продукт",
    description: "UX, UI и продуктовое мышление",
    author: "@design_kitchen",
    channels: 2,
  },
  {
    id: 6,
    title: "Финансы и инвестиции",
    description: "Личные финансы и рынки",
    author: "Редакция tgpulse",
    channels: 2,
    editorial: true,
  },
];

export default collections;