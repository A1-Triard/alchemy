from collections import namedtuple
from itertools import chain, product, combinations, count
import os, sys, shutil
from datetime import datetime
from time import mktime
from os import path, chdir, utime, remove, mkdir
from sys import stdout, stderr
import yaml
import subprocess
from subprocess import PIPE
import winreg
from winreg import HKEY_LOCAL_MACHINE, HKEY_CLASSES_ROOT
from shutil import copyfile, move, rmtree, copytree
import re

negative_effects = [
    'Burden',
    'FireDamage',
    'ShockDamage',
    'FrostDamage',
    'DrainAttribute',
    'DrainHealth',
    'DrainSpellpoints',
    'DrainFatigue',
    'DrainSkill',
    'DamageAttribute',
    'DamageHealth',
    'DamageMagicka',
    'DamageFatigue',
    'DamageSkill',
    'Poison',
    'WeaknessToFire',
    'WeaknessToFrost',
    'WeaknessToShock',
    'WeaknessToMagicka',
    'WeaknessToCommonDisease',
    'WeaknessToBlightDisease',
    'WeaknessToCorprusDisease',
    'WeaknessToPoison',
    'WeaknessToNormalWeapons',
    'DisintegrateWeapon',
    'DisintegrateArmor',
    'Paralyze',
    'Silence',
    'Blind',
    'Sound',
    'StuntedMagicka',
]

Potion2 = namedtuple('Potion2', ['id_1', 'id_base', 'difficulty'])
Potion5 = namedtuple('Potion5', ['id_broken_1', 'id_cheap_1', 'id_standard_1', 'id_qualitative_1', 'id_exclusive_1', 'id_base'])

Kind = namedtuple('Kind', ['name', 'effect', 'potion'])

kinds = [
    Kind('RestoreHealth', 'RestoreHealth', Potion5('p_restore_health_b', 'p_restore_health_c', 'p_restore_health_s', 'p_restore_health_q', 'p_restore_health_e', 'restore_health')),
    Kind('RestoreFatig', 'RestoreFatigue', Potion5('p_restore_fatigue_b', 'p_restore_fatigue_c', 'p_restore_fatigue_s', 'p_restore_fatigue_q', 'p_restore_fatigue_e', 'restore_fatigue')),
    Kind('RestoreMagic', 'RestoreSpellPoints', Potion5('p_restore_magicka_b', 'p_restore_magicka_c', 'p_restore_magicka_s', 'p_restore_magicka_q', 'p_restore_magicka_e', 'restore_magicka')),
    Kind('WaterWalk', 'WaterWalking', Potion5('p_water_walking_b', 'p_water_walking_c', 'p_water_walking_s', 'p_water_walking_q', 'p_water_walking_e', 'water_walking')),
    Kind('WaterBrf', 'WaterBreathing', Potion5('p_water_breathing_b', 'p_water_breathing_c', 'p_water_breathing_s', 'p_water_breathing_q', 'p_water_breathing_e', 'water_breathing')),
    Kind('Levitate', 'Levitate', Potion5('p_levitation_b', 'p_levitation_c', 'p_levitation_s', 'P_Levitation_Q', 'p_levitation_e', 'levitation')),
    Kind('Tele', 'Telekinesis', Potion5('p_telekinesis_b', 'p_telekinesis_c', 'p_telekinesis_s', 'p_telekinesis_q', 'p_telekinesis_e', 'telekinesis')),
    Kind('Blight', 'CureBlightDisease', Potion2('p_cure_blight_s', 'cure_blight', 200)),
    Kind('Cure', 'CureCommonDisease', Potion2('p_cure_common_s', 'cure_common', 400)),
    Kind('DetKey', 'DetectKey', Potion5('p_detect_key_b', 'p_detect_key_c', 'p_detect_key_s', 'p_detect_key_q', 'p_detect_key_e', 'detect_key')),
    Kind('Poison', 'CurePoison', Potion2('p_cure_poison_s', 'cure_poison', 400)),
    Kind('Feather', 'Feather', Potion5('p_feather_b', 'p_feather_c', 'p_feather_s', 'p_feather_q', 'p_feather_e', 'feather')),
    Kind('FireResist', 'ResistFire', Potion5('p_fire_resistance_b', 'p_fire_resistance_c', '"p_fire resistance_s"', 'p_fire_resistance_q', 'p_fire_resistance_e', 'fire_resistance')),
    Kind('RestPers', ('RestoreAttribute', 'Personality'), Potion5('p_restore_personality_b', 'p_restore_personality_c', 'p_restore_personality_s', 'p_restore_personality_q', 'p_restore_personality_e', 'restore_personality')),
    Kind('FortMagic', 'FortifySpellpoints', Potion5('p_fortify_magicka_b', 'p_fortify_magicka_c', 'p_fortify_magicka_s', 'p_fortify_magicka_q', 'p_fortify_magicka_e', 'fortify_magicka')),
    Kind('NightEye', 'NightEye', Potion5('"p_night-eye_b"', '"p_night-eye_c"', '"p_night-eye_s"', '"p_night-eye_q"', '"p_night-eye_e"', 'night-eye')),
    Kind('DetCreature', 'DetectAnimal', Potion5('p_detect_creatures_b', 'p_detect_creatures_c', 'p_detect_creatures_s', 'p_detect_creatures_q', 'p_detect_creatures_e', 'detect_creatures')),
    Kind('Para', 'CureParalyzation', Potion2('p_cure_paralyzation_s', 'cure_paralyzation', 400)),
    Kind('DetEnch', 'DetectEnchantment', Potion5('p_detect_enchantment_b', 'p_detect_enchantment_c', 'p_detect_enchantment_s', 'p_detect_enchantment_q', 'p_detect_enchantment_e', 'detect_enchantment')),
    Kind('Dispel', 'Dispel', Potion5('p_dispel_b', 'p_dispel_c', 'p_dispel_s', 'p_dispel_q', 'p_dispel_e', 'dispel')),
    Kind('FireSh', 'FireShield', Potion5('p_fire_shield_b', 'p_fire_shield_c', 'p_fire_shield_s', 'p_fire_shield_q', 'p_fire_shield_e', 'fire_shield')),
    Kind('FortAgil', ('FortifyAttribute', 'Agility'), Potion5('p_fortify_agility_b', 'p_fortify_agility_c', 'p_fortify_agility_s', 'p_fortify_agility_q', 'p_fortify_agility_e', 'fortify_agility')),
    Kind('FortAttack', 'FortifyAttackBonus', Potion5('p_fortify_attack_b', 'p_fortify_attack_c', 'p_fortify_attack_s', 'p_fortify_attack_q', 'p_fortify_attack_e', 'fortify_attack')),
    Kind('FortEndur', ('FortifyAttribute', 'Endurance'), Potion5('p_fortify_endurance_b', 'p_fortify_endurance_c', 'p_fortify_endurance_s', 'p_fortify_endurance_q', 'p_fortify_endurance_e', 'fortify_endurance')),
    Kind('FortFatig', 'FortifyFatigue', Potion5('p_fortify_fatigue_b', 'p_fortify_fatigue_c', 'p_fortify_fatigue_s', 'p_fortify_fatigue_q', 'p_fortify_fatigue_e', 'fortify_fatigue')),
    Kind('FortHealth', 'FortifyHealth', Potion5('p_fortify_health_b', 'p_fortify_health_c', 'p_fortify_health_s', 'p_fortify_health_q', 'p_fortify_health_e', 'fortify_health')),
    Kind('FortIntel', ('FortifyAttribute', 'Intellegence'), Potion5('p_fortify_intelligence_b', 'p_fortify_intelligence_c', 'p_fortify_intelligence_s', 'p_fortify_intelligence_q', 'p_fortify_intelligence_e', 'fortify_intelligence')),
    Kind('FortLuck', ('FortifyAttribute', 'Luck'), Potion5('p_fortify_luck_b', 'p_fortify_luck_c', 'p_fortify_luck_s', 'p_fortify_luck_q', 'p_fortify_luck_e', 'fortify_luck')),
    Kind('FortPers', ('FortifyAttribute', 'Personality'), Potion5('p_fortify_personality_b', 'p_fortify_personality_c', 'p_fortify_personality_s', 'p_fortify_personality_q', 'p_fortify_personality_e', 'fortify_personality')),
    Kind('FortSpeed', ('FortifyAttribute', 'Speed'), Potion5('p_fortify_speed_b', 'p_fortify_speed_c', 'p_fortify_speed_s', 'p_fortify_speed_q', 'p_fortify_speed_e', 'fortify_speed')),
    Kind('FortStr', ('FortifyAttribute', 'Strength'), Potion5('p_fortify_strength_b', 'p_fortify_strength_c', 'p_fortify_strength_s', 'p_fortify_strength_q', 'p_fortify_strength_e', 'fortify_strength')),
    Kind('FortWill', ('FortifyAttribute', 'Willpower'), Potion5('p_fortify_willpower_b', 'p_fortify_willpower_c', 'p_fortify_willpower_s', 'p_fortify_willpower_q', 'p_fortify_willpower_e', 'fortify_willpower')),
    Kind('FrostResist', 'ResistFrost', Potion5('p_frost_resistance_b', 'p_frost_resistance_c', 'p_frost_resistance_s', 'p_frost_resistance_q', 'p_frost_resistance_e', 'frost_resistance')),
    Kind('FrostSh', 'FrostShield', Potion5('p_frost_shield_b', 'p_frost_shield_c', 'p_frost_shield_s', 'p_frost_shield_q', 'p_frost_shield_e', 'frost_shield')),
    Kind('Invis', 'Invisibility', Potion5('p_invisibility_b', 'p_invisibility_c', 'p_invisibility_s', 'p_invisibility_q', 'p_invisibility_e', 'invisibility')),
    Kind('LightSh', 'LightningShield', Potion5('"p_lightning shield_b"', '"p_lightning shield_c"', '"p_lightning shield_s"', '"p_lightning shield_q"', '"p_lightning shield_e"', 'lightning_shield')),
    Kind('MagicResist', 'ResistMagicka', Potion5('p_magicka_resistance_b', 'p_magicka_resistance_c', 'p_magicka_resistance_s', 'p_magicka_resistance_q', 'p_magicka_resistance_e', 'magicka_resistance')),
    Kind('PoisonResist', 'ResistPoison', Potion5('p_poison_resistance_b', 'p_poison_resistance_c', 'p_poison_resistance_s', 'p_poison_resistance_q', 'p_poison_resistance_e', 'poison_resistance')),
    Kind('Reflect', 'Reflect', Potion5('p_reflection_b', 'p_reflection_c', 'p_reflection_s', 'p_reflection_q', 'p_reflection_e', 'reflection')),
    Kind('RestoreAgility', ('RestoreAttribute', 'Agility'), Potion5('p_restore_agility_b', 'p_restore_agility_c', 'p_restore_agility_s', 'p_restore_agility_q', 'p_restore_agility_e', 'restore_agility')),
    Kind('RestoreEndur', ('RestoreAttribute', 'Endurance'), Potion5('p_restore_endurance_b', 'p_restore_endurance_c', 'p_restore_endurance_s', 'p_restore_endurance_q', 'p_restore_endurance_e', 'restore_endurance')),
    Kind('RestoreIntel', ('RestoreAttribute', 'Intellegence'), Potion5('p_restore_intelligence_b', 'p_restore_intelligence_c', 'p_restore_intelligence_s', 'p_restore_intelligence_q', 'p_restore_intelligence_e', 'restore_intelligence')),
    Kind('RestoreLuck', ('RestoreAttribute', 'Luck'), Potion5('p_restore_luck_b', 'p_restore_luck_c', 'p_restore_luck_s', 'p_restore_luck_q', 'p_restore_luck_e', 'restore_luck')),
    Kind('RestoreSpeed', ('RestoreAttribute', 'Speed'), Potion5('p_restore_speed_b', 'p_restore_speed_c', 'p_restore_speed_s', 'p_restore_speed_q', 'p_restore_speed_e', 'restore_speed')),
    Kind('RestoreStr', ('RestoreAttribute', 'Strength'), Potion5('p_restore_strength_b', 'p_restore_strength_c', 'p_restore_strength_s', 'p_restore_strength_q', 'p_restore_strength_e', 'restore_strength')),
    Kind('RestoreWill', ('RestoreAttribute', 'Willpower'), Potion5('p_restore_willpower_b', 'p_restore_willpower_c', 'p_restore_willpower_s', 'p_restore_willpower_q', 'p_restore_willpower_e', 'restore_willpower')),
    Kind('SpellAbs', 'SpellAbsorption', Potion5('p_spell_absorption_b', 'p_spell_absorption_c', 'p_spell_absorption_s', 'p_spell_absorption_q', 'p_spell_absorption_e', 'spell_absorption')),
    Kind('SwitfSwim', 'SwiftSwim', Potion5('p_swift_swim_b', 'p_swift_swim_c', 'p_swift_swim_s', 'p_swift_swim_q', 'p_swift_swim_e', 'swift_swim')),
    Kind('Mark', 'Mark', Potion2('p_mark_s', 'mark', 400)),
    Kind('Recall', 'Recall', Potion2('p_recall_s', 'recall', 100)),
    Kind('ResCom', 'ResistCommonDisease', Potion5('p_disease_resistance_b', 'p_disease_resistance_c', 'p_disease_resistance_s', 'p_disease_resistance_q', 'p_disease_resistance_e', 'disease_resistance')),
    Kind('Shield', 'Shield', Potion5('p_silence_b', 'p_silence_c', 'p_silence_s', 'p_silence_q', 'p_silence_e', 'silence')),
    Kind('Jump', 'Jump', Potion5('p_jump_b', 'p_jump_c', 'p_jump_s', 'p_jump_q', 'p_jump_e', 'jump')),
    Kind('SlowFall', 'SlowFall', Potion5('p_slowfall_b', 'p_slowfall_c', 'p_slowfall_s', 'p_slowfall_q', 'p_slowfall_e', 'slowfall')),
    Kind('Chameleon', 'Chameleon', Potion5('p_chameleon_b', 'p_chameleon_c', 'p_chameleon_s', 'p_chameleon_q', 'p_chameleon_e', 'chameleon')),
    Kind('Light', 'Light', Potion5('p_light_b', 'p_light_c', 'p_light_s', 'p_light_q', 'p_light_e', 'light')),
    Kind('Sanctuary', 'Sanctuary', Potion5('p_sanctuary_b', 'p_sanctuary_c', 'p_sanctuary_s', 'p_sanctuary_q', 'p_sanctuary_e', 'sanctuary')),
    Kind('AInt', 'AlmsiviIntervention', Potion2('p_almsivi_intervention_s', 'almsivi_intervention', 100)),
    Kind('FortMult', 'FortifyMagickaMultiplier', None),
    Kind('ResShock', 'ResistShock', Potion5('p_shock_resistance_b', 'p_shock_resistance_c', 'p_shock_resistance_s', 'p_shock_resistance_q', 'p_shock_resistance_e', 'shock_resistance')),
    Kind('ResBlight', 'ResistBlightDisease', Potion5('p_blight_resistance_b', 'p_blight_resistance_c', 'p_blight_resistance_s', 'p_blight_resistance_q', 'p_blight_resistance_e', 'blight_resistance')),
    Kind('ResCorpr', 'ResistCorprusDisease', None),
    Kind('ResWeap', 'ResistNormalWeapons', Potion5('p_burden_b', 'p_burden_c', 'p_burden_s', 'p_burden_q', 'p_burden_e', 'burden')),
    Kind('ResPara', 'ResistParalysis', Potion5('p_paralyze_b', 'p_paralyze_c', 'p_paralyze_s', 'p_paralyze_q', 'p_paralyze_e', 'paralyze')),
    Kind('Uncurse', 'RemoveCurse', None),
    Kind('Scamp', 'SummonScamp', None),
    Kind('Clfear', 'SummonClannfear', None),
    Kind('WingTw', 'SummonWingedTwilight', None),
    Kind('Corpus', 'Corpus', None),
    Kind('Vampir', 'Vampirism', None),
    Kind('SkBlock', ('FortifySkill', 'Block'), None),
    Kind('SkArmorer', ('FortifySkill', 'Armorer'), None),
    Kind('SkMeArmor', ('FortifySkill', 'MediumArmor'), None),
    Kind('SkHeArmor', ('FortifySkill', 'HeavyArmor'), None),
    Kind('SkBlWeapon', ('FortifySkill', 'BluntWeapon'), None),
    Kind('SkLongBlade', ('FortifySkill', 'LongBlade'), None),
    Kind('SkAxe', ('FortifySkill', 'Axe'), None),
    Kind('SkSpear', ('FortifySkill', 'Spear'), None),
    Kind('SkAthletics', ('FortifySkill', 'Athletics'), None),
    Kind('SkEnchant', ('FortifySkill', 'Enchant'), None),
    Kind('SkDestruc', ('FortifySkill', 'Destruction'), None),
    Kind('SkAltera', ('FortifySkill', 'Alteration'), None),
    Kind('SkIllusion', ('FortifySkill', 'Illusion'), None),
    Kind('SkConjura', ('FortifySkill', 'Conjuration'), None),
    Kind('SkMysticism', ('FortifySkill', 'Mysticism'), None),
    Kind('SkRestora', ('FortifySkill', 'Restoration'), None),
    Kind('SkAlchemy', ('FortifySkill', 'Alchemy'), None),
    Kind('SkUnarmored', ('FortifySkill', 'Unarmored'), None),
    Kind('SkSecurity', ('FortifySkill', 'Security'), None),
    Kind('SkSneak', ('FortifySkill', 'Sneak'), None),
    Kind('SkAcrob', ('FortifySkill', 'Acrobatics'), None),
    Kind('SkLiArmor', ('FortifySkill', 'LightArmor'), None),
    Kind('SkShBlade', ('FortifySkill', 'ShortBlade'), None),
    Kind('SkMarksman', ('FortifySkill', 'Marksman'), None),
    Kind('SkMercant', ('FortifySkill', 'Mercantile'), None),
    Kind('SkSpeech', ('FortifySkill', 'Speechcraft'), None),
    Kind('SkHand', ('FortifySkill', 'HandToHand'), None),
    Kind('Sphere', 'SummonCenturionSphere', Potion5('p_summon_centurion_sphere_b', 'p_summon_centurion_sphere_c', 'p_summon_centurion_sphere_s', 'p_summon_centurion_sphere_q', 'p_summon_centurion_sphere_e', 'smn_centurion_sphere')),
]

positive_effects = list(map(lambda x: x.effect if isinstance(x.effect, str) else x.effect[0], kinds))

def effect_value(effect):
    effect = effect if isinstance(effect, str) else effect[0]
    if effect in negative_effects:
        return -1
    if effect in positive_effects:
        return 1
    print('unknown effect ' + str(effect))
    sys.exit(1)

Ingredient = namedtuple('Ingredient', ['name', 'modl', 'itex', 'effects'])

def ingr_level(ingr, kind):
    if kind.effect == ingr.effects[0]:
        return 15
    if kind.effect == ingr.effects[1]:
        return 30
    if kind.effect == ingr.effects[2]:
        return 45
    if kind.effect == ingr.effects[3]:
        return 60
    return None

def same_ingr(ingr1, ingr2):
    return ingr1.modl == ingr2.modl and not list(filter(lambda x: x[0] != x[1], zip(ingr1.effects, ingr2.effects)))

def load_ingredient_effect(index, attribute, skill):
    if index == 'FortifyAttribute' or index == 'RestoreAttribute' or index == 'DamageAttribute' or index == 'DrainAttribute':
        return (index, attribute)
    if index == 'FortifySkill' or index == 'DrainSkill':
        return (index, skill)
    return index
    
def load_ingredients(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        for record in data:
            ingr = {}
            for field in record['INGR']:
                ingr.update(field)
            if ingr.get('SCRI') is not None:
                continue
            name = ingr['NAME']
            modl = ingr['MODL']
            itex = ingr['ITEX']
            effects_data = ingr['IRDT']
            effect_1 = load_ingredient_effect(effects_data['effect_1_index'], effects_data['effect_1_attribute'], effects_data['effect_1_skill'])
            effect_2 = load_ingredient_effect(effects_data['effect_2_index'], effects_data['effect_2_attribute'], effects_data['effect_2_skill'])
            effect_3 = load_ingredient_effect(effects_data['effect_3_index'], effects_data['effect_3_attribute'], effects_data['effect_3_skill'])
            effect_4 = load_ingredient_effect(effects_data['effect_4_index'], effects_data['effect_4_attribute'], effects_data['effect_4_skill'])
            yield Ingredient(name, modl, itex, [effect_1, effect_2, effect_3, effect_4])

def same_group(ingr1, ingr2, kind, level):
    return same_ingr(ingr1, ingr2) or level is not None and ingr_level(ingr1, kind) < level and ingr_level(ingr2, kind) < level or list(filter(lambda x: x[0] == x[1] and x[0] != None and effect_value(x[0]) < 0, product(ingr1.effects, ingr2.effects)))

def pair_level(pair, kind):
    l1 = ingr_level(pair[0], kind)
    l2 = ingr_level(pair[1], kind)
    if l1 < l2:
        return l2
    else:
        return l1

def filter_and_group_ingredients(ingrs, kind, level):
    ingrs = list(filter(lambda i: ingr_level(i, kind) is not None and (level is None or ingr_level(i, kind) <= level), ingrs))
    links = list(map(lambda i: set([i]), range(0, len(ingrs))))
    for pair in filter(lambda pair: same_group(ingrs[pair[0]], ingrs[pair[1]], kind, level), combinations(range(0, len(ingrs)), 2)):
        group = links[pair[0]] | links[pair[1]]
        links[pair[0]] = group
        links[pair[1]] = group
    groups = []
    for i in range(0, len(ingrs)):
        group = list(filter(lambda g: i in links[g[0]], groups))
        if group:
            group[0].append(i)
        else:
            groups.append([i])
    groups.sort(key=len, reverse=True)
    special_pairs = list(chain.from_iterable(map(lambda group: filter(lambda pair: not same_group(ingrs[pair[0]], ingrs[pair[1]], kind, level), combinations(group, 2)), groups)))
    if len(groups) < 2:
        groups = []
    elif len(groups) == 2 and len(groups[0]) == 1 and len(groups[1]) == 1:
        special_pairs.append((groups[0][0], groups[1][0]))
        groups = []
    return (
        list(map(lambda g: list(sorted(map(lambda i: ingrs[i], g), key=lambda i: ingr_level(i, kind))), groups)),
        list(sorted(map(lambda s: (ingrs[s[0]], ingrs[s[1]]), special_pairs), key=lambda p: pair_level(p, kind)))
    )

def ingrs_empty(ingrs):
    (groups, pairs) = ingrs
    return len(groups) < 2 and not pairs

def ingrs_equals(ingrs1,ingrs2):
    (groups1, pairs1) = ingrs1
    (groups2, pairs2) = ingrs2
    if len(groups1) != len(groups2) or len(pairs1) != len(pairs2):
        return False
    for (g1, g2) in zip(groups1, groups2):
        if len(g1) != len(g2):
            return False
        for (i1, i2) in zip(g1, g2):
            if i1.name != i2.name:
                return False
    for (p1, p2) in zip(pairs1, pairs2):
        if p1[0].name != p2[0].name or p1[1].name != p2[1].name:
            return False
    return True

def groups_has_ingrs_with_level(groups, level, kind):
    if not list(filter(lambda i: ingr_level(i, kind) == level, chain.from_iterable(groups))):
        return False
    return True

def groups_filter_level(groups, level, kind):
    if not list(filter(lambda g: list(filter(lambda i: ingr_level(i, kind) == level, g)), groups)):
        return []
    groups = list(filter(lambda g: g, map(lambda g: list(filter(lambda i: ingr_level(i, kind) <= level, g)), groups)))
    return [] if len(groups) < 2 else groups

def pairs_filter_level(pairs, level, kind):
    return list(filter(lambda p: pair_level(p, kind) == level, pairs))

def gen_script(name, lines):
    return {
        'SCPT': [
            {'SCHD': {
                'name': name,
                'vars': {'shorts': 0, 'longs': 0, 'floats': 0},
                'data_size': 0,
                'var_table_size': 0
            }},
            {'SCTX': lines}
        ]
    }

def gen_add_script(kind, ingrs, level, index):
    (groups, pairs) = ingrs
    add_name = 'A1V7_AAdd' + str(index) + '_' + kind.name + '_' + str(level)
    s = []
    s.append('Begin ' + add_name)
    s.append('')
    if groups:
        s.append('short in')
    s.append('short add')
    s.append('short state')
    s.append('')
    s.append('short PCSkipEquip')
    s.append('short OnPCEquip')
    s.append('')
    s.append('set PCSkipEquip to 1')
    s.append('')
    s.append('if ( state == 1 )')
    s.append('	if ( A1V7_AlchemyRes != 0 )')
    s.append('		if ( ScriptRunning A1V7_CalcAlchemy' + ('2' if type(kind.potion) == Potion2 else '5') + '_sc == 0 )')
    s.append('			set state to 2')
    s.append('		endif')
    s.append('	endif')
    s.append('	return')
    s.append('endif')
    s.append('')
    s.append('if ( state == 0 )')
    s.append('	if ( OnPCEquip == 1 )')
    s.append('		set OnPCEquip to 0')
    s.append('')
    if type(kind.potion) == Potion2:
        s.append('		set A1V7_CalcAlchemy2_sc.Difficulty to ' + str(kind.potion.difficulty))
    s.append('		set A1V7_CalcAlchemy' + ('2' if type(kind.potion) == Potion2 else '5') + ' to 1')
    s.append('		set A1V7_AlchemyRes to 0')
    s.append('		set state to 1')
    s.append('	endif')
    s.append('	return')
    s.append('endif')
    s.append('')
    s.append('set A1V7_AlchemyCheck to 1')
    s.append('set state to 0')
    s.append('if ( A1V7_AlchemyRes < 4 )')
    s.append('	return')
    s.append('endif')
    s.append('')
    s.append('set add to 0')
    s.append('')
    if groups:
        s.append('set in to 0')
        n_in = 0;
        max_in = 0;
        for g in range(0, len(groups)):
            if g == 1 and g == len(groups) - 1:
                s.append('if ( in > 0 )')
            elif g == len(groups) - 1:
                s.append('if ( add == 0 )')
                s.append('	if ( in > 0 )')
            elif g > 1:
                s.append('if ( add == 0 )')
            for i in range(0, len(groups[g])):
                n_in += 1
                if g == 0 and i == 0:
                    s.append('if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('	set in to 1')
                    max_in = 1
                elif g == 0:
                    s.append('elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('	set in to ' + str(n_in) + '')
                    max_in = n_in
                elif g == 1 and i == 0 and g == len(groups) - 1:
                    s.append('	if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('		set add to 1')
                    s.append('		player->RemoveItem "' + groups[g][i].name + '", 1')
                elif g == 1 and g == len(groups) - 1:
                    s.append('	elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('		set add to 1')
                    s.append('		player->RemoveItem "' + groups[g][i].name + '", 1')
                elif g == 1 and i == 0:
                    s.append('if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('	if ( in > 0 )')
                    s.append('		set add to 1')
                    s.append('		player->RemoveItem "' + groups[g][i].name + '", 1')
                    s.append('	else')
                    s.append('		set in to ' + str(n_in) + '')
                    s.append('	endif')
                    max_in = n_in
                elif g == 1:
                    s.append('elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('	if ( in > 0 )')
                    s.append('		set add to 1')
                    s.append('		player->RemoveItem "' + groups[g][i].name + '", 1')
                    s.append('	else')
                    s.append('		set in to ' + str(n_in) + '')
                    s.append('	endif')
                    max_in = n_in
                elif i == 0 and g == len(groups) - 1:
                    s.append('		if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('			set add to 1')
                    s.append('			player->RemoveItem "' + groups[g][i].name + '", 1')
                elif i == 0:
                    s.append('	if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('		if ( in > 0 )')
                    s.append('			set add to 1')
                    s.append('			player->RemoveItem "' + groups[g][i].name + '", 1')
                    s.append('		else')
                    s.append('			set in to ' + str(n_in) + '')
                    s.append('		endif')
                    max_in = n_in
                elif g == len(groups) - 1:
                    s.append('		elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('			set add to 1')
                    s.append('			player->RemoveItem "' + groups[g][i].name + '", 1')
                else:
                    s.append('	elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    s.append('		if ( in > 0 )')
                    s.append('			set add to 1')
                    s.append('			player->RemoveItem "' + groups[g][i].name + '", 1')
                    s.append('		else')
                    s.append('			set in to ' + str(n_in) + '')
                    s.append('		endif')
                    max_in = n_in
            if g == 1 and g == len(groups) - 1:
                s.append('	endif')
            elif g == len(groups) - 1:
                s.append('		endif')
                s.append('	endif')
            elif g > 1:
                s.append('	endif')
            s.append('endif')
        s.append('if ( add == 1 )')
        if max_in == 0:
            s.append('	player->RemoveItem "' + groups[1][0].name + '", 1')
        elif max_in == 1:
            print('pair error')
            sys.exit(12)
        else:
            n_in = 0
            for g in groups:
                for i in g:
                    n_in += 1
                    if n_in == 1:
                        s.append('	if ( in == 1 )')
                    elif n_in < max_in:
                        s.append('	elseif ( in == ' + str(n_in) + ' )')
                    elif n_in == max_in:
                        s.append('	else')
                    if n_in <= max_in:
                        s.append('		player->RemoveItem "' + i.name + '", 1')
            s.append('	endif')
        s.append('endif')
    n_pair = 0
    for p in pairs:
        n_pair += 1
        if not groups and n_pair == 1:
            s.append('if ( player->GetItemCount "' + p[0].name + '" > 0 )')
            s.append('	if ( player->GetItemCount "' + p[1].name + '" > 0 )')
            s.append('		player->RemoveItem "' + p[0].name + '", 1')
            s.append('		player->RemoveItem "' + p[1].name + '", 1')
            s.append('		set add to 1')
            s.append('	endif')
            s.append('endif')
        else:
            s.append('if ( add == 0 )')
            s.append('	if ( player->GetItemCount "' + p[0].name + '" > 0 )')
            s.append('		if ( player->GetItemCount "' + p[1].name + '" > 0 )')
            s.append('			player->RemoveItem "' + p[0].name + '", 1')
            s.append('			player->RemoveItem "' + p[1].name + '", 1')
            s.append('			set add to 1')
            s.append('		endif')
            s.append('	endif')
            s.append('endif')
    s.append('')
    s.append('if ( add == 0 )')
    s.append('	set A1V7_AlchemyRes to 1')
    s.append('	return')
    s.append('endif')
    if type(kind.potion) == Potion2:
        s.append('if ( A1V7_AlchemyRes == 5 )')
        s.append('	player->AddItem ' + kind.potion.id_1 + ', 1')
        s.append('elseif ( A1V7_AlchemyRes == 6 )')
        s.append('	player->AddItem ' + kind.potion.id_1 + ', 2')
        s.append('endif')
    else:
        s.append('if ( A1V7_AlchemyRes == 5 )')
        s.append('	player->AddItem ' + kind.potion.id_broken_1 + ', 1')
        s.append('elseif ( A1V7_AlchemyRes == 6 )')
        s.append('	player->AddItem ' + kind.potion.id_cheap_1 + ', 1')
        s.append('elseif ( A1V7_AlchemyRes == 7 )')
        s.append('	player->AddItem ' + kind.potion.id_standard_1 + ', 1')
        s.append('elseif ( A1V7_AlchemyRes == 8 )')
        s.append('	player->AddItem ' + kind.potion.id_qualitative_1 + ', 1')
        s.append('elseif ( A1V7_AlchemyRes == 9 )')
        s.append('	player->AddItem ' + kind.potion.id_exclusive_1 + ', 1')
        s.append('endif')
    s.append('')
    s.append('End')
    return gen_script(add_name, s)

def gen_check_script(kind, ingrs, index, next_kind):
    (groups, pairs) = filter_and_group_ingredients(ingrs, kind, None)
    ingrs_15 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 15))
    ingrs_30 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 30))
    ingrs_45 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 45))
    ingrs_60 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 60))
    has_15 = len(groups_filter_level(groups, 15, kind)) >= 2 or not not pairs_filter_level(pairs, 15, kind)
    has_30 = len(groups_filter_level(groups, 30, kind)) >= 2 or not not pairs_filter_level(pairs, 30, kind)
    has_45 = len(groups_filter_level(groups, 45, kind)) >= 2 or not not pairs_filter_level(pairs, 45, kind)
    has_60 = len(groups_filter_level(groups, 60, kind)) >= 2 or not not pairs_filter_level(pairs, 60, kind)
    if has_15 != ingrs_15 or has_30 != ingrs_30 or has_45 != ingrs_45 or has_60 != ingrs_60:
        print('ingrs error')
        sys.exit(12)
    if not has_15 and not has_30 and not has_45 and not has_60:
        print(kind.name, 'has error')
        sys.exit(11)
    check_name = 'A1V7_ACheck' + str(index) + '_' + kind.name + '_sc'
    s = []
    s.append('Begin ' + check_name)
    s.append('')
    if not groups and len(pairs) == 1:
        s.append('if ( player->GetItemCount "A1V7_L' + str(pair_level(pairs[0], kind)) + '_' + kind.potion.id_base + '" == 1 )')
        s.append('	player->RemoveItem "A1V7_L' + str(pair_level(pairs[0], kind)) + '_' + kind.potion.id_base + '", 1')
        s.append('endif')
        s.append('if ( player->GetItemCount "' + pairs[0][0].name + '" > 0 )')
        s.append('	if ( player->GetItemCount "' + pairs[0][1].name + '" > 0 )')
        s.append('		player->AddItem "A1V7_L' + str(pair_level(pairs[0], kind)) + '_' + kind.potion.id_base + '", 1')
        s.append('	endif')
        s.append('endif')
    else:
        if has_15:
            s.append('short in15')
        if has_30:
            s.append('short in30')
        if has_45:
            s.append('short in45')
        if has_60:
            s.append('short in60')
        s.append('')
        line = ''
        if has_15:
            s.append('if ( player->GetItemCount "A1V7_L15_' + kind.potion.id_base + '" == 1 )')
            s.append('	player->RemoveItem "A1V7_L15_' + kind.potion.id_base + '", 1')
            line = 'else' if ingrs_30 or ingrs_45 or ingrs_60 else ''
        if has_30:
            s.append(line + 'if ( player->GetItemCount "A1V7_L30_' + kind.potion.id_base + '" == 1 )')
            s.append('	player->RemoveItem "A1V7_L30_' + kind.potion.id_base + '", 1')
            line = 'else' if ingrs_45 or ingrs_60 else ''
        if has_45:
            s.append(line + 'if ( player->GetItemCount "A1V7_L45_' + kind.potion.id_base + '" == 1 )')
            s.append('	player->RemoveItem "A1V7_L45_' + kind.potion.id_base + '", 1')
            line = 'else' if ingrs_60 else ''
        if has_60:
            s.append(line + 'if ( player->GetItemCount "A1V7_L60_' + kind.potion.id_base + '" == 1 )')
            s.append('	player->RemoveItem "A1V7_L60_' + kind.potion.id_base + '", 1')
        s.append('endif')
        s.append('')
        if has_15:
            s.append('set in15 to 0')
        if has_30:
            s.append('set in30 to 0')
        if has_45:
            s.append('set in45 to 0')
        if has_60:
            s.append('set in60 to 0')
        s.append('')
        line = ''
        if groups:
            was_level = [ False, False, False, False ]
            for g in range(0, len(groups)):
                group_has_level = [ False, False, False, False ]
                for i in range(0, len(groups[g])):
                    if i == 0:
                        s.append('if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    else:
                        s.append('elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )')
                    level = ingr_level(groups[g][i], kind)
                    if level == 15 and not has_15:
                        level = 30
                    if level == 30 and not has_30:
                        level = 45
                    if level == 45 and not has_45:
                        level = 60
                    if level == 60 and not has_60:
                        print('level error')
                        sys.exit(8)
                    level_index = level // 15 - 1
                    if was_level[level_index]:
                        s.append('	set in' + str(level) + ' to ( in' + str(level) + ' + 1 )')
                    else:
                        group_has_level[level_index] = True
                        s.append('	set in' + str(level) + ' to 1')
                s.append('endif')
                for level_index in range(0, 4):
                    was_level[level_index] = was_level[level_index] or group_has_level[level_index]
            s.append('')
            adds = False
            if has_30 and has_15:
                s.append('set in30 to ( in30 + in15 )')
                adds = True
            if has_45:
                if has_30:
                    s.append('set in45 to ( in45 + in30 )')
                    adds = True
                elif has_15:
                    s.append('set in45 to ( in45 + in15 )')
                    adds = True
            if has_60:
                if has_45:
                    s.append('set in60 to ( in60 + in45 )')
                    adds = True
                elif has_30:
                    s.append('set in60 to ( in60 + in30 )')
                    adds = True
                elif has_15:
                    s.append('set in60 to ( in60 + in15 )')
                    adds = True
            if adds:
                s.append('')
        if pairs:
            for p in pairs:
                s.append('if ( player->GetItemCount "' + p[0].name + '" > 0 )')
                s.append('	if ( player->GetItemCount "' + p[1].name + '" > 0 )')
                s.append('		set in' + str(pair_level(p, kind)) + ' to 2')
                s.append('	endif')
                s.append('endif')
            s.append('')
        if has_15:
            s.append('if ( in15 > 1 )')
            s.append('	player->AddItem "A1V7_L15_' + kind.potion.id_base + '", 1')
            line = 'else' if has_30 or has_45 or has_60 else ''
        if has_30:
            s.append(line + 'if ( in30 > 1 )')
            s.append('	player->AddItem "A1V7_L30_' + kind.potion.id_base + '", 1')
            line = 'else' if has_45 or has_60 else ''
        if has_45:
            s.append(line + 'if ( in45 > 1 )')
            s.append('	player->AddItem "A1V7_L45_' + kind.potion.id_base + '", 1')
            line = 'else' if has_60 else ''
        if has_60:
            s.append(line + 'if ( in60 > 1 )')
            s.append('	player->AddItem "A1V7_L60_' + kind.potion.id_base + '", 1')
        s.append('endif')
    s.append('')
    s.append('StopScript ' + check_name)
    if next_kind == None:
        s.append('if ( A1V7_AlchemyRes == 0 )')
        s.append('	MessageBox "Готово"')
        s.append('elseif ( A1V7_AlchemyRes == 1 )')
        s.append('	MessageBox "Недостаточно компонентов"')
        s.append('elseif ( A1V7_AlchemyRes == 2 )')
        s.append('	MessageBox "Вам нужны ступка и пестик"')
        s.append('elseif ( A1V7_AlchemyRes == 3 )')
        s.append('	MessageBox "Выглядит слишком сложным"')
        s.append('elseif ( A1V7_AlchemyRes == 4 )')
        s.append('	PlaySound "potion fail"')
        s.append('	MessageBox "Вам не удалось создать зелье"')
        s.append('else')
        s.append('	PlaySound "potion success"')
        s.append('	MessageBox "Вы создали зелье"')
        s.append('	StartScript A1V7_ModAlchemyExp')
        s.append('endif')
        s.append('set A1V7_AlchemyRes to 0')
    else:
        s.append('StartScript A1V7_ACheck' + str(next_kind[0]) + '_' + next_kind[1].name + '_sc')
    s.append('')
    s.append('End')
    return gen_script(check_name, s)

def gen_del_script(kind, ingrs, index, next_kind):
    ingrs_15 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 15))
    ingrs_30 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 30))
    ingrs_45 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 45))
    ingrs_60 = not ingrs_empty(filter_and_group_ingredients(ingrs, kind, 60))
    del_name = 'A1V7_ADel' + str(index) + '_' + kind.name + '_sc'
    s = []
    s.append('Begin ' + del_name)
    s.append('')
    line = ''
    if ingrs_15:
        s.append('if ( player->GetItemCount "A1V7_L15_' + kind.potion.id_base + '" == 1 )')
        s.append('	player->RemoveItem "A1V7_L15_' + kind.potion.id_base + '", 1')
        line = 'else' if ingrs_30 or ingrs_45 or ingrs_60 else ''
    if ingrs_30:
        s.append(line + 'if ( player->GetItemCount "A1V7_L30_' + kind.potion.id_base + '" == 1 )')
        s.append('	player->RemoveItem "A1V7_L30_' + kind.potion.id_base + '", 1')
        line = 'else' if ingrs_45 or ingrs_60 else ''
    if ingrs_45:
        s.append(line + 'if ( player->GetItemCount "A1V7_L45_' + kind.potion.id_base + '" == 1 )')
        s.append('	player->RemoveItem "A1V7_L45_' + kind.potion.id_base + '", 1')
        line = 'else' if ingrs_60 else ''
    if ingrs_60:
        s.append(line + 'if ( player->GetItemCount "A1V7_L60_' + kind.potion.id_base + '" == 1 )')
        s.append('	player->RemoveItem "A1V7_L60_' + kind.potion.id_base + '", 1')
    s.append('endif')
    s.append('')
    s.append('StopScript ' + del_name)
    if next_kind == None:
        s.append('StartScript A1V7_ADelPlus')
    else:
        s.append('StartScript A1V7_ADel' + str(next_kind[0]) + '_' + next_kind[1].name + '_sc')
    s.append('')
    s.append('End')
    return gen_script(del_name, s)

def gen_effect_prop(irdt, value, suffix, level):
    irdt['effect_' + str(level // 15) + suffix] = str(value)

def gen_add_item(kind, index, level):
    if kind.potion is None:
        print(kind.name + ' does not have potion')
        sys.exit(1)
    add_name = 'A1V7_AAdd' + str(index) + '_' + kind.name + '_' + str(level)
    irdt = {
        'weight': 0.0,
        'value': 0,
        'effect_1_index': None,
        'effect_2_index': None,
        'effect_3_index': None,
        'effect_4_index': None,
        'effect_1_attribute': None,
        'effect_2_attribute': None,
        'effect_3_attribute': None,
        'effect_4_attribute': None,
        'effect_1_skill': None,
        'effect_2_skill': None,
        'effect_3_skill': None,
        'effect_4_skill': None,
    }
    if isinstance(kind.effect, str):
        gen_effect_prop(irdt, kind.effect, '_index', level)
    else:
        gen_effect_prop(irdt, kind.effect[0], '_index', level)
        if kind.effect[0] == 'FortifySkill':
            gen_effect_prop(irdt, kind.effect[1], '_skill', level)
        else:
            gen_effect_prop(irdt, kind.effect[1], '_attribute', level)
    name = 'A1V7_L' + str(level) + '_' + kind.potion.id_base
    if len(name) > 31:
        print('too long name')
        sys.exit(31)
    return {
        'INGR': [
            {'NAME': name},
            {'MODL': 'm\\misc_com_bottle_05.nif'},
            {'FNAM': ' Создать '},
            {'IRDT': irdt},
            {'SCRI': add_name},
            {'ITEX': 'k\\magic_alchemy.dds'},
        ]
    }

def gen_level_book(level):
    return {
        'BOOK': [
            {'NAME': 'A1V7_AlchemyPlus_' + str(level)},
            {'MODL': 'm\\Text_Scroll_01.NIF'},
            {'FNAM': 'Навык алхимии вырос'},
            {'BKDT': {
                'weight': 0.0,
                'value': 0,
                'flags': 'SCROLL',
                'skill': 'Alchemy',
                'enchantment': 0
            }},
            {'ITEX': 'm\\Tx_scroll_open_01.tga'},
            {'TEXT': [
                '<DIV ALIGN="LEFT"><FONT COLOR="000000" SIZE="3" FACE="Magic Cards"><BR>Ваш навык алхимии вырос.<BR>',
                ''
            ]},
        ]
    }

def assembly_plugin(path, year, month, day, hour, minute, second, keep=False):
    subprocess.run('espa -p ru -' + ('k' if keep else '') + 'v "' + path + '.yaml"', stdout=stdout, stderr=stderr, check=True)
    date = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    t = mktime(date.timetuple())
    utime(path, (t, t))

def find_mfr():
    with winreg.OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall') as uninstall_key:
        for i in count():
            subkey = winreg.EnumKey(uninstall_key, i)
            with winreg.OpenKey(uninstall_key, subkey) as key:
                try:
                    (token, _) = winreg.QueryValueEx(key, 'HelpLink')
                    if token == 'http://www.fullrest.ru/forum/topic/36164-morrowind-fullrest-repack/':
                        return winreg.QueryValueEx(key, 'InstallLocation')[0] + 'Data Files/'
                except FileNotFoundError:
                    pass

def gen_potions(icon, model, name, suffix, description):
    with open('potions.esp.yaml', 'r', encoding='utf-8') as f:
        potions = yaml.load(f, Loader=yaml.FullLoader)
    
    for potion in potions:
        icons = [i for i, x in enumerate(potion['ALCH']) if 'TEXT' in x]
        if len(icons) != 4:
            print('Error in potions.esp.yaml')
            sys.exit(1)
        for i in filter(lambda x: x != icon, range(len(icons) - 1, -1, -1)):
            del potion['ALCH'][icons[i]]

        models = [i for i, x in enumerate(potion['ALCH']) if 'MODL' in x]
        if len(models) != 3:
            print('Error in potions.esp.yaml')
            sys.exit(1)
        for i in filter(lambda x: x != model, range(len(models) - 1, -1, -1)):
            del potion['ALCH'][models[i]]

        names = [i for i, x in enumerate(potion['ALCH']) if 'FNAM' in x]
        if len(names) != 3:
            print('Error in potions.esp.yaml')
            sys.exit(1)
        for n in names:
            if len(potion['ALCH'][n]['FNAM']) > 31:
                print('Too long potion name:', potion['ALCH'][0]['NAME'])
                sys.exit(1)
        for i in filter(lambda x: x != name, range(len(names) - 1, -1, -1)):
            del potion['ALCH'][names[i]]

    with open('potions_header.esp.yaml', 'r', encoding='utf-8') as f:
        esp_header = yaml.load(f, Loader=yaml.FullLoader)

    esp_header[0]['TES3'][0]['HEDR']['description'].append('')
    esp_header[0]['TES3'][0]['HEDR']['description'].append(description)
    esp_header[0]['TES3'][0]['HEDR']['records'] = len(esp_header) + len(potions) - 1

    with open('A1_Alchemy_Potions' + suffix + '.esp.yaml', 'w', encoding='utf-8') as esp:
        yaml.dump(esp_header, esp, allow_unicode=True)
        yaml.dump(potions, esp, allow_unicode=True)
    
    reformat('A1_Alchemy_Potions' + suffix + '.esp')

def prepare_dialogs(path):
    with open(path + '.esp.yaml', 'r', encoding='utf-8') as f:
        records = yaml.load(f, Loader=yaml.FullLoader)
    
    topics = {}
    for record in records:
        info = record.get('INFO')
        if info is not None:
            name = [i for i, x in enumerate(info) if 'NAME' in x]
            if len(name) != 1:
                print('Error in ' + path + '.esp.yaml')
                sys.exit(1)
            value = info[name[0]]['NAME']
            ms = list(re.compile(r'\{([^{|}]*)(\|([^{|}]*))?\}').finditer(value))
            if not ms:
                continue
            ts = ['@' + m.group(1) + '#' for m in ms]
            ps = [value[p.end() : n.start()] for (p, n) in zip(ms[:-1], ms[1:])]
            info[name[0]]['NAME'] = value[: ms[0].start()] + ts[0] + ''.join([i + t for (i, t) in zip(ps, ts[1:])]) + value[ms[-1].end() :]
            for m in ms:
                if m.group(3) is not None:
                    topics[m.group(1)] = m.group(3)

    with open(path + '.esp.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(records, f, allow_unicode=True)

    reformat(path + '.esp')

    topics = list(topics.items())
    topics.sort(key=lambda x: x[0])
    with open(path + '.top', 'w', encoding='utf-8') as f:
        for topic in topics:
            f.write('{}\t{}\n'.format(topic[0], topic[1]))

def reformat(path):
    subprocess.run('espa -p ru -v "' + path + '.yaml"', stdout=stdout, stderr=stderr, check=True)
    subprocess.run('espa -p ru -vd ' + path, stdout=stdout, stderr=stderr, check=True)

def run_au3(path):
    command = winreg.QueryValue(HKEY_CLASSES_ROOT, 'AutoIt3XScript\\Shell\\Run\\Command')
    command = command[:command.index('"%1"')]
    subprocess.run(command + ' ' + path, stdout=stdout, stderr=stderr, check=True)

def gen_apparatus(ingrs_set, mfr, year, month, day, hour, minute, second, suffix, version):
    ingrs = { i.name: i for i in load_ingredients('ingredients/Morrowind.esm.yaml') }
    ingrs.update({ i.name: i for i in load_ingredients('ingredients/Tribunal.esm.yaml') })
    ingrs.update({ i.name: i for i in load_ingredients('ingredients/Bloodmoon.esm.yaml') })

    extra_ingrs_esp = []
    extra_ingr_files = [
        'AlterationPrecise_1C.esp.yaml',
        'Clean Ash_Grasses_20RU.esp.yaml',
        'Clean Bones11RU.esp.yaml',
        'Clean Cobwebs3.4RU.esp.yaml',
        'Clean Ferns_10_unscriptedRU.esp.yaml',
        'Clean Grasses_10RU.esp.yaml',
        'Clean Lilypads11RU.esp.yaml',
        'Clean Swamp_Scums_20_unscriptedRU.esp.yaml',
    ]
    for e in extra_ingr_files:
        ingrs.update({ i.name: i for i in load_ingredients('ingredients/' + e) })
        with open('ingredients/' + e, 'r', encoding='utf-8') as f:
            extra_ingrs_esp.extend(yaml.load(f, Loader=yaml.FullLoader))

    if ingrs_set == 'eva':
        ingrs.update({ i.name: i for i in load_ingredients('ingredients/EVA.ESP.yaml') })
    elif ingrs_set == 'mfr':
        ingrs.update({ i.name: i for i in load_ingredients('ingredients/MFR_EVA.esm.yaml') })

    ingrs = list(ingrs.values())
    ingrs.sort(key=lambda x: x.name)
    ingrs.sort(key=lambda x: len(x.name))

    add_items = []
    add_scripts = []
    check_scripts = []
    del_scripts = []
    next_useful_kind = None
    for (i, kind) in reversed(list(enumerate(kinds))):
        index = i + 1
        is_useful = False
        for level in reversed([15, 30, 45, 60]):
            level_ingrs = filter_and_group_ingredients(ingrs, kind, level)
            if not ingrs_empty(level_ingrs):
                is_useful = True
                add_items.append(gen_add_item(kind, index, level))
                add_scripts.append(gen_add_script(kind, level_ingrs, level, index))
        if is_useful:
            check_scripts.append(gen_check_script(kind, ingrs, index, next_useful_kind))
            del_scripts.append(gen_del_script(kind, ingrs, index, next_useful_kind))
        if is_useful:
            next_useful_kind = (index, kind)
    add_items.reverse()
    add_scripts.reverse()
    check_scripts.reverse()
    del_scripts.reverse()

    level_books = []
    for level in range(0, 100):
        level_books.append(gen_level_book(level))

    with open('apparatus_header.esp.yaml', 'r', encoding='utf-8') as f:
        esp_header = yaml.load(f, Loader=yaml.FullLoader)

    esp_header[0]['TES3'][0]['HEDR']['description'].append('')
    esp_header[0]['TES3'][0]['HEDR']['description'].append(version)
    esp_header[0]['TES3'][0]['HEDR']['records'] = len(esp_header) + len(add_items) + len(check_scripts) + len(add_scripts) + len(del_scripts) + len(level_books) - 1

    with open(mfr + 'alchemy_' + ingrs_set + '.esp.yaml', 'w', encoding='utf-8') as esp:
        yaml.dump(esp_header, esp, allow_unicode=True)
        yaml.dump(extra_ingrs_esp, esp, allow_unicode=True)
        yaml.dump(add_items, esp, allow_unicode=True)
        yaml.dump(add_scripts, esp, allow_unicode=True)
        yaml.dump(check_scripts, esp, allow_unicode=True)
        yaml.dump(del_scripts, esp, allow_unicode=True)
        yaml.dump(level_books, esp, allow_unicode=True)

    assembly_plugin(mfr + 'alchemy_' + ingrs_set + '.esp', year, month, day, hour, minute, second)

    with open('00_includes.au_', 'r', encoding='utf-8') as f:
        au3_includes = f.read()
    with open('01_header.au_', 'r', encoding='utf-8') as f:
        au3_header = f.read()
    with open('02_script.au_', 'r', encoding='utf-8') as f:
        au3_script = f.read()
    with open('03_close.au_', 'r', encoding='utf-8') as f:
        au3_close = f.read()
    with open('alchemy_' + ingrs_set + '.au3', 'w', encoding='utf-8') as au3:
        au3.write(au3_includes)
        au3.write('\n$ingrs_set = "' + ingrs_set +'"\n\n')
        au3.write(au3_header)
        au3.write('\n')
        au3.write('$script = "A1V7_AppaInfo_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_AlchemyActivator_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_ApparatusDeactivate_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_ApparatusSetUp"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_Calcinator_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_Alembic_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_Retort_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_ApparatusItem_1_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_ApparatusItem_2_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_ApparatusItem_3_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_ModAlchemyExp"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_CalcAlchemy2_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_CalcAlchemy5_sc"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_StartAlchemy"\n')
        au3.write(au3_script)
        au3.write('\n')
        au3.write('$script = "A1V7_AlchemyCheck_sc"\n')
        au3.write(au3_script)
        for script in chain(check_scripts, add_scripts, del_scripts):
            script_name = script['SCPT'][0]['SCHD']['name']
            au3.write('\n')
            au3.write('$script = "' + script_name +'"\n')
            au3.write(au3_script)
        au3.write(au3_close)
    run_au3('alchemy_' + ingrs_set + '.au3')
    remove('alchemy_' + ingrs_set + '.au3')
    move(mfr + 'alchemy_' + ingrs_set + '.esp', 'A1_Alchemy_V7_Apparatus' + suffix + '.esp')
    subprocess.run('espa -p ru -vd ' + 'A1_Alchemy_V7_Apparatus' + suffix + '.esp', stdout=stdout, stderr=stderr, check=True)
    prepare_dialogs('A1_Alchemy_V7_Apparatus' + suffix)

def write_records_count(esp_path):
    with open(esp_path, 'r', encoding='utf-8') as f:
        esp = yaml.load(f, Loader=yaml.FullLoader)
    esp[0]['TES3'][0]['HEDR']['records'] = len(esp) - 1
    with open(esp_path, 'w', encoding='utf-8') as f:
        yaml.dump(esp, f, allow_unicode=True)

def check_espa_version():
  espa = subprocess.run('espa -V', stdout=PIPE, check=True, universal_newlines=True)
  if espa.stdout != '0.3.0\n':
    print('wrong espa version')
    sys.exit(1)

def prepare_text(path, d):
    with open(path.upper(), 'r', encoding='utf-8') as utf8:
        with open(d + path + '.txt', 'w', encoding='cp1251') as cp1251:
            cp1251.write(utf8.read())

def make_archive(name, dir):
    chdir(dir)
    if path.exists('../' + name + '.7z'):
        remove('../' + name + '.7z')
    subprocess.run('7za a ../' + name + '.7z .', stdout=stdout, stderr=stderr, check=True)
    chdir('..')

def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '~')

def main():
    cd = path.dirname(path.realpath(__file__))
    chdir(cd)
    check_espa_version()
    mfr = find_mfr()
    yaml.add_representer(type(None), represent_none)
    if path.exists('ar'):
        rmtree('ar')
    mkdir('ar')
    copytree('Data Files', 'ar/Data Files')
    prepare_text('Readme', 'ar/')
    prepare_text('Versions', 'ar/')
    copytree('Screenshots', 'ar/Screenshots')
    gen_potions(0, 0, 0, '', 'Стандартная версия')
    copyfile('A1_Alchemy_Potions.esp.yaml', mfr + 'alchemy_potions.esp.yaml')
    assembly_plugin(mfr + 'alchemy_potions.esp', 2014, 8, 3, 18, 53, 0)
    chdir('bin')
    subprocess.run('cargo build --workspace --target i686-pc-windows-msvc --release --out-dir .. -Z unstable-options', stdout=stdout, stderr=stderr, check=True)
    chdir('..')
    copyfile('potions_balance.exe', 'ar/PotionsBalance.exe')
    copyfile('migrate_legacy_save.exe', 'ar/MigrateLegacySave.exe')
    gen_apparatus('mfr', mfr, 2014, 8, 10, 18, 53, 0, '_MFR', 'Версия для использования с MFR_EVA.esm (M[FR] 3.x)')
    gen_apparatus('eva', mfr, 2097, 9, 1, 18, 53, 0, '_EVA', 'Версия для использования с EVA.esp (M[FR] 2.x)')
    gen_apparatus('std', mfr, 2014, 8, 10, 18, 53, 0, '', 'Версия для использования без EVA.esp/MFR_EVA.esm')
    remove(mfr + 'alchemy_potions.esp')
    gen_potions(1, 0, 0, '_MM', 'Версия для MagicMarker')
    gen_potions(2, 1, 1, '_PU', 'Версия для Potion Upgrade')
    gen_potions(3, 2, 2, '_PR', 'Версия для AOF Potions Recolored')
    copyfile('A1_Alchemy_Potions.esp.yaml', 'ar/Data Files/A1_Alchemy_Potions.esp.yaml')
    copyfile('A1_Alchemy_Potions_MM.esp.yaml', 'ar/Data Files/A1_Alchemy_Potions_MM.esp.yaml')
    copyfile('A1_Alchemy_Potions_PU.esp.yaml', 'ar/Data Files/A1_Alchemy_Potions_PU.esp.yaml')
    copyfile('A1_Alchemy_Potions_PR.esp.yaml', 'ar/Data Files/A1_Alchemy_Potions_PR.esp.yaml')
    copyfile('A1_Alchemy_V7_Apparatus.top', 'ar/Data Files/A1_Alchemy_V7_Apparatus.top')
    copyfile('A1_Alchemy_V7_Apparatus_EVA.top', 'ar/Data Files/A1_Alchemy_V7_Apparatus_EVA.top')
    copyfile('A1_Alchemy_V7_Apparatus_MFR.top', 'ar/Data Files/A1_Alchemy_V7_Apparatus_MFR.top')
    copyfile('A1_Alchemy_V7_Apparatus.esp.yaml', 'ar/Data Files/A1_Alchemy_V7_Apparatus.esp.yaml')
    copyfile('A1_Alchemy_V7_Apparatus_EVA.esp.yaml', 'ar/Data Files/A1_Alchemy_V7_Apparatus_EVA.esp.yaml')
    copyfile('A1_Alchemy_V7_Apparatus_MFR.esp.yaml', 'ar/Data Files/A1_Alchemy_V7_Apparatus_MFR.esp.yaml')
    assembly_plugin('ar/Data Files/A1_Alchemy_V7_Apparatus.esp', 2026, 10, 6, 18, 53, 0)
    assembly_plugin('ar/Data Files/A1_Alchemy_V7_Apparatus_MFR.esp', 2026, 10, 6, 18, 53, 0)
    assembly_plugin('ar/Data Files/A1_Alchemy_V7_Apparatus_EVA.esp', 2097, 9, 1, 18, 53, 0)
    assembly_plugin('ar/Data Files/A1_Alchemy_Potions.esp', 2014, 8, 3, 18, 53, 0)
    assembly_plugin('ar/Data Files/A1_Alchemy_Potions_MM.esp', 2014, 8, 3, 18, 53, 0)
    assembly_plugin('ar/Data Files/A1_Alchemy_Potions_PU.esp', 2026, 10, 5, 18, 53, 0)
    assembly_plugin('ar/Data Files/A1_Alchemy_Potions_PR.esp', 2014, 8, 3, 18, 53, 0)
    make_archive('A1_Alchemy_2.0', 'ar')
    rmtree('ar')    

if __name__ == "__main__":
    main()
