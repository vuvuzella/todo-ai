from sqlmodel import select

from domain.aggregates.users import Users
from infrastructure.repositories.base import Repository


class UserRepository(Repository):
    def get_all_users(self):
        users = self.session.exec(select(Users)).fetchall()
        return list(users)

    def get_user_by_id(self, user_id: int, raise_not_found: bool = True):
        user = self.session.exec(select(Users).where(Users.id == user_id)).first()

        if user is None and raise_not_found:
            raise Exception(f"User id {user_id} not found")

        return user

    def get_user_by_auth0_id(self, auth0_id: str):
        stmt = select(Users).filter_by(auth0_id=auth0_id)
        user = self.session.exec(stmt).one()
        return user

    def create_user(self, new_user: Users) -> Users:
        result = self.session.scalar(select(Users.id).where(Users.id == new_user.id))
        if result is not None:
            raise Exception(f"Task id {new_user.id} already exists")

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user
