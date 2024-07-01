import discord
import json
import argparse
import asyncio

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True

client = discord.Client(intents=intents)

async def export_data(file_name):
    all_data = {}
    
    for guild in client.guilds:
        guild_data = {
            "id": guild.id,
            "name": guild.name,
            "description": guild.description,
            "roles": {role.name: role.id for role in guild.roles if role.name != "@everyone"},
            "channels": {}
        }
        
        for category in guild.categories:
            category_channels = {}
            for channel in category.channels:
                if 'ticket' not in channel.name.lower() and 'closed' not in channel.name.lower():
                    category_channels[channel.name] = channel.id
            if category_channels:
                guild_data["channels"][category.name] = category_channels
        
        all_data[guild.id] = guild_data

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f'Информация о сервере сохранена в {file_name}')
    await client.close()

async def import_data(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for guild_id, guild_data in data.items():
            guild = discord.utils.get(client.guilds, id=int(guild_id))
            if guild:
                print(f'Найден сервер: {guild.name}')
                # Установить описание сервера, если оно изменилось
                if guild.description != guild_data["description"]:
                    await guild.edit(description=guild_data["description"])
                    print(f'Обновлено описание сервера для {guild.name}')

                # Обновить роли
                for role_name, role_id in guild_data["roles"].items():
                    role = discord.utils.get(guild.roles, id=int(role_id))
                    if role and role.name != role_name:
                        try:
                            await role.edit(name=role_name)
                            print(f'Изменено имя роли: {role.name} на {role_name}')
                        except discord.errors.Forbidden:
                            print(f'Невозможно изменить роль {role.name}: нет прав')
                    elif not role:
                        print(f'Роль с ID {role_id} не найдена')

                # Обновить каналы
                for category_name, channels in guild_data["channels"].items():
                    category = discord.utils.get(guild.categories, name=category_name)
                    if category:
                        for channel_name, channel_id in channels.items():
                            channel = discord.utils.get(guild.channels, id=int(channel_id))
                            if channel and channel.name != channel_name:
                                try:
                                    await channel.edit(name=channel_name)
                                    print(f'Изменено имя канала: {channel.name} на {channel_name}')
                                except discord.errors.Forbidden:
                                    print(f'Невозможно изменить канал {channel.name}: нет прав')
                            elif not channel:
                                print(f'Канал с ID {channel_id} не найден')
                    else:
                        print(f'Категория {category_name} не найдена')
            else:
                print(f'Сервер с ID {guild_id} не найден')
    except Exception as e:
        print(f'Произошла ошибка: {e}')
    await client.close()

@client.event
async def on_ready():
    print(f'{client.user}')
    if args.mode == 'export':
        asyncio.create_task(export_data(args.file))
    elif args.mode == 'import':
        asyncio.create_task(import_data(args.file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Экспорт или импорт информации о сервере Discord.')
    parser.add_argument('mode', choices=['export', 'import'], help='Режим работы: экспорт или импорт данных о сервере')
    parser.add_argument('file', help='Файл для экспорта или импорта')
    args = parser.parse_args()

    token = ''  # Замените на токен вашего бота
    client.run(token)
