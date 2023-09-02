from app.dao.base import BaseDAO
from app.users.models import Users


class UserDAO(BaseDAO):
    model = Users