from django.db.models import QuerySet


class SubscriptionQuerySet(QuerySet):
    def exclude_cancelled(self):
        from subscriptions.models.meta import SubscriptionStatus
        statuses = [
            SubscriptionStatus.INACTIVE,
            SubscriptionStatus.CANCELLED,
        ]
        qs = self.exclude(status__in=statuses)
        return qs

    def filter_by_user_id(self, user_id: str):
        return self.filter(client__user_id=user_id)

    def filter_by_status(self, status):
        return self.filter(status=status)