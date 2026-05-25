import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, select

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kotrac_agent.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(30), index=True)
    user_message: Mapped[str] = mapped_column(Text)
    assistant_message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Memory:
    async def init_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_history(self, phone: str, limit: int = 10) -> list[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Message)
                .where(Message.phone == phone)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            messages = result.scalars().all()
            return [
                {"user": m.user_message, "assistant": m.assistant_message}
                for m in reversed(messages)
            ]

    async def save_message(self, phone: str, user_msg: str, assistant_msg: str):
        async with AsyncSessionLocal() as session:
            msg = Message(
                phone=phone,
                user_message=user_msg,
                assistant_message=assistant_msg,
            )
            session.add(msg)
            await session.commit()
