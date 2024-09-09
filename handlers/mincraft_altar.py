import asyncio
import random

from aiogram import types
from mcrcon import MCRcon

from api_requests import get_player_username
from config import RCON_HOST, RCON_PASSWORD
from keyboards import altar_menu_keyboard
from minecraft_server import is_player_online, return_player_to_last_coordinate, gift_to_vladick
import re


async def show_altar_menu(message: types.Message):
    keyboard = altar_menu_keyboard()
    await message.answer(
        "Священный алтарь:",
        reply_markup=keyboard
    )


async def return_to_last_location(message: types.Message):
    user_id = message.from_user.id
    from handlers import show_action_menu
    if await is_player_online(user_id):
        await return_player_to_last_coordinate(user_id)
        await show_action_menu(message)
    else:
        await message.answer("Ты должен быть в сети")


async def donation(message: types.Message):
    user_id = message.from_user.id

    if not await is_player_online(user_id):
        await message.answer("Ты должен быть в сети...")

    nickname = await get_player_username(user_id)



    TOO_CHEAP_FOOD_COST = 0.5
    TREE_COST = 1
    CHEAP_FOOD_COST = 1
    MEAT_FISH_COST = 5
    FOOD = 10
    BEST_FOOD = 25
    IRON_COST = 25
    GOLD_COST = 25
    DISK_COST = 50
    DIAMOND_COST = 75
    HEAD_COST = 500
    NETHERITE_COST = 1000
    NETHER_STAR_COST = 10000

    badAnswer = [
        ' "[Владик] Не пытайся меня надурить. Я принимаю то, что вы отрываете от сердца. Достаточно понятно?"',
        ' "[Владик] Были бы у меня ноги, я бы дал тебе подзатыльник."',
        ' "[Владик] Время - самый важный ресурс даже среди богов. И прямо сейчас ты его благополучно просрал."',
        ' "[Владик] Я по натуре не злой, но выбешивают прямоходящие, пытающиеся бесстыдно потратить моё время. Что-нибудь покруче!"',
        ' "[Владик] В этот раз бумажки остаются при мне. Вытри слëзы и ищи дальше."',
        ' "[Владик] Да, я могу принять легкодобываемый ресурс, если он ценен. В этот раз мимо."',
        ' "[Владик] После такого я и твой мозг не приму.",'
        ' "[Владик] Неа. Оставь себе."',
        ' "[Владик] В такие моменты я молю, чтоб у меня самого был бог, к которому можно было бы сбежать и уткнуться в плечо."',
        ' "[Владик] Ить в тц, ить в тц, Миша псих. Современный сленг поражает. Ты Миша?"',
        ' "[Владик] Знаешь, у меня плохое настроение сегодня. Своим приношением ты меня уже повеселил, теперь повесели страданиями"']

    with MCRcon(RCON_HOST, RCON_PASSWORD) as mcr:
        await asyncio.sleep(0.5)
        output = mcr.command(' execute as ' + str(nickname) + ' run data get entity ' + str(nickname) + ' Pos')
        match = re.search(r"\[([\d.-]+)d, ([\d.-]+)d, ([\d.-]+)d\]", output)
        if match:
            x = int(float(match.group(1)))
            y = int(float(match.group(2)))
            z = int(float(match.group(3)))
        if x in range(-15, -12) and y == 286 and z in range(-12, -10):
            item = "minecraft:diamond"
            result = mcr.command('execute as ' + nickname + ' run clear ' + nickname + ' ' + item + ' 0')
            if result != "":
                await gift_to_vladick(result, DIAMOND_COST,
                                      ' "[Владик] Твоё подношение принято. С моей стороны насыпаю тебе пустышки смертных..."',
                                      item, nickname)
                return
            else:
                item = "minecraft:gold_ingot"
                result = mcr.command('execute as ' + nickname + ' run clear ' + nickname + ' ' + item + ' 0')
                if result != "":
                    await gift_to_vladick(result, GOLD_COST,
                                          ' "[Владик] Слыхал, драконы любят блеск этого металла. В нем явно можно утонуть.."',
                                          item, nickname)
                    return
                else:
                    item = "minecraft:iron_ingot"
                    result = mcr.command('execute as ' + nickname + ' run clear ' + nickname + ' ' + item + ' 0')
                    if result != "":
                        await gift_to_vladick(result, IRON_COST,
                                              ' "[Владик] Интересно, считают ли двуногие это съедобным. Раз готовы обменять на бумагу, то нет."',
                                              item, nickname)
                        return
                    else:
                        item = "minecraft:netherite_ingot"
                        result = mcr.command('execute as ' + nickname + ' run clear ' + nickname + ' ' + item + ' 0')
                        if result != "":
                            await gift_to_vladick(result, NETHERITE_COST,
                                                  ' "[Владик] Разве из этого земляне не делают самую крепкую броню? Да ты реально поехавший на деньгах!"',
                                                  item, nickname)
                            return
                        else:
                            item = ["minecraft:zombie_head", "minecraft:creeper_head", "minecraft:skeleton_skull",
                                    "minecraft:wither_skeleton_skull"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' + item[i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result, HEAD_COST,
                                                          ' "[Владик] Я надеюсь, ты лишил этого существа жизни не ради 500$."',
                                                          item[i], nickname)
                                    return
                            item = "minecraft:nether_star"
                            result = mcr.command(
                                'execute as ' + nickname + ' run clear ' + nickname + ' ' + item + ' 0')
                            if result != "":
                                await gift_to_vladick(result, NETHER_STAR_COST,
                                                      ' "[Владик] Я, честно сказать, поражен. Иссушитель, мы же с ним вместе в школе учились. А теперь он стал жертвой жадного до денег убийцы. Время не щадит никого..."',
                                                      item, nickname)
                                return
                            item = ["minecraft:oak_log", "minecraft:spruce_log",
                                    "minecraft:birch_log", "minecraft:jungle_log",
                                    "minecraft:acacia_log", "minecraft:dark_oak_log",
                                    "minecraft:mangrove_log"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' + item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result, TREE_COST,
                                                          ' "[Владик] Мне пытаются впарить это уже сотый раз за день. Забери деньги и проваливай!"',
                                                          item[i], nickname)
                                    return
                            item = ["minecraft:sweet_berries", "minecraft:glow_berries", "minecraft:wheat",
                                    "minecraft:beetroot"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' +
                                    item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result, CHEAP_FOOD_COST,
                                                          ' "[Владик] Порою мне льстит, что эти безмозглые антропосы фанатично несут мне всякие безделушки и, получая еще большие безделушки, прыгают от счастья. Ты ничем от них не отличаешься."',
                                                          item[i], nickname)
                                    return
                            item = ["minecraft:carrot", "minecraft:potato",
                                    "minecraft:melon", "minecraft:beetroot"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' +
                                    item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result, TOO_CHEAP_FOOD_COST,
                                                          ' "[Владик] Слышал цитату: "Деньги - воздух. Деньги портят людей. Я порчу воздух. Я мщу деньгам за человечество"? Все-таки, некоторые "хомо" из вашего вида заслуживают статуса "сапиенс"."',
                                                          item[i], nickname)
                                    return
                            item = ["minecraft:music_disc_13", "minecraft:music_disc_cat",
                                    "minecraft:music_disc_blocks", "minecraft:music_disc_chirp",
                                    "minecraft:music_disc_far", "minecraft:music_disc_mall",
                                    "minecraft:music_disc_mellohi", "minecraft:music_disc_stal",
                                    "minecraft:music_disc_strad", "minecraft:music_disc_ward",
                                    "minecraft:music_disc_11", "minecraft:music_disc_wait",
                                    "minecraft:music_disc_otherside", "minecraft:music_disc_5",
                                    "minecraft:music_disc_pigstep", "minecraft:disc_fragment_5"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' +
                                    item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result, DISK_COST,
                                                          ' "[Владик] Интересная вещица. Ты заслужил земную валюту..."',
                                                          item[i], nickname)
                                    return
                            item = ["minecraft:beef",
                                    "minecraft:porkchop",
                                    "minecraft:mutton",
                                    "minecraft:chicken",
                                    "minecraft:cod",
                                    "minecraft:salmon",
                                    "minecraft:tropical_fish"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' +
                                    item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result,
                                                          MEAT_FISH_COST,
                                                          ' "[Владик] Мне это явно нужнее, чем тебе. Таким, как ты, для жизни достаточно крашеной древесной коры"',
                                                          item[i], nickname)
                                    return
                            item = ["minecraft:cooked_beef",
                                    "minecraft:cooked_porkchop",
                                    "minecraft:cooked_mutton",
                                    "minecraft:cooked_chicken",
                                    "minecraft:cooked_rabbit",
                                    "minecraft:cooked_cod",
                                    "minecraft:cooked_salmon",
                                    "minecraft:bread",
                                    "minecraft:cookie"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' +
                                    item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result,
                                                          FOOD,
                                                          ' "[Владик] Твоё подношение принято. Позволяю тебе насытиться пустышками смертных."',
                                                          item[i],
                                                          nickname)
                                    return
                            item = ["minecraft:golden_apple",
                                    "minecraft:enchanted_golden_apple",
                                    "minecraft:cake",
                                    "minecraft:pumpkin_pie",
                                    "minecraft:golden_carrot"]
                            for i in range(0, len(item)):
                                result = mcr.command(
                                    'execute as ' + nickname + ' run clear ' + nickname + ' ' +
                                    item[
                                        i] + ' 0')
                                if result != "":
                                    await gift_to_vladick(result,
                                                          BEST_FOOD,
                                                          ' "[Владик] Твоё подношение принято. Позволяю тебе насытиться пустышками смертных."',
                                                          item[i],
                                                          nickname)
                                    return
                            item = "minecraft:rotten_flesh"
                            result = mcr.command(
                                'execute as ' + nickname + ' run clear ' + nickname + ' ' + item + ' 0')
                            if result != "":
                                text = ' "[Владик] Когда ты сам будешь гнить в земле, я позабочусь о том, чтоб твои останки также не оставляли в покое."'
                                mcr.command('tellraw ' + nickname + text)
                                mcr.command('effect give ' + nickname + ' minecraft:hunger 300')
                                mcr.command('clear ' + nickname + ' ' + item)
                                return
                            else:
                                item = [
                                    "minecraft:grass_block",
                                    "minecraft:dirt",
                                    "minecraft:coarse_dirt",
                                    "minecraft:podzol",
                                    "minecraft:rooted_dirt",
                                    "minecraft:mud",
                                    "minecraft:cobblestone",
                                    "minecraft:sand",
                                    "minecraft:red_sand",
                                    "minecraft:stone",
                                    "minecraft:granite",
                                    "minecraft:diorite",
                                    "minecraft:andesite",
                                    "minecraft:deepslate",
                                    "minecraft:calcite",
                                    "minecraft:tuff"]
                                for i in range(0, len(item)):
                                    result = mcr.command(
                                        'execute as ' + nickname + ' run clear ' + nickname + ' ' + item[i] + ' 0')
                                    if result != "":
                                        text = random.choice(badAnswer)
                                        mcr.command('tellraw ' + nickname + text)
                                        random_number = random.randint(0, 5)
                                        if random_number == 0:
                                            mcr.command(
                                                'effect give ' + nickname + ' minecraft:darkness 300')
                                        if random_number == 1:
                                            mcr.command(
                                                'effect give ' + nickname + ' minecraft:nausea 300 30')
                                        if random_number == 2:
                                            mcr.command(
                                                'effect give ' + nickname + ' minecraft:mining_fatigue 300 2')
                                        if random_number == 3:
                                            mcr.command(
                                                'effect give ' + nickname + ' minecraft:weakness 300 3')
                                        if random_number == 4:
                                            mcr.command(
                                                'effect give ' + nickname + ' minecraft:hunger 300 3')
                                        if random_number == 5:
                                            mcr.command(
                                                'effect give ' + nickname + ' minecraft:blindness 300 3')
                                        mcr.command(
                                            'clear ' + nickname + ' ' + item[i])
                                        return
                                num = random.choice([i for i in range(10) if i not in [0, 1, 5]])
                                mcr.command('tellraw ' + nickname + badAnswer[num])
                                random_number = random.randint(
                                    0, 5)
                                if random_number == 0:
                                    mcr.command(
                                        'effect give ' + nickname + ' minecraft:darkness 30')
                                if random_number == 1:
                                    mcr.command(
                                        'effect give ' + nickname + ' minecraft:nausea 30 30')
                                if random_number == 2:
                                    mcr.command(
                                        'effect give ' + nickname + ' minecraft:mining_fatigue 30 2')
                                if random_number == 3:
                                    mcr.command(
                                        'effect give ' + nickname + ' minecraft:weakness 30 3')
                                if random_number == 4:
                                    mcr.command(
                                        'effect give ' + nickname + ' minecraft:hunger 30 3')
                                if random_number == 5:
                                    mcr.command(
                                        'effect give ' + nickname + ' minecraft:blindness 30 3')
                                return
        else:
            await message.answer("Ты не в подходящем месте...")
