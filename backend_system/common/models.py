import datetime
import pytz
import uuid

from django.db import models
from django.db.models.signals import post_delete, pre_delete


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(f'{self.__class__.__name__} ID: {self.id}')


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeleteQuerySet, self).update(deleted_at=datetime.datetime.now(pytz.UTC))

    def hard_delete(self):
        return super(SoftDeleteQuerySet, self).delete()

    def existing(self):
        return self.filter(deleted_at=None)

    def deleted(self):
        return self.exclude(deleted_at=None)


class SoftDeleteManager(models.Manager):
    queryset_class = SoftDeleteQuerySet

    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop('with_deleted', False)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.with_deleted:
            return self.queryset_class(self.model)
        return self.queryset_class(self.model).filter(deleted_at=None)


class SoftDeleteModel(BaseModel):
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True)

    objects = SoftDeleteManager()
    objects_with_deleted = SoftDeleteManager(with_deleted=True)

    class Meta:
        abstract = True

    def delete(self):
        pre_delete.send(sender=self.__class__, instance=self, using=self._state.db)
        self.deleted_at = datetime.datetime.now(pytz.UTC)
        self.save()
        post_delete.send(sender=self.__class__, instance=self, using=self._state.db)

    def hard_delete(self):
        super(SoftDeleteModel, self).delete()
