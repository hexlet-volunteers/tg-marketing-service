import type { UserRequest, UserRequestWithColors } from "@/types/user";
import type { Article, ArticleWithColor } from '@/types/article';
import type { CollectionColor, Collection, CollectionWithColor } from "@/types/collection";
import type { MainCharactersOfChannel, MainCharactersOfChannelAndColor } from "@/types/channel";
import userRequests from '@/shared/mocks/userRequests';
import articles from '@/shared/mocks/articles';
import collections from "@/shared/mocks/collections";
import chCollection from "@/shared/mocks/chCollection";

const channelsColors = [ "indigo", "orange", "teal", "pink" ]


const addColorsToUsersRequests = (channelsColors: string[], userRequests: UserRequest[]): 
  UserRequestWithColors[] => {
    return userRequests.map((item, index) => {
      const assignedColor = channelsColors[index % channelsColors.length];
      return { ...item, color: assignedColor }
    })
}

export const mockUserRequests = addColorsToUsersRequests(channelsColors, userRequests)

const articleColors: string[] = [
  "var(--mantine-color-tgblue-5)",
  "var(--mantine-color-tggreen-5)",
  "var(--mantine-color-tgorange-5)",
]

const addColorsToArticles = (articleColors: string[], articles: Article[]): ArticleWithColor[] => {
  return articles.map((article, index) => {
    const assignedColor = articleColors[index % articleColors.length];
    return { ...article, color: assignedColor }
  })
}

export const mockArticles = addColorsToArticles(articleColors, articles)

const collectionPageColors = [
  "var(--mantine-color-tgblue-5)",
  "var(--mantine-color-tgpurple-5)",
  "var(--mantine-color-tgblue-4)",
]

const addColorsToCollectionPage = (сolors: string[], data: MainCharactersOfChannel[]): 
  MainCharactersOfChannelAndColor[] => {
    return data.map((item, index) => {
    const assignedColor = сolors[index % сolors.length];
    return { ...item, color: assignedColor }
  })
}

export const mockCollection = addColorsToCollectionPage(collectionPageColors, chCollection)

const collectionsColorsAndGradients: CollectionColor[] = [
  { color: "var(--mantine-color-tgblue-5)", 
    gradient: "linear-gradient(90deg,var(--mantine-color-tgblue-5),var(--mantine-color-tgpurple-6))" },
  { color: "var(--mantine-color-tgpurple-4)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgpurple-3),var(--mantine-color-tgpurple-6))" },
  { color: "var(--mantine-color-tgorange-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgorange-3),var(--mantine-color-tgorange-5))" },
  { color: "var(--mantine-color-tggreen-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tggreen-3),var(--mantine-color-tggreen-5))" },
  { color: "var(--mantine-color-tggreen-6)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tggreen-4),var(--mantine-color-tggreen-6))" },
  { color: "var(--mantine-color-tgblue-4)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgblue-3),var(--mantine-color-tgblue-5))" },
]

const addColorstoCollections = (
  collections: Collection[], 
  collectionsColorsAndGradients: CollectionColor[]): 
  CollectionWithColor[] => {
    return collections.map((collection, index) => {
      const assignedColorAndGradient = collectionsColorsAndGradients[index % collectionsColorsAndGradients.length];
    return { ...collection, ...assignedColorAndGradient }
    })
}

export const mockCollections = addColorstoCollections(collections, collectionsColorsAndGradients)