import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import WatchList, WatchListItem

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")

    def test_user_with_phone_number(self, user):
        assert user.phone_number == "010-1234-5678"
        assert user.receive_daily_report is True

    def test_user_string_representation(self, user):
        assert str(user) == "testuser"


@pytest.mark.django_db
class TestWatchListModel:
    def test_create_watchlist(self, user):
        watchlist = WatchList.objects.create(
            user=user,
            name="테스트 관심목록"
        )
        assert watchlist.user == user
        assert watchlist.name == "테스트 관심목록"
        assert watchlist.created_at is not None

    def test_watchlist_string_representation(self, watchlist):
        expected = f"{watchlist.user} - {watchlist.name}"
        assert str(watchlist) == expected

    def test_watchlist_user_relationship(self, user, watchlist):
        assert watchlist in user.watchlists.all()


@pytest.mark.django_db
class TestWatchListItemModel:
    def test_create_watchlist_item(self, watchlist, stock):
        item = WatchListItem.objects.create(
            watchlist=watchlist,
            stock=stock
        )
        assert item.watchlist == watchlist
        assert item.stock == stock

    def test_watchlist_item_unique_constraint(self, watchlist, stock):
        WatchListItem.objects.create(
            watchlist=watchlist,
            stock=stock
        )
        with pytest.raises(Exception):
            WatchListItem.objects.create(
                watchlist=watchlist,
                stock=stock
            )

    def test_watchlist_items_relationship(self, watchlist_item):
        assert watchlist_item in watchlist_item.watchlist.items.all()
