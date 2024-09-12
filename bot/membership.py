import logging
from aiogram import Bot, BaseMiddleware
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Callable, Any, Awaitable
from aiogram.exceptions import TelegramBadRequest
from config import GROUP_CHAT_ID
from handlers.admin_menu import is_user_blocked

class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message], Awaitable[Any]],
        event: Message,
        data: dict
    ) -> Any:
        user_id = event.from_user.id # type: ignore

        if await is_user_blocked(user_id): # type: ignore
            await event.answer("❌ Вы заблокированы и не можете пользоваться ботом\n\nПо всем вопросам обращайтесь в поддержку *@refbot_admin*.", parse_mode="Markdown")
            return
        
        if not await check_membership(event.bot, event): # type: ignore
            return
        
        return await handler(event, data) # type: ignore
         
async def check_membership(bot: Bot, message: Message) -> bool:
    """
    Проверяет, находится ли пользователь в чате.
    Если нет, отправляет сообщение с просьбой присоединиться к чату.
    
    :param bot: Инстанс бота
    :param message: Сообщение пользователя
    :return: True, если пользователь в чате, False если нет
    """
    user_id = message.from_user.id  # type: ignore
    try:
        member = await bot.get_chat_member(GROUP_CHAT_ID, user_id)  # type: ignore
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            link_on_group = InlineKeyboardButton(text="🔗 Вступить в чат", url="https://t.me/+PKddIYAM4so5MzNi")
            check_user_in_group = InlineKeyboardButton(text="🔄 Проверить", callback_data="check_user_in_group")
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[[link_on_group], [check_user_in_group]])
            
            await message.answer(
                "⚠ Для использования бота вам необходимо вступить в [чат](https://t.me/+PKddIYAM4so5MzNi).\n\n"
                "После вступления нажмите 'Проверить'.",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=inline_kb
            )
            return False
    except TelegramBadRequest as e:
        logging.error(f"Error checking user status in chat: {e}")
        await message.answer("❌ Произошла ошибка при проверке вашего статуса в чате. Пожалуйста, попробуйте позже.")
        return False
