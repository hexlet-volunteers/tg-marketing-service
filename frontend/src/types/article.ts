interface Article {
  id: string;
  category: string;
  title: string;
  date: string;
  time: string;
}

interface ArticleWithColor extends Article {
  color: string;
}

interface BlogPageProps {
  articles: ArticleWithColor[];
}

export type { Article, ArticleWithColor, BlogPageProps };