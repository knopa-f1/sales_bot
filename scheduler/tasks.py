import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.connection import database
from db.models import Broadcast

logger = logging.getLogger(__name__)


async def run_broadcasts(bot):
    async with database.session as session:
        result = await session.execute(
            select(Broadcast).where(Broadcast.status == 'pending').options(
                selectinload(Broadcast.recipients)
            )
        )
        broadcasts = result.scalars().all()

        for b in broadcasts:
            recipients = b.recipients
            logger.info("Рассылка #%s для %d пользователей", b.id, len(recipients))

            for user in recipients:
                try:
                    await bot.send_message(chat_id=user.chat_id, text=b.message)
                except Exception as e:
                    logger.error("Не удалось отправить %s: %s", user.chat_id, e)

            b.status = 'sent'
            b.sent_at = datetime.now()

        await session.commit()
