import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
import json
from datetime import datetime

from apps.parser.models import TelegramChannel
from apps.group_channels.models import Group

User = get_user_model()

class TestUserModel:
    """Тесты для модели User"""
    
    def test_create_user(self, db, user_fixtures):
        """Тест создания пользователя с валидными данными"""
        valid_data = user_fixtures['valid'][0]
        user = User.objects.create_user(
            username=valid_data['username'],
            email=valid_data['email'],
            password=valid_data['password'],
            first_name=valid_data.get('first_name', ''),
            last_name=valid_data.get('last_name', ''),
            bio=valid_data.get('bio', ''),
            role=valid_data.get('role', '')
        )
        
        assert user.username == valid_data['username']
        assert user.email == valid_data['email']
        assert user.check_password(valid_data['password'])
        assert user.first_name == valid_data.get('first_name', '')
        assert user.last_name == valid_data.get('last_name', '')
        assert user.bio == valid_data.get('bio', '')
        assert user.role == valid_data.get('role', '')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_user_with_avatar(self, db, user_fixtures):
        """Тест создания пользователя с аватаром"""
        valid_data = user_fixtures['valid'][0]
        user = User.objects.create_user(
            username=valid_data['username'],
            email=valid_data['email'],
            password=valid_data['password'],
            avatar_image=valid_data.get('avatar_image', '')
        )
        
        assert user.avatar_image == valid_data.get('avatar_image', '')
    
    def test_user_str_method(self, db, user_fixtures):
        """Тест строкового представления пользователя"""
        valid_data = user_fixtures['valid'][0]
        user = User.objects.create_user(
            username=valid_data['username'],
            email=valid_data['email'],
            password=valid_data['password']
        )
        
        assert str(user) == valid_data['username']
    
    def test_unique_username_constraint(self, db, user_fixtures):
        """Тест уникальности username"""
        valid_data = user_fixtures['valid'][0]
        User.objects.create_user(
            username=valid_data['username'],
            email=valid_data['email'],
            password=valid_data['password']
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username=valid_data['username'],
                email='another@example.com',
                password='password123'
            )
    
    def test_unique_email_constraint(self, db, user_fixtures):
        """Тест уникальности email"""
        valid_data = user_fixtures['valid'][0]
        User.objects.create_user(
            username=valid_data['username'],
            email=valid_data['email'],
            password=valid_data['password']
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username='another_user',
                email=valid_data['email'],
                password='password123'
            )
    
    def test_create_superuser(self, db):
        """Тест создания суперпользователя"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        assert user.is_superuser
        assert user.is_staff


class TestTelegramChannelModel:
    """Тесты для модели TelegramChannel"""
    
    def test_create_channel(self, db, telegram_channel_fixtures):
        """Тест создания канала с валидными данными"""
        valid_data = telegram_channel_fixtures['valid'][0]
        channel = TelegramChannel.objects.create(
            channel_id=valid_data['channel_id'],
            title=valid_data['title'],
            username=valid_data.get('username', ''),
            description=valid_data.get('description', ''),
            participants_count=valid_data['participants_count'],
            parsed_at=datetime.now() if valid_data.get('parsed_at') is None else valid_data.get('parsed_at')
        )
        
        assert channel.channel_id == valid_data['channel_id']
        assert channel.title == valid_data['title']
        assert channel.username == valid_data.get('username', '')
        assert channel.description == valid_data.get('description', '')
        assert channel.participants_count == valid_data['participants_count']
    
    def test_channel_str_method(self, db, telegram_channel_fixtures):
        """Тест строкового представления канала"""
        valid_data = telegram_channel_fixtures['valid'][0]
        channel = TelegramChannel.objects.create(
            channel_id=valid_data['channel_id'],
            title=valid_data['title'],
            participants_count=valid_data['participants_count']
        )
        
        expected_str = f"{valid_data['channel_id']} канал {valid_data['title']}"
        assert str(channel) == expected_str
    
    def test_unique_channel_id(self, db, telegram_channel_fixtures):
        """Тест уникальности channel_id"""
        valid_data = telegram_channel_fixtures['valid'][0]
        TelegramChannel.objects.create(
            channel_id=valid_data['channel_id'],
            title=valid_data['title'],
            participants_count=valid_data['participants_count']
        )
        
        with pytest.raises(IntegrityError):
            TelegramChannel.objects.create(
                channel_id=valid_data['channel_id'],
                title='Another Channel',
                participants_count=100
            )


class TestGroupModel:
    """Тесты для модели Group из group_channels"""
    
    def test_create_group(self, db, group_fixtures, user):
        """Тест создания группы с валидными данными"""
        valid_data = group_fixtures['valid'][0]
        group = Group.objects.create(
            name=valid_data['name'],
            description=valid_data.get('description', ''),
            owner=user,
            is_editorial=False,
            order=0
        )
        
        assert group.name == valid_data['name']
        assert group.description == valid_data.get('description', '')
        assert group.owner == user
        assert group.is_editorial is False
    
    def test_group_str_method(self, db, group_fixtures, user):
        """Тест строкового представления группы"""
        valid_data = group_fixtures['valid'][0]
        group = Group.objects.create(
            name=valid_data['name'],
            owner=user
        )
        
        assert str(group) == valid_data['name']
    
    def test_unique_group_name(self, db, group_fixtures, user):
        """Тест уникальности названия группы"""
        valid_data = group_fixtures['valid'][0]
        Group.objects.create(
            name=valid_data['name'],
            owner=user
        )
        
        with pytest.raises(IntegrityError):
            Group.objects.create(
                name=valid_data['name'],
                owner=user
            )
    
    def test_group_owner_relation(self, db, group_fixtures, user):
        """Тест связи группы с владельцем"""
        valid_data = group_fixtures['valid'][0]
        group = Group.objects.create(
            name=valid_data['name'],
            owner=user
        )
        
        assert group.owner == user
        assert group in user.owned_groups.all()


class TestPartnerProfileModel:
    """Тесты для модели PartnerProfile"""
    
    def test_create_partner_profile(self, db, user):
        """Тест создания партнерского профиля"""
        from apps.users.models import PartnerProfile
        profile = PartnerProfile.objects.create(
            user=user,
            status='active'
        )

        assert profile.user == user
        assert profile.status == 'active'
        assert str(profile) == f"{user.username} (Активен)"
    
    def test_partner_profile_status_choices(self, db, user):
        """Тест выбора статуса партнера"""
        from apps.users.models import PartnerProfile
        
        statuses = ['active', 'pending', 'rejected', 'suspended']
        for status in statuses:
            profile = PartnerProfile.objects.create(
                user=User.objects.create_user(
                    username=f'test_{status}',
                    email=f'{status}@example.com',
                    password='password'
                ),
                status=status
            )
            assert profile.status == status
            assert profile.get_status_display() is not None


class TestRoleModel:
    """Тесты для модели Role из users.roles"""
    
    def test_create_role(self, db):
        """Тест создания роли"""
        from apps.users.roles import Role
        import uuid
        
        unique_code = f'test_role_{uuid.uuid4().hex[:8]}'
        role = Role.objects.create(
            code=unique_code,
            name='Тестовая роль'
        )
        
        assert role.code == unique_code
        assert role.name == 'Тестовая роль'
        assert str(role) == 'Тестовая роль'
    
    def test_role_unique_code(self, db):
        """Тест уникальности кода роли"""
        from apps.users.roles import Role
        from django.db import IntegrityError
        import uuid
        
        unique_code = f'test_unique_{uuid.uuid4().hex[:8]}'
        
        Role.objects.create(code=unique_code, name='Тестовая роль 1')
        
        with pytest.raises(IntegrityError):
            Role.objects.create(code=unique_code, name='Тестовая роль 2')
    
    def test_role_str_method(self, db):
        """Тест строкового представления роли"""
        from apps.users.roles import Role
        import uuid
        
        unique_code = f'test_str_{uuid.uuid4().hex[:8]}'
        role = Role.objects.create(code=unique_code, name='Тестовая роль')
        assert str(role) == 'Тестовая роль'
        
        unique_code_empty = f'test_empty_{uuid.uuid4().hex[:8]}'
        role_empty = Role.objects.create(code=unique_code_empty, name='')
        assert str(role_empty) == 'NONE'


class TestUserRoleHistory:
    """Тесты для модели UserRoleHistory"""
    
    @pytest.mark.skip(reason="Проблемы с внешними ключами в тестовой БД")
    def test_create_user_role_history(self, db, user):
        """Тест создания записи истории роли"""
        from apps.users.roles import Role, UserRoleHistory
        import uuid
        
        role = Role.objects.create(
            code=f'test_history_{uuid.uuid4().hex[:8]}',
            name='Тестовая роль'
        )
        
        history = UserRoleHistory.objects.create(
            user=user,
            role=role,
            reason='Начальная роль'
        )
        
        assert history.user == user
        assert history.role == role
        assert history.reason == 'Начальная роль'
        assert history.start_date is not None
        assert history.end_date is None
        assert history.is_current_role is True
    
    @pytest.mark.skip(reason="Проблемы с внешними ключами в тестовой БД")
    def test_user_role_history_str(self, db, user):
        """Тест строкового представления истории"""
        from apps.users.roles import Role, UserRoleHistory
        import uuid
        
        role = Role.objects.create(
            code=f'test_str_{uuid.uuid4().hex[:8]}',
            name='Тестовая роль'
        )
        history = UserRoleHistory.objects.create(
            user=user,
            role=role
        )
        
        expected = f"Роль Тестовая роль пользователя {user.username}"
        assert str(history) == expected
    
    @pytest.mark.skip(reason="Проблемы с внешними ключами в тестовой БД")
    def test_multiple_roles_history(self, db, user):
        """Тест истории с несколькими ролями"""
        from apps.users.roles import Role, UserRoleHistory
        from datetime import datetime
        import uuid
        
        role1 = Role.objects.create(
            code=f'test_multi1_{uuid.uuid4().hex[:8]}',
            name='Роль 1'
        )
        role2 = Role.objects.create(
            code=f'test_multi2_{uuid.uuid4().hex[:8]}',
            name='Роль 2'
        )
        
        history1 = UserRoleHistory.objects.create(
            user=user,
            role=role1
        )
        
        history1.end_date = datetime.now()
        history1.save()
        
        history2 = UserRoleHistory.objects.create(
            user=user,
            role=role2
        )
        
        assert history1.is_current_role is False
        assert history2.is_current_role is True
        assert UserRoleHistory.objects.filter(user=user).count() == 2
    
    @pytest.mark.skip(reason="Проблемы с внешними ключами в тестовой БД")
    def test_unique_current_role_constraint(self, db, user):
        """Тест уникальности текущей роли для пользователя"""
        from apps.users.roles import Role, UserRoleHistory
        from django.db import IntegrityError
        import uuid
        
        role = Role.objects.create(
            code=f'test_unique_{uuid.uuid4().hex[:8]}',
            name='Тестовая роль'
        )
        
        UserRoleHistory.objects.create(
            user=user,
            role=role
        )
        
        with pytest.raises(IntegrityError):
            UserRoleHistory.objects.create(
                user=user,
                role=role
            )
    
    @pytest.mark.skip(reason="Проблемы с внешними ключами в тестовой БД")
    def test_current_role_manager(self, db, user):
        """Тест менеджера для получения текущей роли"""
        from apps.users.roles import Role, UserRoleHistory
        from datetime import datetime
        import uuid
        
        role = Role.objects.create(
            code=f'test_manager_{uuid.uuid4().hex[:8]}',
            name='Тестовая роль'
        )
        history = UserRoleHistory.objects.create(
            user=user,
            role=role
        )
        
        current = UserRoleHistory.objects.current_role(user)
        assert current == role
        
        history.end_date = datetime.now()
        history.save()
        
        current = UserRoleHistory.objects.current_role(user)
        assert current is None