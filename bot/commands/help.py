"""/help"""

import json
import math
from discord import (
    Client,
    Object,
    Interaction,
    Embed,
    Color,
    ButtonStyle,
    app_commands,
)
from discord.ui import View, Button

# =====================================================
# 🔧 CONFIGURATION
# =====================================================

COMMANDS_FILE = "data/commands.json"   # Path to commands list JSON
COMMANDS_PER_PAGE = 3                  # Number of commands shown per page


# =====================================================
# 📂 LOAD COMMAND LIST
# =====================================================

try:
    with open(COMMANDS_FILE, "r", encoding="utf-8") as file:
        COMMANDS = json.load(file)
        TOTAL_PAGES = max(1, math.ceil(len(COMMANDS) / COMMANDS_PER_PAGE))
except Exception as e:
    print("⚠️ Error loading commands list:", e)
    COMMANDS = []
    TOTAL_PAGES = 1


# =====================================================
# 🧱 EMBED CREATION
# =====================================================

def create_help_embed(page: int = 1, keyword: str = "") -> Embed:
    """
    Create a paginated Discord Embed showing a list of available bot commands.
    Supports optional keyword-based filtering.
    """
    filtered = COMMANDS

    # Apply search filter (case-insensitive)
    if keyword:
        key = keyword.lower()
        filtered = [
            cmd for cmd in COMMANDS
            if key in cmd["name"].lower() or key in cmd["description"].lower()
        ]

    # Create the main embed structure
    embed = Embed(
        title="🤖 PSCP Bot Command Center",
        description=(
            "> สงสัยว่าบอททำอะไรได้บ้าง? มาดูคำสั่งทั้งหมดที่คุณใช้ได้ที่นี่เลย!\n"
            "> ใช้ `/help [ชื่อคำสั่ง]` เพื่อดูคำอธิบายแบบละเอียด 💡"
        ),
        color=Color.from_rgb(47, 49, 54),
    )

    # Handle empty search result
    if not filtered:
        embed.add_field(
            name="❌ ไม่พบคำสั่งที่ค้นหา",
            value=(
                f"ไม่มีคำสั่งที่ตรงกับคำว่า `{keyword}`"
                if keyword else "ยังไม่มีคำสั่งในระบบ"
            ),
            inline=False,
        )
        embed.set_footer(text="📘 ไม่พบข้อมูล")
        return embed

    # Handle pagination logic
    total_pages = max(1, math.ceil(len(filtered) / COMMANDS_PER_PAGE))
    page = max(1, min(page, total_pages))

    start = (page - 1) * COMMANDS_PER_PAGE
    end = page * COMMANDS_PER_PAGE

    # Populate embed fields for each command on this page
    for cmd in filtered[start:end]:
        desc = f"```{cmd['description']}```"

        # Add command argument details if available
        if cmd.get("args"):
            args = [f"[{a['name']}]" for a in cmd["args"]]
            arg_info = "\n".join(
                f"> 🧩 `{a['name']}` — {a['description']}" for a in cmd["args"]
            )
            desc += (
                f"\n> 💡 **ตัวอย่างการใช้งาน**\n> "
                f"`{cmd['name']} {' '.join(args)}`\n"
                f"> **Arguments**\n{arg_info}"
            )

        embed.add_field(name=f"✨ {cmd['name']}", value=desc, inline=False)

    embed.set_footer(text=f"📘 Page {page} of {total_pages}")
    return embed


# =====================================================
# 🔄 PAGINATION VIEW (Previous / Next Buttons)
# =====================================================

def create_pagination_view(
    interaction: Interaction, current_page: int, keyword: str = ""
) -> View:
    """
    Create interactive buttons for navigating between help pages.
    Buttons are restricted so only the original command user can interact.
    """
    view = View(timeout=180)

    # Filter commands if searching
    key = keyword.lower() if keyword else None

    filtered = [
        cmd for cmd in COMMANDS
        if not key or key in cmd["name"].lower() or key in cmd["description"].lower()
    ]

    # Handle pagination logic
    total_pages = max(1, math.ceil(len(filtered) / COMMANDS_PER_PAGE))
    current_page = max(1, min(current_page, total_pages))

    # For loop for create pagination button
    for label, delta in [("⬅️ ก่อนหน้า", -1), ("➡️ ถัดไป", 1)]:
        async def callback(i, d=delta):
            """
            Handle When User interact with button
            """
            if i.user.id != interaction.user.id:
                await i.response.send_message("❌ คุณไม่สามารถควบคุมหน้านี้ได้", ephemeral=True)
                return
            new_page = max(1, min(current_page + d, total_pages))
            emb = create_help_embed(new_page, keyword)
            await i.response.edit_message(embed=emb, view=create_pagination_view(interaction, new_page, keyword))

        # Create Button
        btn = Button(
            label=label,
            style=ButtonStyle.secondary,
            disabled=(
                (current_page == 1 and delta == -1)
                or
                (current_page == total_pages and delta == 1)
            )
        )
        # Set Button Callback
        btn.callback = callback
        # Add Button to view
        view.add_item(btn)
    return view


# =====================================================
# 🧩 REGISTER HELP COMMAND
# =====================================================

def register_help_command(client: Client, guild: Object) -> None:
    """
    Register the /help command for the PSCP bot.
    Supports optional keyword search and page navigation.
    """

    @client.tree.command(
        name="help",
        description="แสดงรายการคำสั่งทั้งหมดของ PSCP Bot (หรือค้นหาคำสั่ง)",
        guild=guild,
    )
    @app_commands.describe(
        keyword="ระบุชื่อคำสั่งเพื่อค้นหา (เช่น random, pair, info)"
    )
    async def handle_help_command(
        interaction: Interaction,
        keyword: str = ""
    ) -> None:
        """Handles the /help command logic with pagination."""
        await interaction.response.defer(ephemeral=True)
        current_page = 1
        embed = create_help_embed(current_page, keyword)
        view = create_pagination_view(interaction, current_page, keyword)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
