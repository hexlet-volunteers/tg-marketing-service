interface Post {
  title: string;
  views: number;
  reactions: number;
  forwards: number;
  er: number;
}

interface PostProps {
  posts: Post[]
}

interface PostReaction {
  emoji: '🔥' | '❤️' | '👍' | '🤯';
  label: 'Огонь' | 'Сердце' | 'Лайк' | 'Восторг';
  percent: number;
  count: number;
}

interface PostReactionsProps {
  reactions: PostReaction[]
}

export type { Post, PostProps, PostReaction, PostReactionsProps}