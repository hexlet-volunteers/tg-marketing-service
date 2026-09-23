import type { Post, PostReaction, PostAnalysis } from "@/types/post";

const mockPosts: Post[] = [
  { title: 'Обзор нового iPhone 16 Pro', views: 52100, reactions: 890, forwards: 234, er: 31.2 },
  { title: 'Сравнение Android vs iOS в 2026', views: 41300, reactions: 756, forwards: 189, er: 28.4 },
  { title: 'Топ-10 приложений для продуктивности', views: 38000, reactions: 567, forwards: 123, er: 22.1 },
  { title: 'Как заработать на Telegram-канале', views: 22400, reactions: 198, forwards: 45, er: 14.8 },
];

const mockReactions: PostReaction[] = [
  { emoji: '🔥', label: 'Огонь', percent: 42, count: 374 },
  { emoji: '❤️', label: 'Сердце', percent: 28, count: 250 },
  { emoji: '👍', label: 'Лайк', percent: 20, count: 178 },
  { emoji: '🤯', label: 'Восторг', percent: 10, count: 89 },
];

const MOCK_ANALYSIS_DATA: PostAnalysis = {
 status: "processing",
 model_version: "GPT-4o",
 why_worked: [
  "Конкретный список + эмоция в заголовке и понятная польза",
  "Реакции на 34% выше среднего по каналу",
 ],
 how_to_improve: [
  "Добавить больше данных и графиков",
  "Сократить воду в начале",
  "Добавить CTA в конце",
 ],
 similar_posts: [
  {
   id: 1,
   text: "7 ошибок в продуктовой аналитике",
   permalink: "#",
   telegram_message_id: 101,
   published_at: "",
   views: 0,
   forwards: 0,
   comments_count: 0,
  },
  {
   id: 2,
   text: "Метрики активации по шагам воронки",
   permalink: "#",
   telegram_message_id: 102,
   published_at: "",
   views: 0,
   forwards: 0,
   comments_count: 0,
  },
 ],
};
export { mockPosts, mockReactions, MOCK_ANALYSIS_DATA }