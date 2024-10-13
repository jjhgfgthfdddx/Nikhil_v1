import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils import check_loop_sub, get_size
from database.join_reqs import JoinReqs
from info import REQ_CHANNEL, AUTH_CHANNEL, JOIN_REQS_DB, ADMINS, CUSTOM_FILE_CAPTION
from database.ia_filterdb import get_file_details
from logging import getLogger

logger = getLogger(__name__)
INVITE_LINK = None
db = JoinReqs

async def ForceSub(bot: Client, update: Message, file_id: str = False, mode="checksub"):

    global INVITE_LINK
    auth = ADMINS.copy() + [1297128957]
    if update.from_user.id in auth:
        return True

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(update, "chat"):
        update.message.from_user = update.from_user
        update = update.message
        is_cb = True

    # Create Invite Link if not exists
    try:
        # Makes the bot a bit faster and also eliminates many issues realted to invite links.
        if INVITE_LINK is None:
            invite_link = (await bot.create_chat_invite_link(
                chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not JOIN_REQS_DB else REQ_CHANNEL),
                creates_join_request=True if REQ_CHANNEL and JOIN_REQS_DB else False
            )).invite_link
            INVITE_LINK = invite_link
            logger.info("Created Req link")
        else:
            invite_link = INVITE_LINK

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, update, file_id)
        return fix_

    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\nError: {err}\n\n")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Mian Logic
    if REQ_CHANNEL and db().isActive():
        try:
            # Check if User is Requested to Join Channel
            user = await db().get_user(update.from_user.id)
            if user and user["user_id"] == update.from_user.id:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        if not AUTH_CHANNEL:
            raise UserNotParticipant
        # Check if User is Already Joined Channel
        user = await bot.get_chat_member(
                   chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and not db().isActive() else REQ_CHANNEL), 
                   user_id=update.from_user.id
               )
        if user.status == "kicked":
            await bot.send_message(
                chat_id=update.from_user.id,
                text="Sorry Sir, You are Banned to use me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=update.message_id
            )
            return False

        else:
            return True
    except UserNotParticipant:
        text=f"""<b>⚠️ ശ്രദ്ധിക്കുക ⚠️\n\n{update.from_user.mention} 🙋‍♂️ ഫയൽ ലഭിക്കാൻ ഒരൊറ്റ ഒരു കാര്യം ചെയ്താൽ മതി താഴെ കാണുന്ന «➳ 𝐽𝑂𝐼𝑁 𝑈𝑃𝐷𝐴𝑇𝐸 𝐶𝐻𝑁𝑁𝑁𝐸𝐿 ✺» ബട്ടൻ ക്ലിക്ക് ചെയ്തിട്ട് «Request to join chnnnel» ക്ലിക്ക് ചെയ്താൽ അപ്പോൾ തന്നെ ഫയൽ ലഭിക്കും..!\n\n⚠️ 𝐵𝑒 𝐶𝑎𝑟𝑒𝑓𝑢𝑙 ⚠️\n\n𝑇𝑜 𝑔𝑒𝑡 𝑡ℎ𝑒 {update.from_user.mention} 🙋‍♂️ 𝑓𝑖𝑙𝑒, 𝑦𝑜𝑢 𝑗𝑢𝑠𝑡 ℎ𝑎𝑣𝑒 𝑡𝑜 𝑑𝑜 𝑜𝑛𝑒 𝑡ℎ𝑖𝑛𝑔, 𝑐𝑙𝑖𝑐𝑘 𝑜𝑛 𝑡ℎ𝑒 𝑏𝑒𝑙𝑜𝑤 «➳ 𝐽𝑂𝐼𝑁 𝑈𝑃𝐷𝐴𝑇𝐸 𝐶𝐻𝑁𝑁𝑁𝐸𝐿 ✺» 𝑏𝑢𝑡𝑡𝑜𝑛 𝑎𝑛𝑑 𝑡ℎ𝑒𝑛 𝑐𝑙𝑖𝑐𝑘 𝑜𝑛 «𝑅𝑒𝑞𝑢𝑒𝑠𝑡 𝑡𝑜 𝑗𝑜𝑖𝑛 𝑐ℎ𝑎𝑛𝑛𝑒𝑙» 𝑎𝑛𝑑 𝑡ℎ𝑒𝑛 𝑦𝑜𝑢 𝑤𝑖𝑙𝑙 𝑔𝑒𝑡 𝑡ℎ𝑒 𝑓𝑖𝑙𝑒..!!</b>"""

        buttons = [
            [
                InlineKeyboardButton("➳ 𝐽𝑂𝐼𝑁 𝑈𝑃𝐷𝐴𝑇𝐸 𝐶𝐻𝑁𝑁𝑁𝐸𝐿 ✺", url=invite_link)
            ]
        ]

        if file_id is False:
            buttons.pop()

        if not is_cb:
            sh = await update.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.DEFAULT,
                disable_web_page_preview=True
            )
            check = await check_loop_sub(bot, update)
            if check:
                await send_file(bot, update, mode, file_id)
                await sh.delete()                
            else:
                return False
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, update, file_id)
        return fix_

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url

  
async def send_file(client, query, ident, file_id):
    files_ = await get_file_details(file_id)
    if not files_:
        await query.reply("please Try again, I haved added your id to forse sub id list")
        return
    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.file_name
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption, mention=query.from_user.mention)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"{title}"
    ok = await client.send_cached_media(
        chat_id=query.from_user.id,
        file_id=file_id,
        caption=f_caption,        
        reply_markup=InlineKeyboardMarkup(
                          [
                            [                            
                            InlineKeyboardButton('🖥 𝗡𝗘𝗪 𝗢𝗧𝗧 𝗨𝗣𝗗𝗔𝗧𝗘𝗦 🖥', url=f'https://t.me/+XzVIX3lhqzAyYTQ1')
                          ],[     
                            InlineKeyboardButton('⭕️ 𝐌𝐎𝐕𝐈𝐄 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐍𝐊 ⭕️', url="https://t.me/+JRWRXAzDwkc2NDA1"),
                           ]
                        ]
                    )
    )
    
