from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db import db

class Chat(db.Model):
	id: Mapped[int] = mapped_column(primary_key=True)
	message: Mapped[str] = mapped_column(Text)
	sender: Mapped[str]