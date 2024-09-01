import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import sqlite3

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_ROLE_IDS = [123456789012345678, 987654321098765432]
GUILD_ID = 1278457839609843784

PAYMENT_METHODS = [
    {"name": "Сбербанк", "card_number": "220216934151", "note": "Копейки обязательно"},
    {"name": "Тинькофф", "card_number": "553691387654", "note": "Перевод без комиссии"},
]

PRODUCT_PRICES = {
    "NITRO FULL | 1 месяц": 399,
    "NITRO BASIC | 1 месяц": 150,
    "Boost Discord | 2 шт": 70,
    "Boost Discord | 4 шт": 140,
    "Boost Discord | 8 шт": 340,
    "Boost Discord | 14 шт": 580,
    "Аккаунты Telegram Россия": 260,
    "Аккаунты Telegram Другие страны": 130,
    "Новореги Дискорд": 20,
    "Новореги Дискорд Nitro": 110,
    "Программа для генерации нитро": 100,
    "Программа для FunPay автоматический бот": 300,
    "CeЛF-Б0T для Дискорд v2": 200,
    "CeЛF-Б0T для Дискорд v1": 70,
}

EMOJIS = {
    "NITRO FULL | 1 месяц": "✨",
    "NITRO BASIC | 1 месяц": "💫",
    "Boost Discord | 2 шт": "🚀",
    "Boost Discord | 4 шт": "🔥",
    "Boost Discord | 8 шт": "⚡",
    "Boost Discord | 14 шт": "💥",
    "Аккаунты Telegram Россия": "📱",
    "Аккаунты Telegram Другие страны": "💬",
    "Новореги Дискорд": "🆕",
    "Новореги Дискорд Nitro": "🎉",
    "Программа для генерации нитро": "🔧",
    "Программа для FunPay автоматический бот": "🤖",
    "CeЛF-Б0T для Дискорд v2": "🛠️",
    "CeЛF-Б0T для Дискорд v1": "🔨",
}

class InfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.selected_product = None
        self.order_channel = None
        self.order_message = None
        self.custom_price = None
        self.conn = sqlite3.connect('users.db')
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS agreed_users (user_id INTEGER PRIMARY KEY)"
            )

    def has_agreed(self, user_id):
        cursor = self.conn.execute(
            "SELECT 1 FROM agreed_users WHERE user_id = ?", (user_id,)
        )
        return cursor.fetchone() is not None

    def add_user(self, user_id):
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO agreed_users (user_id) VALUES (?)", (user_id,)
            )

    @commands.command(name="start")
    async def start(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            if self.has_agreed(ctx.author.id):
                await ctx.send("Вы уже согласились с пользовательским соглашением.")
                await self.send_main_menu(ctx)
            else:
                embed = discord.Embed(
                    title="Добро пожаловать в $ SHOP! ×",
                    description=(
                        "Для дальнейшего использования данного бота "
                        "вам надо подтвердить [пользовательское соглашение](https://telegra.ph/Polzovatelskoe-soglashenie-08-12-10).\n"
                        f"ID: {ctx.author.id} | Дата: {datetime.now().strftime('%Y-%m-%d')} | SERVER: AUTH-3"
                    ),
                    color=discord.Color.blurple()
                )

                view = discord.ui.View(timeout=None)
                agree_button = discord.ui.Button(label="Я согласен с соглашением", style=discord.ButtonStyle.green)
                agree_button.callback = lambda interaction: self.agree_callback(interaction, ctx.author.id)
                view.add_item(agree_button)

                await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("Эта команда работает только в личных сообщениях.")

    async def agree_callback(self, interaction: discord.Interaction, user_id):
        self.add_user(user_id)
        await interaction.response.send_message("Спасибо за подтверждение! Теперь вы можете использовать бота.", ephemeral=True)
        await self.send_main_menu(interaction)

    async def send_main_menu(self, ctx_or_interaction):
        embed = discord.Embed(
            title="Главное меню",
            description="Выберите один из разделов ниже:",
            color=discord.Color.blurple()
        )

        view = discord.ui.View(timeout=None)
        about_button = discord.ui.Button(label="О создателе", style=discord.ButtonStyle.primary, emoji="👤")
        support_button = discord.ui.Button(label="Поддержка", style=discord.ButtonStyle.primary, emoji="🛠️")
        shop_button = discord.ui.Button(label="Товары", style=discord.ButtonStyle.primary, emoji="🛒")

        about_button.callback = self.about_creator
        support_button.callback = self.support_info
        shop_button.callback = self.send_product_selection

        view.add_item(about_button)
        view.add_item(support_button)
        view.add_item(shop_button)

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.followup.send(embed=embed, view=view)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

    async def about_creator(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="О создателе",
            description=(
                "Телеграм создателя: [кликабельно](https://t.me/tropic_yt) (частые розыгрыши на разные подписки)\n"
                "Дискорд: zovut_serezka\n"
                "Сайт: [клик](https://www.tropic.website/)"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def support_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Поддержка",
            description=(
                "Кликните [СЮДА](https://discord.com/channels/1245344234375217223/1250896552768307301) "
                "- и задавайте интересующие вопросы. Наши саппорты помогут!"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_product_selection(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Выберите товар из списка",
            description="Нажмите на товар, чтобы продолжить",
            color=discord.Color.blurple()
        )

        view = discord.ui.View(timeout=None)
        select = discord.ui.Select(
            placeholder="Выберите товар",
            options=[
                discord.SelectOption(label=product, emoji=EMOJIS.get(product, "📦"))
                for product in PRODUCT_PRICES.keys()
            ]
        )
        select.callback = self.select_callback
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def select_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]
        self.selected_product = selected_option
        embed = discord.Embed(title="Подтверждение выбора", color=discord.Color.green())

        price = PRODUCT_PRICES.get(selected_option, "Неизвестно")
        embed.description = f"Вы выбрали: {selected_option}\nЦена товара: {price} ₽"

        view = discord.ui.View(timeout=None)
        confirm_button = discord.ui.Button(label="Оплатить", style=discord.ButtonStyle.green)
        confirm_button.callback = self.confirm_callback
        view.add_item(confirm_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def confirm_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Подтверждение заказа",
            description="Вы действительно хотите приобрести данный товар?",
            color=discord.Color.orange()
        )

        view = discord.ui.View(timeout=None)
        order_button = discord.ui.Button(label="Да, перейти к заказу", style=discord.ButtonStyle.blurple)
        order_button.callback = self.order_callback
        view.add_item(order_button)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def order_callback(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            await interaction.response.send_message("Ошибка: не удалось получить гильдию.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }

        for role_id in ALLOWED_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        self.order_channel = await guild.create_text_channel(
            name=f"order-{interaction.user.name}",
            overwrites=overwrites
        )

        price = PRODUCT_PRICES.get(self.selected_product, "Неизвестно")

        embed = discord.Embed(
            title="ТропаШоп | Оформление заказа",
            description=(
                f"Имя пользователя: {interaction.user.name}\n"
                f"Товар: {self.selected_product}\n"
                f"Цена: {price} ₽\n"
                f"ID Заказа: #T1OZ2Q\n\n"
                f"Состояние заказа: Не оплачен 🔴"
            ),
            color=discord.Color.red()
        )
        embed.set_image(url="https://i.ibb.co/vVLGkBt/image.png")

        self.order_message = await self.order_channel.send(embed=embed)
        await interaction.response.send_message(f"Приватный канал создан: {self.order_channel.mention}", ephemeral=True)

    @commands.command(name="счет")
    @commands.has_permissions(administrator=True)
    async def invoice(self, ctx, amount: float):
        await ctx.message.delete()
        if not self.selected_product:
            await ctx.send("Ошибка: товар не выбран.")
            return

        self.custom_price = amount

        embed = discord.Embed(
            title="Пожалуйста, оплатите заказ",
            description=f"После оплаты обязательно пришлите чек.\n\n"
                        f"Вам надо перевести: {self.custom_price} ₽\n",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://i.ibb.co/vVLGkBt/image.png")

        for method in PAYMENT_METHODS:
            formatted_card_number = ' '.join(method["card_number"][i:i+4] for i in range(0, len(method["card_number"]), 4))
            embed.add_field(
                name=method["name"],
                value=f"{method['note']}\nНомер карты: `{formatted_card_number}`",
                inline=False
            )

        embed.add_field(name="Товар", value=self.selected_product, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="оплачено")
    @commands.has_permissions(administrator=True)
    async def paid(self, ctx):
        await ctx.message.delete()
        if self.order_message and self.order_channel:
            embed = self.order_message.embeds[0]
            if "Не оплачен 🔴" in embed.description:
                embed.description = embed.description.replace("Не оплачен 🔴", "Оплачен 🟢")
                await self.order_message.edit(embed=embed)
                await ctx.send("Заказ обновлён на 'Оплачен'.", delete_after=5)
            else:
                await ctx.send("Заказ уже был обновлён.", delete_after=5)

    @commands.command(name="завершить")
    @commands.has_permissions(administrator=True)
    async def complete_order(self, ctx):
        await ctx.message.delete()
        if self.order_channel:
            embed = discord.Embed(
                title="Ваш заказ выполнен!",
                description="Оставьте отзыв в канале -> https://discord.com/channels/1278457839609843784/1279772501328793691 ⚡",
                color=discord.Color.green()
            )
            await self.order_channel.send(embed=embed)
            await ctx.send("Заказ завершён. Канал будет удалён через 1 минуту.", delete_after=5)
            await asyncio.sleep(60)
            await self.order_channel.delete()
            self.order_channel = None

    @commands.command()
    async def infof(self, ctx):
        await ctx.message.delete()
        image_embed = discord.Embed(color=discord.Color.blurple())
        image_url = "https://cdn.discordapp.com/attachments/1148965223043178576/1261265199353167872/shop.png?ex=66affe00&is=66aeac80&hm=40d98cb4e208f901a968d6730cdc46d00b79b1e7e21d2c921fc309f3cc231150&"
        image_embed.set_image(url=image_url)

        info_embed = discord.Embed(
            title="Приветствуем в нашем NitroShop",
            description="Выберите интересующую вас категорию и воспользуйтесь **интерактивным меню**, чтобы ознакомиться с информацией.\n\n"
                        "・ [Discord](https://discord.com/) - услуги, связанные с мессенджером.\n"
                        "・ [BoostDiscord](https://discord.com/) - Бусты на ваш Discord.\n"
                        "・ [Аккаунты Telegram](https://telegram.org/) - подписка для Telegram.\n"
                        "・ [Полезное ПО](https://discord.gg/FFRRm5YN) - программы и боты.",
            color=discord.Color.blurple()
        )
        info_embed.set_footer(text="Эта информация будет отправлена приватно")

        view = discord.ui.View(timeout=None)
        select = discord.ui.Select(
            placeholder="Выберите категорию",
            options=[
                discord.SelectOption(label="Discord", emoji="💬", description="Подписка Discord Nitro"),
                discord.SelectOption(label="BoostDiscord", emoji="🚀", description="Бустинг на ваш дискорд сервер"),
                discord.SelectOption(label="Аккаунты Telegram", emoji="📱", description="Аккаунты Телеграммы"),
                discord.SelectOption(label="Новореги Дискорд", emoji="🆕", description="Новые аккаунты Discord"),
                discord.SelectOption(label="Новореги Дискорд Nitro", emoji="🎉", description="Новые аккаунты с Nitro"),
                discord.SelectOption(label="Полезное ПО", emoji="🔧", description="Программы и боты для различных задач")
            ]
        )
        select.callback = self.category_select_callback
        view.add_item(select)

        await ctx.send(embeds=[image_embed, info_embed], view=view)

    async def category_select_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]

        if selected_option == "Discord Nitro":
            await self.button1_callback(interaction)
        elif selected_option == "BoostDiscord":
            await self.button2_callback(interaction)
        elif selected_option == "Аккаунты Telegram":
            await self.button3_callback(interaction)
        elif selected_option == "Новореги Дискорд":
            await self.button4_callback(interaction)
        elif selected_option == "Новореги Дискорд Nitro":
            await self.button5_callback(interaction)
        elif selected_option == "Полезное ПО":
            await self.useful_software_callback(interaction)

    async def button1_callback(self, interaction: discord.Interaction):
        image_embed = discord.Embed(color=discord.Color.green())
        image_url = "https://cdn.discordapp.com/attachments/1238905535957307412/1269492273708666880/img.png?ex=66b04250&is=66aef0d0&hm=7ceb18b56b27bf24dc028ff4d4db56c0ec084c9123d7e35e13e514dd2d6a5984&"
        image_embed.set_image(url=image_url)

        info_embed = discord.Embed(
            title="                DISCORD NITRO",
            description="```Цены (Без гарантии | Активация 100%)```\n\n"
                        "NITRO FULL | 1 месяц - 399 ₽\n"
                        "NITRO BASIC | 1 месяц - 150 ₽\n\n"
                        "```Цены (Для тех, у кого еще не было)```\n\n"
                        "NITRO FULL | 3 месяца - 290 ₽\n"
                        "NITRO FULL | 1 месяц - 180 ₽",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embeds=[image_embed, info_embed], ephemeral=True)

    async def button2_callback(self, interaction: discord.Interaction):
        image_embed = discord.Embed(color=discord.Color.green())
        image_url = "https://cdn.discordapp.com/attachments/1238905535957307412/1269487462749569044/p1_3356614_c6a48370.jpeg?ex=66b03dd5&is=66aeec55&hm=c5e53a4394201c784db89bc8b4f3d96efb361c74d7f7d741e707c595d57b8be9&"
        image_embed.set_image(url=image_url)

        info_embed = discord.Embed(
            title="               DISCORD BOOST",
            description="```DISCORD BOOST 2(ШТ) -> 1 MOTH```\n"
                        "Boost Discord (2шт)\n\n"
                        "PRICE: 70RUB\n"
                        "Способы оплаты: Любая удобная для вас (сделку можно провести через FunPay)\n\n"
                        "```DISCORD BOOST 4(ШТ) -> 1 MOTH```\n"
                        "Boost Discord (4шт)\n\n"
                        "PRICE: 140RUB\n"
                        "Способы оплаты: Любая удобная для вас (сделку можно провести через FunPay)\n\n"
                        "```DISCORD BOOST 8(ШТ) -> 1 MOTH```\n"
                        "Boost Discord (8шт) -> (1 месяц)\n\n"
                        "PRICE: 340RUB\n"
                        "Способы оплаты: Любая удобная для вас (сделку можно провести через FunPay)\n\n"
                        "```DISCORD BOOST 14(ШТ) -> 1 MOTH```\n"
                        "Boost Discord (14шт) -> (1 месяц)\n\n"
                        "PRICE: 580RUB\n"
                        "Способы оплаты: Любая удобная для вас (сделку можно провести через FunPay)",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embeds=[image_embed, info_embed], ephemeral=True)

    async def button3_callback(self, interaction: discord.Interaction):
        image_embed = discord.Embed(color=discord.Color.green())
        image_url = "https://cdn.discordapp.com/attachments/1238905535957307412/1269488190469701773/t2.jpeg?ex=66b03e82&is=66aeed02&hm=d0cfda3c9b7eef4801aa9e26d55027030f6cbb168ca369eb0fb855372f10c4c2&"
        image_embed.set_image(url=image_url)

        info_embed = discord.Embed(
            title="  АККАУНТЫ TELEGRAM",
            description="""```Цены```
            
```Аккаунты новореги (БОЛЬШОЙ ШАНС БАНА ЕСЛИ БЕЗ ПРОКСИ)```
Аккаунты Telegram `Russia` - 260 ₽
Аккаунты Telegram Другие страны - 130 ₽
```Аккаунты с отлегой (100% БЕЗ БАНА)```
Аккаунты Telegram `Russia` - 330 ₽ (отлега 10 дней)
Аккаунты Telegram Другие страны (отлега 10 дней) - 230 ₽

```Описание```

Аккаунты Telegram - Это аккаунты под разные цели. Подходят для: Спама, Рассылки, Обходов блокировок и т.п.""",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embeds=[image_embed, info_embed], ephemeral=True)

    async def button4_callback(self, interaction: discord.Interaction):
        image_embed = discord.Embed(color=discord.Color.green())
        image_url = "https://cdn.discordapp.com/attachments/1238905535957307412/1269492273708666880/img.png?ex=66b04250&is=66aef0d0&hm=7ceb18b56b27bf24dc028ff4d4db56c0ec084c9123d7e35e13e514dd2d6a5984&"
        image_embed.set_image(url=image_url)

        info_embed = discord.Embed(
            title="НОВОРЕГИ ДИСКОРД",
            description="```Цены```\n\n"
                        "Новореги Дискорд - 20 ₽\n\n"
                        "```Описание```\n\n"
                        "Новые аккаунты Discord.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embeds=[image_embed, info_embed], ephemeral=True)

    async def button5_callback(self, interaction: discord.Interaction):
        image_embed = discord.Embed(color=discord.Color.green())
        image_url = "https://cdn.discordapp.com/attachments/1238905535957307412/1269492273708666880/img.png?ex=66b04250&is=66aef0d0&hm=7ceb18b56b27bf24dc028ff4d4db56c0ec084c9123d7e35e13e514dd2d6a5984&"
        image_embed.set_image(url=image_url)

        info_embed = discord.Embed(
            title="НОВОРЕГИ ДИСКОРД NITRO",
            description="```Цены```\n\n"
                        "Новореги Дискорд Nitro - 110 ₽\n\n"
                        "```Описание```\n\n"
                        "Новые аккаунты с активированным Nitro.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embeds=[image_embed, info_embed], ephemeral=True)

    async def useful_software_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Полезное ПО", 
            description=(
                "1. **Программа для генерации нитро** 🔧\n"
                "   Описание: Программа генерирует нитро гифтами или с активацией турецкой картой\n"
                "   Нужно: Турецкая карта (необязательна), Установленный Python Прокси http или https, впн\n"
                "   PRICE: 100RUB\n\n"
                "2. **Программа для FunPay автоматический бот** 🤖\n"
                "   Описание: Бот для автоматизации продаж на FunPay\n"
                "   Нужно: Python\n"
                "   PRICE: 300RUB\n\n"
                "3. **CeЛF-Б0T для Дискорд v2** 🛠️\n"
                "   Описание: Новый селф для дискорд с множеством возможностей\n"
                "   Нужно: Python, Хостинг (необязательно)\n"
                "   PRICE: 200RUB\n\n"
                "4. **CeЛF-Б0T для Дискорд v1** 🔨\n"
                "   Описание: Упрощённая версия селфа с CHAT-GPT 3.5 turbo\n"
                "   Нужно: Python, Хостинг (необязательно)\n"
                "   PRICE: 70RUB"
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command()
    async def image(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(color=discord.Color.blurple())
        image_url = "https://cdn.discordapp.com/attachments/1193894842904891394/1269408926055792650/image.png?ex=66aff4b0&is=66aea330&hm=a800c37ab482815efa2844bc7c414606f27949d73e604bb8626264ca34f35309&"
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.add_cog(InfoCommand(bot))

if __name__ == "__main__":
    bot.run('token')