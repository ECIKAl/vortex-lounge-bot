import discord
from discord.ext import commands
import asyncio
import io

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

WELCOME_CHANNEL_ID = 1210695434406858813

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {bot.user}')
    print('Vortex Lounge Bot is online and fully fixed!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if "http://" in message.content or "https://" in message.content or "discord.gg/" in message.content or "discord.com/invite/" in message.content:
        if not message.author.guild_permissions.manage_messages:
            try:
                await message.delete()
                await message.channel.send(f'ممنوع نشر الروابط والدعوات هنا يا {message.author.mention}، حافظ على نظافة السيرفر!', delete_after=5)
            except Exception as e:
                print(f"خطأ في الحماية: {e}")

    await bot.process_commands(message)

# زرار رتبة LADY بدون جملة "أنا فتاة" وبدون رسائل مزعجة
class WelcomeButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="الحصول على رتبة LADY 🌸", style=discord.ButtonStyle.secondary, custom_id="vortex_lady_role_btn_custom_v3")
    async def lady_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        lady_role = discord.utils.get(guild.roles, name="⚘ •丨LADY")
        
        if not lady_role:
            await interaction.response.send_message("⚠️ عذراً يا غالي، رتبة `⚘ •丨LADY` غير موجودة بالسيرفر بنفس الاسم المزخرف.", ephemeral=True)
            return

        if lady_role in interaction.user.roles:
            await interaction.response.send_message("✨ أنت تمتلكين رتبة `⚘ •丨LADY` بالفعل يا فندم!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(lady_role)
                await interaction.response.send_message("🌸 تم منحك رتبة **⚘ •丨LADY** بنجاح!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message("❌ حدث خطأ، تأكد أن رتبة البوت أعلى من رتبة LADY في قائمة الرتب.", ephemeral=True)

@bot.event
async def on_member_join(member):
    guild = member.guild
    
    # 1. إعطاء رتبة Member المزخرفة تلقائياً
    member_role = discord.utils.get(guild.roles, name="✿ •丨Member")
    if member_role:
        try:
            await member.add_roles(member_role)
        except Exception as e:
            print(f"فشل في إعطاء رتبة Member المزخرفة: {e}")

    # 2. إرسال رسالة الترحيب مع الجيف الخاص بالترحيب فقط
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID) or discord.utils.get(guild.text_channels, name="الترحيب")
    
    if welcome_channel:
        embed = discord.Embed(
            title="🚀 ┋ عـضـو جـديـد أنـار الـسـيـرفـر",
            description=(
                f"أهلاً ومرحباً بك يا تاج راسي {member.mention} في سيرفر **{guild.name}**!\n\n"
                f"> نورتنا وشرفتتنا يا غالي. نتمنى لك أوقاتاً ممتعة ومميزة معنا.\n"
                f"> 📌 **تنبيه:** يرجى قراءة القوانين والالتزام بها لضمان راحتك.\n\n"
                f"🌸 **إذا كنتِ فتاة، يمكنكِ الضغط على الزر بالأسفل للحصول على رتبة LADY الخاصة بكِ فوراً!**"
            ),
            color=discord.Color.from_rgb(0, 255, 204)
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        # جيف الترحيب المخصص
        embed.set_image(url="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnRhZWk0azM0ZGE3aDYxc2tjMzRvOWloYTNvZnhkbXowdWRxZWs0YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FWtVYDHIxgGgE/giphy.gif")
        embed.set_footer(text=f"Member #{guild.member_count} • Vortex Lounge Welcome System", icon_url=guild.icon.url if guild.icon else None)

        try:
            await welcome_channel.send(embed=embed, view=WelcomeButtonView())
        except Exception as e:
            print(f"فشل في إرسال رسالة الترحيب: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong! 🏓 سرعة استجابة البوت: {round(bot.latency * 1000)}ms')

async def send_transcript(guild, channel_name, messages_list):
    category = discord.utils.get(guild.categories, name="TICKET")
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    for role in guild.roles:
        if role.permissions.administrator or role.permissions.manage_channels:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    logs_channel = discord.utils.get(guild.text_channels, name="ticket-logs")
    if not logs_channel:
        logs_channel = await guild.create_text_channel("ticket-logs", overwrites=overwrites, category=category)

    transcript_text = "\n".join(messages_list)
    
    if len(transcript_text) > 1900:
        file = discord.File(fp=io.BytesIO(transcript_text.encode('utf-8')), filename=f"transcript-{channel_name}.txt")
        await logs_channel.send(f"📁 **سجل تذكرة مغلقة:** `{channel_name}`", file=file)
    else:
        embed = discord.Embed(
            title=f"📁 سجل تذكرة مغلقة: {channel_name}",
            description=f"```text\n{transcript_text[:1900]}\n```",
            color=discord.Color.dark_embed()
        )
        await logs_channel.send(embed=embed)

async def create_support_ticket(interaction: discord.Interaction):
    guild = interaction.guild
    member = interaction.user

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    category = discord.utils.get(guild.categories, name="TICKET")
    if not category:
        category = await guild.create_category("TICKET")

    channel_name = f'ticket-{member.name.lower()}'
    existing_channel = discord.utils.get(category.text_channels, name=channel_name)
    if existing_channel:
        await interaction.response.send_message(f'⚠️ يا تاج راسي، لديك تذكرة مفتوحة بالفعل هنا: {existing_channel.mention}', ephemeral=True, delete_after=5)
        return

    await interaction.response.defer(ephemeral=True)

    ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
    
    class CloseView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="🔒 إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="vortex_close_ticket_final_fixed_v2")
        async def close_btn(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.send_message("⏳ جاري حفظ السجل وإغلاق التذكرة...", ephemeral=True)
            
            messages = [f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.author}: {msg.content}" async for msg in ticket_channel.history(limit=1000, oldest_first=True)]
            await send_transcript(guild, ticket_channel.name, messages)

            await asyncio.sleep(2)
            await ticket_channel.delete()

    embed = discord.Embed(
        title="🎫 تذكرة دعم فني جديدة",
        description=f"أهلاً بك يا {member.mention}\nيرجى كتابة مشكلتك أو استفسارك بالتفصيل، وسيقوم فريق الإدارة بمساعدتك في أقرب وقت.\n\n⚠️ **ملاحظة:** سيتم إغلاق التذكرة تلقائياً بعد 30 دقيقة من عدم النشاط.",
        color=discord.Color.from_rgb(88, 101, 242)
    )
    embed.set_footer(text="Vortex Lounge Support System", icon_url=guild.icon.url if guild.icon else None)

    await ticket_channel.send(embed=embed, view=CloseView())

    def check(m):
        return m.channel == ticket_channel and not m.author.bot

    try:
        while True:
            await bot.wait_for('message', timeout=1800.0, check=check)
    except asyncio.TimeoutError:
        try:
            messages = [f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.author}: {msg.content}" async for msg in ticket_channel.history(limit=1000, oldest_first=True)]
            await send_transcript(guild, ticket_channel.name, messages)
            await ticket_channel.send("⏳ انتهت مهلة 30 دقيقة بدون نشاط. سيتم إغلاق التذكرة.")
            await asyncio.sleep(3)
            await ticket_channel.delete()
        except:
            pass

class SupportPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة دعم", style=discord.ButtonStyle.success, emoji="🎟️", custom_id="vortex_open_ticket_final_fixed_v2")
    async def open_ticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_support_ticket(interaction)

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="🎫 VORTEX LOUNGE | مركز الدعم والمساعدة",
        description="مرحباً بك في سيرفر **Vortex Lounge**.\n\nإذا كنت تواجه أي مشكلة تقنية أو استفسار، **اضغط على الزر بالأسفل** لفتح تذكرة خاصة بك وسيقوم فريق الإدارة بمساعدتك فوراً.",
        color=discord.Color.from_rgb(47, 49, 54)
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
    embed.set_footer(text="Vortex Lounge • نظام التذاكر الرسمي", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

    view = SupportPanelView()
    await ctx.send(embed=embed, view=view)

@bot.command()
@commands.has_permissions(administrator=True)
async def rules(ctx):
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="⚖️ ┋ قــوانــيــن ســيــرفــر VORTEX LOUNGE",
        description=(
            "أهلاً بك يا تاج راسي في سيرفرنا. لضمان بيئة محترمة وممتعة للجميع، يُرجى الالتزام بالقواعد الآتية:\n\n"
            "**[ 01 ] ┋ الاحترام المتبادل:**\n> يُمنع منعاً باتاً الإهانة، أو التلفظ بألفاظ نابية، أو التقليل من شأن أي عضو.\n\n"
            "**[ 02 ] ┋ منع السبام والتكرار:**\n> يمنع إرسال الرسائل المتكررة أو الحروف المزعجة (Spam) في الرومات العامة.\n\n"
            "**[ 03 ] ┋ حظر الروابط والدعوات:**\n> يمنع تماماً نشر أي روابط خارجية أو دعوات لسيرفرات أخرى دون إذن الإدارة.\n\n"
            "**[ 04 ] ┋ منع النقاشات السياسية والدينية:**\n> يُحظر التطرق للمواضيع السياسية أو الدينية منعاً للمشاكل والفتن.\n\n"
            "**[ 05 ] ┋ الالتزام بالرومات المخصصة:**\n> يرجى وضع كل محتوى في مكانه الصحيح، وطلب المساعدة عبر التذاكر حصراً.\n\n"
            "**[ 06 ] ┋ المحتوى اللائق فقط:**\n> يُمنع إرسال صور، مقاطع، أو إيموجيات مخلة بالآداب أو تحتوي على إيحاءات سيئة.\n\n"
            "**[ 07 ] ┋ منع انتحال الشخصيات:**\n> يمنع محاولة انتحال صفة الإدارة أو أي عضو آخر بأي شكل من الأشكال.\n\n"
            "**[ 08 ] ┋ التعامل مع الإدارة:**\n> يجب احترام قرارات الإدارة وفي حال وجود شكوى يتم فتح تذكرة خاصة.\n\n"
            "**[ 09 ] ┋ الالتزام بقواعد ديسكورد العامة:**\n> يجب مراعاة شروط خدمة منصة Discord الأساسية داخل السيرفر."
        ),
        color=discord.Color.from_rgb(138, 43, 226)
    )
    
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
        
    # جيف القوانين المخصص
    embed.set_image(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ245MW1naHE0YmpmMTgzYW1nZmJqaGthdmY5YW5oNXh5bHQ5YzMzNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UC8DbMqXvkpd6/giphy.gif")
    embed.set_footer(text="Vortex Lounge • Server Rules & Regulations", icon_url=guild.icon.url if guild.icon else None)

    await ctx.send(embed=embed)

bot.run('')