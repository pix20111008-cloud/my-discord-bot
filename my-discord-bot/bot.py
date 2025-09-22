import os
import discord
from discord.ext import commands
import asyncio

# 環境変数からトークン取得
TOKEN = os.environ["DISCORD_TOKEN"]

# Intents の設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True  # メンバー情報取得に必要

# Bot 本体
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot 起動時のメッセージ
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

# ---------------------------------
# !purge_user <ユーザーID> <履歴上限>
# 特定ユーザーのメッセージ削除
# ---------------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge_user(ctx, user_id: int, limit: int = 500):
    deleted = 0
    async for msg in ctx.channel.history(limit=limit):
        if msg.author.id == user_id:
            try:
                await msg.delete()
                deleted += 1
                await asyncio.sleep(0.2)  # レート制限回避
            except discord.Forbidden:
                await ctx.send("権限がありません。")
                return
            except discord.HTTPException:
                pass
    await ctx.send(f"{deleted} 件のメッセージを削除しました。")

# ---------------------------------
# !purge_left <履歴上限>
# サーバーを抜けたユーザーのメッセージ削除
# ---------------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge_left(ctx, limit: int = 1000):
    deleted = 0
    # 現在のメンバーIDを取得
    member_ids = [member.id for member in ctx.guild.members]
    async for msg in ctx.channel.history(limit=limit):
        if msg.author.id not in member_ids:  # サーバーにいないユーザー
            try:
                await msg.delete()
                deleted += 1
                await asyncio.sleep(0.2)  # レート制限回避
            except discord.Forbidden:
                await ctx.send("権限がありません。")
                return
            except discord.HTTPException:
                pass
    await ctx.send(f"{deleted} 件のメッセージを削除しました（サーバーを抜けたユーザー）")

# エラーハンドリング
@purge_user.error
async def purge_user_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("このコマンドを使う権限がありません。")

@purge_left.error
async def purge_left_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("このコマンドを使う権限がありません。")

# Bot 起動
bot.run(TOKEN)
