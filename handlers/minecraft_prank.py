import asyncio
import logging
import random

from minecraft_server import get_all_players


async def execute_random_prank(mcr, player):
    prank_num = random.randint(0, 27)
    phrases = ["На самом деле я Амир Елдашев", "Топоры говно", "Вот бы кого то убить... ", "Я хочу убить ",
               "Дам алмазов", "Я не люблю, когда волосатые мужики обмазываются маслом",
               "На самом деле это я мамочка амира юлдашбаева", "Я чурка я хач я чурка я хач",
               "Я люблю грязных потных женщин"]
    logging.info(f"Выпал пранк {prank_num + 1}")
    if prank_num in pranks:
        if prank_num == 14:
            await prank_14(mcr, player, phrases)
        if prank_num == 27:
            await prank_27(mcr, player, phrases)
        else:
            await pranks[prank_num](mcr, player)


async def send_title(mcr, message, target="@a"):
    mcr.command(f'title {target} title "{message}"')


async def summon_entity(mcr, prankplayer, entity, count=1):
    for _ in range(count):
        mcr.command(f'execute at {prankplayer} run summon {entity}')
        logging.info(f"execute at {prankplayer} run summon {entity}")
        await asyncio.sleep(0.1)


async def give_effects(mcr, prankplayer, effects):
    for effect, duration, amplifier in effects:
        mcr.command(f'effect give {prankplayer} minecraft:{effect} {duration} {amplifier}')


async def give_items(mcr, prankplayer, item, count):
    for _ in range(count):
        mcr.command(f'give {prankplayer} {item}')


async def prank_0(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:creeper', 3)


async def prank_1(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:zombie', 4)


async def prank_2(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:wither_skeleton', 2)


async def prank_3(mcr, prankplayer):
    mcr.command(f'execute at {prankplayer} run fill ~5 ~200 ~-5 ~-5 ~200 ~5 minecraft:zombie_wall_head')
    await asyncio.sleep(2)
    mcr.command(f'tp {prankplayer} ~ ~205 ~')


async def prank_4(mcr, prankplayer):
    await give_items(mcr, prankplayer, 'minecraft:white_dye 6400', 4)
    await asyncio.sleep(5)
    await send_title(mcr, "Он обосрался...")


async def prank_5(mcr, prankplayer):
    effects = [
        ('darkness', 300, 0),
        ('nausea', 300, 30),
        ('mining_fatigue', 300, 2),
        ('weakness', 300, 3),
        ('hunger', 300, 3),
        ('blindness', 300, 3)
    ]
    await give_effects(mcr, prankplayer, effects)
    await asyncio.sleep(5)
    await send_title(mcr, "Ить в тц...")


async def prank_6(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:evoker_fangs')


async def prank_7(mcr, prankplayer):
    evoker_entity = (
        'minecraft:magma_cube ~ ~1 ~ {Size:0,Passengers:[{id:"minecraft:evoker",'
        'CustomName:"\\"Амироголовый\\"",CustomNameVisible:1,Health:1,'
        'Attributes:[{Name:"generic.maxHealth",Base:1.0},{Name:"generic.movementSpeed",Base:10.0}],'
        'HandDropChances:[0.5F,2.0F],HandItems:[{id:"minecraft:kelp",Count:3},{}]}]}'
    )
    await summon_entity(mcr, prankplayer, evoker_entity, 2)


async def prank_8(mcr, prankplayer):
    turtle_entity = (
        'minecraft:turtle ~ ~1 ~ {CustomName:"\\"Хаю хай\\"",CustomNameVisible:1,'
        'Attributes:[{Name:"generic.movementSpeed",Base:10.0}],'
        'HandDropChances:[0.5F,2.0F],'
        'HandItems:[{id:"minecraft:kelp",Count:3},{}]}'
    )
    await summon_entity(mcr, prankplayer, turtle_entity, 10)


async def prank_9(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:shulker_bullet')


async def prank_10(mcr, prankplayer):
    await asyncio.sleep(5)
    await send_title(mcr, "Сегодня у него хороший день")
    await asyncio.sleep(1)
    await give_items(mcr, prankplayer, 'minecraft:apple', 1)


async def prank_11(mcr, prankplayer):
    mcr.command(f'kick {prankplayer} повезло повезло')
    await asyncio.sleep(5)
    await send_title(mcr, "Ниихт")


async def prank_12(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:end_crystal', 3)


async def prank_13(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:slime', 15)


async def prank_14(mcr, prankplayer, phrases):
    randomph = random.randint(0, len(phrases) - 1)
    players = await get_all_players()
    random_index = random.randint(0, len(players) - 1)
    random_player = players[random_index]
    if randomph in {2, 3}:
        message = f'<{prankplayer}> {phrases[randomph]} {random_player()}.'
    else:
        message = f'<{prankplayer}> {phrases[randomph]}.'
    mcr.command(f'tellraw @a {{"text":"{message}","color":"white"}}')


async def prank_15(mcr, prankplayer):
    sheep_entity = (
        'minecraft:magma_cube ~ ~1 ~ {Size:0,Passengers:[{id:"minecraft:sheep",'
        'CustomName:"\\"ачё\\"",CustomNameVisible:1,NoGravity:1b,Health:100,'
        'Attributes:[{Name:"generic.maxHealth",Base:100.0},{Name:"generic.movementSpeed",Base:10.0}],'
        'Color:6,HandDropChances:[0.5F,2.0F],'
        'HandItems:[{id:"minecraft:leather_boots",Count:64,tag:{display:{color:16746482}}},{}]}]}'
    )
    await summon_entity(mcr, prankplayer, sheep_entity, 2)


async def prank_16(mcr, prankplayer):
    goat_entity = (
        'minecraft:goat ~ ~1 ~ {CustomName:"\\"бронированный\\"",CustomNameVisible:1,NoGravity:1b,Health:100,'
        'Attributes:[{Name:"generic.maxHealth",Base:100.0},{Name:"generic.knockbackResistance",Base:0.6},{Name:"generic.movementSpeed",Base:10.0}],'
        'HandDropChances:[0.5F,2.0F],HandItems:[{id:"minecraft:wheat_seeds",Count:64},{}]}'
    )
    await summon_entity(mcr, prankplayer, goat_entity)


async def prank_17(mcr, prankplayer):
    jockey_entity = (
        'minecraft:chicken ~ ~1 ~ {IsChickenJockey:1,Passengers:[{id:"minecraft:zombie",IsBaby:1,'
        'Passengers:[{id:"minecraft:chicken",IsChickenJockey:1,Passengers:[{id:"minecraft:zombie",IsBaby:1,'
        'CustomName:"\\"НИКОГДА НИКОГДА\\"",CustomNameVisible:1,Attributes:[{Name:"generic.movementSpeed",Base:0.1}],'
        'ArmorItems:[{},{Count:2,id:"minecraft:apple"},{},{}],ArmorDropChances:[0.0F,0.7F,0.0F,0.0F]}]}]}]}'
    )
    await summon_entity(mcr, prankplayer, jockey_entity)


async def prank_18(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:witch', 2)


async def prank_19(mcr, prankplayer):
    mcr.command(f'execute at {prankplayer} run playsound minecraft:music_disc.5 ambient {prankplayer}')
    mcr.command(f'execute at {prankplayer} run playsound minecraft:music_disc.11 ambient {prankplayer}')
    mcr.command(f'execute at {prankplayer} run playsound minecraft:music_disc.13 ambient {prankplayer}')


async def prank_20(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:tadpole', 45)


async def prank_21(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:boat', 20)


async def prank_22(mcr, prankplayer):
    await summon_entity(mcr, prankplayer, 'minecraft:creeper ~ ~ ~ {powered:1}', 2)
    await asyncio.sleep(4)
    await send_title(mcr, "Любимчики")


async def prank_23(mcr, prankplayer):
    await asyncio.sleep(2)
    mcr.command(f'execute at {prankplayer} run fill ~0 ~1 ~0 ~0 ~1 ~0 minecraft:water')
    await send_title(mcr, "Огурчик Миши")
    await asyncio.sleep(2)


async def prank_24(mcr, prankplayer):
    squid_entity = (
        'minecraft:slime ~ ~1 ~ {Size:0,Passengers:[{id:"minecraft:squid",Glowing:1,'
        'Attributes:[{Name:"generic.knockbackResistance",Base:1.0},{Name:"generic.movementSpeed",Base:10.0}],'
        'Invulnerable:1,HandDropChances:[2.0F,2.0F],HandItems:[{},{id:"minecraft:dead_bush",Count:64}]}]}'
    )
    await summon_entity(mcr, prankplayer, squid_entity)


async def prank_25(mcr, prankplayer):
    snow_golem_entity = (
        'minecraft:snow_golem ~ ~1 ~ {Passengers:[{id:"minecraft:sheep",CustomName:"jeb_",CustomNameVisible:1,Glowing:1,NoGravity:1b,'
        'Attributes:[{Name:"generic.knockbackResistance",Base:1.0},{Name:"generic.movementSpeed",Base:10.0}],'
        'Invulnerable:1,HandDropChances:[2.0F,2.0F],HandItems:[{},{id:"minecraft:clock",Count:64}]}]}'
    )
    await summon_entity(mcr, prankplayer, snow_golem_entity)


async def prank_26(mcr, prankplayer):
    mcr.command(
        f'give {prankplayer} rabbit_spawn_egg{{EntityTag:{{id:"minecraft:rabbit",RabbitType:99,CustomName:"\"НИКОГДА НИКОГДА\"",CustomNameVisible:1,Attributes:[{{Name:"generic.movementSpeed",Base:0.1f}}],HandDropChances:[0.5F,2F],HandItems:[{{id:"minecraft:diamond",Count:3}},{{}}]}}}}')


async def prank_27(mcr, prankplayer, phrases):
    rando_mph = random.randint(0, len(phrases) - 1)
    phrase = phrases[rando_mph]
    command = f'give @a minecraft:written_book{{title:"Откровение",author:"{prankplayer}",pages:[\'{{"text":"{phrase}"}}\']}}'
    mcr.command(command)


pranks = {
    0: prank_0,
    1: prank_1,
    2: prank_2,
    3: prank_3,
    4: prank_4,
    5: prank_5,
    6: prank_6,
    7: prank_7,
    8: prank_8,
    9: prank_9,
    10: prank_10,
    11: prank_11,
    12: prank_12,
    13: prank_13,
    14: prank_14,
    15: prank_15,
    16: prank_16,
    17: prank_17,
    18: prank_18,
    19: prank_19,
    20: prank_20,
    21: prank_21,
    22: prank_22,
    23: prank_23,
    24: prank_24,
    25: prank_25,
    26: prank_26,
    27: prank_27
}
