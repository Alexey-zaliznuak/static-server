import uuid

from tortoise import fields
from tortoise.models import Model


class File(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    slug = fields.CharField(max_length=50)
    description = fields.TextField(null=True)

    file_type = fields.CharField(max_length=20, null=True)
    size = fields.IntField(null=True)  # Size in bytes
    path = fields.CharField(max_length=300, null=False)

    @property
    def filename(self) -> str:
        return self.path.split("\\")[-1]

    @staticmethod
    def make_path(id: uuid.UUID) -> str:
        """
        <first 2 symbols of id>/<second 2 symbols of id>/<rest_of_id>.<extension>
        """
        id_str = str(id)
        return f"/{id_str[:2]}/{id_str[2:4]}/{id_str[4:]}"
