interface Collection {
  id: number;
  title: string;
  description: string;
  author: string;
  channels: number;
  editorial?: boolean;
}

interface CollectionColor {
  color: string;
  gradient: string;
}

interface CollectionWithColor extends Collection, CollectionColor {
  onClick?: () => void;
}

interface CollectionsPageProps {
  collections: CollectionWithColor[]
}


export type { Collection, CollectionColor, CollectionWithColor, CollectionsPageProps }