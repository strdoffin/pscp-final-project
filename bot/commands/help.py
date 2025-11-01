"""Help Command Register and Handle"""

from json import load
from math import ceil

from discord import Client
from discord import Object
from discord import Interaction
from discord import Embed
from discord import Color
from discord import ButtonStyle
from discord.ui import View
from discord.ui import Button

COMMANDS = []
COMMANDS_PAGE = 0
COMMANDS_PER_PAGE = 3

try:
    with open('data/commands.json', 'r', encoding='utf-8') as file:
        COMMANDS = load(file)
        COMMANDS_PAGE = ceil(len(COMMANDS) / COMMANDS_PER_PAGE)
except Exception as e:
    print("Error occurs while fetching commands list.", e)


def create_help_embed(page=1):
    """
    สร้าง Embed สำหรับคำสั่ง Help
    """
    embed = Embed(
        title="🤖 PSCP Bot Command Center",
        description=(
            "> สงสัยว่าบอททำอะไรได้บ้าง? มาดูคำสั่งทั้งหมดที่คุณใช้ได้ที่นี่เลย!\n"
            "> ใช้ `/help [ชื่อคำสั่ง]` เพื่อดูคำอธิบายแบบละเอียด 💡"
        ),
        color=Color.from_rgb(47, 49, 54)  # เทาเข้มแบบ Discord
    )

    # ส่วนรายชื่อคำสั่ง
    if len(COMMANDS) == 0:
        embed.add_field(
            name="❌ ไม่พบคำสั่ง",
            value="ยังไม่มีคำสั่งในระบบ หรือเกิดข้อผิดพลาดขณะโหลดข้อมูล",
            inline=False
        )
    else:
        start = (page - 1) * COMMANDS_PER_PAGE
        end = start + COMMANDS_PER_PAGE
        page_commands = COMMANDS[start:end]
        
        for command in page_commands:
            # สร้างรายละเอียดของแต่ละคำสั่ง
            description = f'```{command["description"]}```'

            if len(command["args"]) > 0:
                args = [f'[{arg["name"]}]' for arg in command["args"]]
                arg_details = "\n".join(
                    [f'> 🧩 `{arg["name"]}` — {arg["description"]}' for arg in command["args"]]
                )
                description += (
                    f'\n> 💡 **ตัวอย่างการใช้งาน**\n> `{" ".join([command["name"]] + args)}`\n'
                    f'> **Arguments**\n{arg_details}'
                )

            embed.add_field(
                name=f':sparkles: {command["name"]}',
                value=description,
                inline=False
            )

    embed.set_footer(
        text=f"📘 Page {page} of {COMMANDS_PAGE}"
    )

    return embed


def register_help_command(client: Client, guild: Object):
    """
    Registers /help command to display command list for PSCP Bot
    """
    @client.tree.command(
        name="help",
        description="แสดงรายการคำสั่งทั้งหมดของ PSCP Bot",
        guild=guild
    )
    async def handle_help_command(interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        current_page = 1

        embed = create_help_embed(current_page)

        async def update_message(interaction: Interaction, page: int):
            """อัพเดท Embed เมื่อมีการกดปุ่ม"""
            embed = create_help_embed(page)
            view = create_pagination_view(page)
            await interaction.edit_original_response(embed=embed, view=view)

        def create_pagination_view(page):
            """
            สร้างกลุ่มสำหรับปุ่ม เลื่อนหน้า
            """
            view = View(timeout=180)

            # สร้างปุ่มย้อนกลับ
            prev_button = Button(
                label="⬅️ ก่อนหน้า",
                style=ButtonStyle.secondary,
                disabled=(page <= 1)
            )
            # สร้างปุ่มเลื่อนถัดไป
            next_button = Button(
                label="➡️ ถัดไป",
                style=ButtonStyle.secondary,
                disabled=(page >= COMMANDS_PAGE)
            )

            async def prev_callback(i: Interaction):
                nonlocal current_page  # เพื่อให้ฟังชั่นนี้ใช้ ตัวแปร current_page ของ function หลัก
                if i.user.id != interaction.user.id:
                    await i.response.send_message("❌ คุณไม่สามารถควบคุมหน้านี้ได้", ephemeral=True)
                    return
                current_page -= 1
                await i.response.defer()
                await update_message(i, current_page)

            async def next_callback(i: Interaction):
                nonlocal current_page  # เพื่อให้ฟังชั่นนี้ใช้ ตัวแปร current_page ของ function หลัก
                if i.user.id != interaction.user.id:
                    await i.response.send_message("❌ คุณไม่สามารถควบคุมหน้านี้ได้", ephemeral=True)
                    return
                current_page += 1
                await i.response.defer()
                await update_message(i, current_page)

            prev_button.callback = prev_callback
            next_button.callback = next_callback

            view.add_item(prev_button)
            view.add_item(next_button)
            return view

        view = create_pagination_view(current_page)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
