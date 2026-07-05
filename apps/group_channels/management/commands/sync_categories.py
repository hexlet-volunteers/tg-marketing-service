# config/group_channels/management/commands/sync_categories.py
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from apps.group_channels.models import AutoGroupRule, Group
from apps.parser.models import TelegramChannel


def _flatten_choices(choices):
    """
    Поддержка как плоских choices [(val, label), ...],
    так и сгруппированных [('Группа', [(val, label), ...]), ...]
    """
    for item in choices:
        if isinstance(item[1], (list, tuple)):
            for sub in item[1]:
                yield sub[0]
        else:
            yield item[0]


class Command(BaseCommand):
    help = (
        "Создаёт автоподборки (Group + AutoGroupRule) для категорий.\n"
        "По умолчанию берёт полный список категорий из формы (choices),\n"
        "чтобы категории существовали даже без каналов.\n"
        "При желании можно взять только реально встречающиеся категории из БД (--source=db)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            choices=["choices", "db"],
            default="choices",
            help="Откуда брать категории: 'choices' (по умолчанию) или 'db'."
        )
        parser.add_argument("--owner-id", type=int, default=None)
        parser.add_argument("--owner-username", type=str, default=None)
        parser.add_argument("--owner-email", type=str, default=None)
        parser.add_argument("--start-order", type=int, default=10)
        parser.add_argument("--order-step", type=int, default=10)
        parser.add_argument("--dry-run", action="store_true")

    def _resolve_owner(self, owner_id, owner_username, owner_email):
        User = get_user_model()
        user = None
        if owner_id is not None:
            user = User.objects.filter(id=owner_id).first()
            if not user:
                raise CommandError(f"Пользователь с id={owner_id} не найден.")
        elif owner_username:
            user = User.objects.filter(username=owner_username).first()
            if not user:
                raise CommandError(f"Пользователь username='{owner_username}' не найден.")
        elif owner_email:
            user = User.objects.filter(email=owner_email).first()
            if not user:
                raise CommandError(f"Пользователь email='{owner_email}' не найден.")
        else:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()

        if not user:
            raise CommandError("Не удалось определить владельца (нет пользователей).")
        return user

    def _load_categories_from_choices(self):
        try:
            # берём choices прямо из формы парсера
            from config.parser.forms import ChannelParseForm
            field = ChannelParseForm.base_fields["category"]
            raw = list(_flatten_choices(field.choices))
        except Exception as e:
            raise CommandError(f"Не удалось получить категории из формы: {e}")

        out, seen = [], set()
        for val in raw:
            val = (val or "").strip()
            if val and val not in seen:
                seen.add(val)
                out.append(val)
        return out

    def _load_categories_from_db(self):
        raw = (
            TelegramChannel.objects
            .filter(~Q(category__isnull=True) & ~Q(category__exact=""))
            .values_list("category", flat=True)
            .distinct()
        )
        out, seen = [], set()
        for val in raw:
            val = (val or "").strip()
            if val and val not in seen:
                seen.add(val)
                out.append(val)
        return out

    def handle(self, *args, **options):
        owner = self._resolve_owner(
            options["owner_id"], options["owner_username"], options["owner_email"]
        )
        start_order = options["start_order"]
        order_step = options["order_step"]
        dry_run = options["dry_run"]

        # источник категорий
        if options["source"] == "choices":
            categories = self._load_categories_from_choices()
        else:
            categories = self._load_categories_from_db()

        if not categories:
            self.stdout.write(self.style.WARNING("Категории не найдены."))
            return

        created_groups = 0
        updated_rules = 0
        created_rules = 0
        order_val = start_order

        with transaction.atomic():
            for cat in categories:
                g, g_created = Group.objects.get_or_create(
                    name=cat,
                    defaults={
                        "owner": owner,
                        "is_editorial": False,
                        "order": order_val,
                    },
                )
                if g_created:
                    created_groups += 1
                    order_val += order_step

                rule, r_created = AutoGroupRule.objects.get_or_create(
                    group=g, defaults={"category": cat}
                )
                if r_created:
                    created_rules += 1
                elif rule.category != cat:
                    rule.category = cat
                    rule.save(update_fields=["category"])
                    updated_rules += 1

            if dry_run:
                raise transaction.TransactionManagementError("DRY RUN: изменения не сохранены.")

        self.stdout.write(self.style.SUCCESS("Синхронизация категорий завершена."))
        self.stdout.write(
            f"Всего категорий: {len(categories)} | создано групп: {created_groups} | "
            f"создано правил: {created_rules} | обновлено правил: {updated_rules}"
        )
        self.stdout.write(self.style.SUCCESS(f"Владелец групп: {owner}"))
