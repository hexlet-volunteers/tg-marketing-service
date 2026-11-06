from django import forms

from apps.blog.models import BlogArticle

EDITABLE_FIELDS = (
    "title",
    "slug",
    "excerpt",
    "cover_image",
    "body",
    "category",
    "tags",
    "is_featured",
    "is_published",
    "read_time",
)


class BlogArticleForm(forms.ModelForm):
    """Форма редактора статьи: валидирует поля, доступные в админке."""

    tags = forms.JSONField(required=False)

    class Meta:
        model = BlogArticle
        fields = EDITABLE_FIELDS

    def clean_tags(self) -> list[str]:
        tags = self.cleaned_data.get("tags") or []
        if not isinstance(tags, list) or not all(
            isinstance(tag, str) for tag in tags
        ):
            raise forms.ValidationError("Теги должны быть списком строк.")
        return [tag.strip() for tag in tags if tag.strip()]
