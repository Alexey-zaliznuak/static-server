from tortoise import fields
from tortoise.models import Model
import uuid
from datetime import datetime


class File(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = fields.DatetimeField(auto_now_add=True, null=False)
    updated_at = fields.DatetimeField(auto_now=True, null=False)
    path = fields.CharField(max_length=300, null=False)

    def filename(self) -> str:
        return self.path.split("\\")[-1]

    @staticmethod
    def generate_path(id: uuid.UUID) -> str:
        """
        /<first 2 symbols of id>/<second 2 symbols of id>/<rest_of_id>.<extension>
        """
        id_str = str(id)
        return f"/{id_str[:2]}/{id_str[2:4]}/{id_str[4:]}"
