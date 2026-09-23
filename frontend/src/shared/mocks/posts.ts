import type { Post, PostReaction } from "@/types/post";

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

export { mockPosts, mockReactions }