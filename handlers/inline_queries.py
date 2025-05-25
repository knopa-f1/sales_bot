from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram import Router
from uuid import uuid4

from lexicon.faq import FAQ_ENTRIES_RU

router = Router()

@router.inline_query()
async def handle_faq_inline_query(inline_query: InlineQuery):
    query = inline_query.query.lower()

    results = []

    for entry in FAQ_ENTRIES_RU:
        if query in entry["question"].lower() or query == "":
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=entry["question"],
                    input_message_content=InputTextMessageContent(
                        message_text=f"<b>{entry['question']}</b>\n\n{entry['answer']}",
                        parse_mode="HTML"
                    ),
                    description=entry["answer"][:50] + "..."
                )
            )

    await inline_query.answer(results, cache_time=1)
