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


type SimilarPost = {
 id: number;
 telegram_message_id: number;
 text: string;
 published_at: string;
 views: number;
 forwards: number;
 comments_count: number;
 permalink: string;
};

type PostAnalysis = {
 status: "processing" | "completed";
 why_worked: string[];
 how_to_improve: string[];
 similar_posts: SimilarPost[];
 model_version: string | null;
};

interface PostPageProps {
 analysis?: PostAnalysis | null;
 reactions?: PostReaction[];
}



export type { Post, PostProps, PostAnalysis, PostReaction, PostPageProps}