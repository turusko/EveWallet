from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base, UUIDTimestampMixin


class User(UUIDTimestampMixin, Base):
    __tablename__ = "users"

    characters: Mapped[list["EveCharacter"]] = relationship(back_populates="user")
    buckets: Mapped[list["ProjectBucket"]] = relationship(back_populates="user")
