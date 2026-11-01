export interface ArticleCard {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  cover_image: string;
  category: string;
  tags: string[];
  read_time: number;
  published_at: string | null;
  views_count: number;
  author_name: string | null;
}

export interface CallToAction {
  label: string;
  url: string;
}

export interface ArticleDetail extends ArticleCard {
  body: string;
  cta: CallToAction;
  related: ArticleCard[];
}

export interface BlogPageProps {
  featured: ArticleCard | null;
  articles: ArticleCard[];
}

export type BlogPostProps = ArticleDetail;
