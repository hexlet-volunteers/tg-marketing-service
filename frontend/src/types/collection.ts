interface Collection {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  is_editorial: boolean;
  curator: string | null;
  channel_count: number;
  cover: string;
  gradient_key: string;
}

interface CollectionColor {
  color: string;
  gradient: string;
}

interface CollectionWithColor {
  id: number;
  title: string;
  description: string;
  author: string;
  channels: number;
  editorial?: boolean;
  color: string;
  gradient: string;
  onClick?: () => void;
}

interface CollectionSection {
  title: string;
  collections: Collection[];
  count: number;
}

interface CollectionsFilters {
  q: string | null;
  country: string | null;
  category: string | null;
  country_options: string[];
  category_options: string[];
}

interface CollectionsPageProps {
  featured: Collection[];
  collections: Collection[];
  sections: CollectionSection[];
  filters: CollectionsFilters;
}


export type { Collection, CollectionColor, CollectionWithColor, CollectionSection, CollectionsFilters, CollectionsPageProps }
