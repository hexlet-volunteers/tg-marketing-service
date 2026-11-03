const formatter = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

export default function formatArticleDate(
  publishedAt: string | null,
): string {
  if (!publishedAt) {
    return "";
  }
  return formatter.format(new Date(publishedAt));
}
