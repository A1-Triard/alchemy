# -*- coding: utf-8 -*-
from collections import namedtuple
from itertools import chain, product, combinations
import os, sys, shutil

Effect = namedtuple('Effect', ['id', 'spec'])
Effect.__eq__ = lambda a, b: None != b and a.id == b.id and a.spec == b.spec

negative_effects = [
    Effect(7, None),
    Effect(14, None),
    Effect(15, None),
    Effect(16, None),
    Effect(17, 0),
    Effect(17, 1),
    Effect(17, 2),
    Effect(17, 3),
    Effect(17, 4),
    Effect(17, 5),
    Effect(17, 6),
    Effect(17, 7),
    Effect(18, None),
    Effect(19, None),
    Effect(20, None),
    Effect(21, 11),
    Effect(22, 0),
    Effect(22, 1),
    Effect(22, 2),
    Effect(22, 3),
    Effect(22, 4),
    Effect(22, 5),
    Effect(22, 6),
    Effect(22, 7),
    Effect(23, None),
    Effect(24, None),
    Effect(25, None),
    Effect(26, None),
    Effect(27, None),
    Effect(28, None),
    Effect(29, None),
    Effect(30, None),
    Effect(31, None),
    Effect(32, None),
    Effect(33, None),
    Effect(34, None),
    Effect(35, None),
    Effect(36, None),
    Effect(37, None),
    Effect(38, None),
    Effect(45, None),
    Effect(46, None),
    Effect(47, None),
    Effect(48, None),
    Effect(132, None),
    Effect(133, None),
    Effect(136, None),
]

neutral_effects = [
    Effect(3, None),
    Effect(9, None),
    Effect(11, None),
    Effect(40, None),
    Effect(41, None),
    Effect(42, None),
    Effect(61, None),
    Effect(83, None),
    Effect(84, None),
    Effect(92, None),
    Effect(95, None),
    Effect(96, None),
    Effect(98, None),
    Effect(99, None),
    Effect(100, None),
]

neutral_effects_eva = [
    Effect(3, None),
    Effect(9, None),
    Effect(11, None),
    Effect(40, None),
    Effect(41, None),
    Effect(42, None),
    Effect(63, None),
    Effect(83, None),
    Effect(84, None),
    Effect(92, None),
    Effect(95, None),
    Effect(96, None),
    Effect(98, None),
    Effect(99, None),
    Effect(100, None),
    Effect(102, None),
    Effect(103, None),
    Effect(111, None),
]

Potion2 = namedtuple('Potion2', ['id_1_16', 'id_1', 'id_base', 'difficulty'])
Potion5 = namedtuple('Potion5', ['id_broken_1_8', 'id_cheap_1_8', 'id_standard_1_8', 'id_qualitative_1_8', 'id_exclusive_1_8', 'id_broken_1', 'id_cheap_1', 'id_standard_1', 'id_qualitative_1', 'id_exclusive_1', 'id_base'])

Kind = namedtuple('Kind', ['index', 'name', 'effect', 'potion'])

base_kinds = [
    Kind(1, 'RestoreHealth', Effect(75, None), Potion5('p_restore_health_b_A1_8', 'p_restore_health_c_A1_8', 'p_restore_health_s_A1_8', 'p_restore_health_q_A1_8', 'p_restore_health_e_A1_8', 'p_restore_health_b', 'p_restore_health_c', 'p_restore_health_s', 'p_restore_health_q', 'p_restore_health_e', 'restore_health')),
    Kind(2, 'RestoreFatig', Effect(77, None), Potion5('p_restore_fatigue_b_A1_8', 'p_restore_fatigue_c_A1_8', 'p_restore_fatigue_s_A1_8', 'p_restore_fatigue_q_A1_8', 'p_restore_fatigue_e_A1_8', 'p_restore_fatigue_b', 'p_restore_fatigue_c', 'p_restore_fatigue_s', 'p_restore_fatigue_q', 'p_restore_fatigue_e', 'restore_fatigue')),
    Kind(3, 'RestoreMagic', Effect(76, None), Potion5('p_restore_magicka_b_A1_8', 'p_restore_magicka_c_A1_8', 'p_restore_magicka_s_A1_8', 'p_restore_magicka_q_A1_8', 'p_restore_magicka_e_A1_8', 'p_restore_magicka_b', 'p_restore_magicka_c', 'p_restore_magicka_s', 'p_restore_magicka_q', 'p_restore_magicka_e', 'restore_magicka')),
    Kind(4, 'WaterWalk', Effect(2, None), Potion5('p_water_walking_b_A1_8', 'p_water_walking_c_A1_8', 'p_water_walking_s_A1_8', 'p_water_walking_q_A1_8', 'p_water_walking_e_A1_8', 'p_water_walking_b_A1', 'p_water_walking_c_A1', 'p_water_walking_s', 'p_water_walking_q_A1', 'p_water_walking_e_A1', 'water_walking')),
    Kind(5, 'WaterBrf', Effect(0, None), Potion5('p_water_breathing_b_A1_8', 'p_water_breathing_c_A1_8', 'p_water_breathing_s_A1_8', 'p_water_breathing_q_A1_8', 'p_water_breathing_e_A1_8', 'p_water_breathing_b_A1', 'p_water_breathing_c_A1', 'p_water_breathing_s', 'p_water_breathing_q_A1', 'p_water_breathing_e_A1', 'water_breathing')),
    Kind(6, 'Levitate', Effect(10, None), Potion5('p_levitation_b_A1_8', 'p_levitation_c_A1_8', 'p_levitation_s_A1_8', 'p_levitation_q_A1_8', 'p_levitation_e_A1_8', 'p_levitation_b', 'p_levitation_c', 'p_levitation_s', 'p_levitation_q', 'p_levitation_e', 'levitation')),
    Kind(7, 'Tele', Effect(59, None), Potion5('p_telekinesis_b_A1_8', 'p_telekinesis_c_A1_8', 'p_telekinesis_s_A1_8', 'p_telekinesis_q_A1_8', 'p_telekinesis_e_A1_8', 'p_telekinesis_b_A1', 'p_telekinesis_c_A1', 'p_telekinesis_s', 'p_telekinesis_q_A1', 'p_telekinesis_e_A1', 'telekinesis')),
    Kind(8, 'Blight', Effect(70, None), Potion2('p_cure_blight_s_A1_16', 'p_cure_blight_s', 'cure_blight', 60)),
    Kind(9, 'Cure', Effect(69, None), Potion2('p_cure_common_s_A1_16', 'p_cure_common_s', 'cure_common', 40)),
    Kind(10, 'DetKey', Effect(66, None), Potion5('p_detect_key_b_A1_8', 'p_detect_key_c_A1_8', 'p_detect_key_s_A1_8', 'p_detect_key_q_A1_8', 'p_detect_key_e_A1_8', 'p_detect_key_b_A1', 'p_detect_key_c_A1', 'p_detect_key_s', 'p_detect_key_q_A1', 'p_detect_key_e_A1', 'detect_key')),
    Kind(11, 'Poison', Effect(72, None), Potion2('p_cure_poison_s_A1_16', 'p_cure_poison_s', 'cure_poison', 40)),
    Kind(12, 'Feather', Effect(8, None), Potion5('p_feather_b_A1_8', 'p_feather_c_A1_8', 'p_feather_s_A1_8', 'p_feather_q_A1_8', 'p_feather_e_A1_8', 'p_feather_b', 'p_feather_c', 'p_feather_s_A1', 'p_feather_q', 'p_feather_e', 'feather')),
    Kind(13, 'FireResist', Effect(90, None), Potion5('p_fire_resistance_b_A1_8', 'p_fire_resistance_c_A1_8', '"p_fire resistance_s_A1_8"', 'p_fire_resistance_q_A1_8', 'p_fire_resistance_e_A1_8', 'p_fire_resistance_b', 'p_fire_resistance_c', '"p_fire resistance_s"', 'p_fire_resistance_q', 'p_fire_resistance_e', 'fire_resistance')),
    Kind(14, 'RestPers', Effect(74, 6), Potion5('p_restore_personality_b_A1_8', 'p_restore_personality_c_A1_8', 'p_restore_personality_s_A1_8', 'p_restore_personality_q_A1_8', 'p_restore_personality_e_A1_8', 'p_restore_personality_b', 'p_restore_personality_c', 'p_restore_personality_s', 'p_restore_personality_q', 'p_restore_personality_e', 'restore_personality')),
    Kind(15, 'FortMagic', Effect(81, None), Potion5('p_fortify_magicka_b_A1_8', 'p_fortify_magicka_c_A1_8', 'p_fortify_magicka_s_A1_8', 'p_fortify_magicka_q_A1_8', 'p_fortify_magicka_e_A1_8', 'p_fortify_magicka_b', 'p_fortify_magicka_c', 'p_fortify_magicka_s', 'p_fortify_magicka_q', 'p_fortify_magicka_e', 'fortify_magicka')),
    Kind(16, 'NightEye', Effect(43, None), Potion5('"p_night-eye_b_A1_8"', '"p_night-eye_c_A1_8"', '"p_night-eye_s_A1_8"', '"p_night-eye_q_A1_8"', '"p_night-eye_e_A1_8"', '"p_night-eye_b"', '"p_night-eye_c"', '"p_night-eye_s"', '"p_night-eye_q"', '"p_night-eye_e"', 'night-eye')),
    Kind(17, 'DetCreature', Effect(64, None), Potion5('p_detect_creatures_b_A1_8', 'p_detect_creatures_c_A1_8', 'p_detect_creatures_s_A1_8', 'p_detect_creatures_q_A1_8', 'p_detect_creatures_e_A1_8', 'p_detect_creatures_b_A1', 'p_detect_creatures_c_A1', 'p_detect_creatures_s', 'p_detect_creatures_q_A1', 'p_detect_creatures_e_A1', 'detect_creatures')),
    Kind(18, 'Para', Effect(73, None), Potion2('p_cure_paralyzation_s_A1_16', 'p_cure_paralyzation_s', 'cure_paralyzation', 40)),
    Kind(19, 'DetEnch', Effect(65, None), Potion5('p_detect_enchantment_b_A1_8', 'p_detect_enchantment_c_A1_8', 'p_detect_enchantment_s_A1_8', 'p_detect_enchantment_q_A1_8', 'p_detect_enchantment_e_A1_8', 'p_detect_enchantment_b_A1', 'p_detect_enchantment_c_A1', 'p_detect_enchantment_s', 'p_detect_enchantment_q_A1', 'p_detect_enchantment_e_A1', 'detect_enchantment')),
    Kind(20, 'Dispel', Effect(57, None), Potion5('p_dispel_b_A1_8', 'p_dispel_c_A1_8', 'p_dispel_s_A1_8', 'p_dispel_q_A1_8', 'p_dispel_e_A1_8', 'p_dispel_b_A1', 'p_dispel_c_A1', 'p_dispel_s', 'p_dispel_q_A1', 'p_dispel_e_A1', 'dispel')),
    Kind(21, 'FireSh', Effect(4, None), Potion5('p_fire_shield_b_A1_8', 'p_fire_shield_c_A1_8', 'p_fire_shield_s_A1_8', 'p_fire_shield_q_A1_8', 'p_fire_shield_e_A1_8', 'p_fire_shield_b', 'p_fire_shield_c', 'p_fire_shield_s', 'p_fire_shield_q', 'p_fire_shield_e', 'fire_shield')),
    Kind(22, 'FortAgil', Effect(79, 3), Potion5('p_fortify_agility_b_A1_8', 'p_fortify_agility_c_A1_8', 'p_fortify_agility_s_A1_8', 'p_fortify_agility_q_A1_8', 'p_fortify_agility_e_A1_8', 'p_fortify_agility_b', 'p_fortify_agility_c', 'p_fortify_agility_s', 'p_fortify_agility_q', 'p_fortify_agility_e', 'fortify_agility')),
    Kind(23, 'FortAttack', Effect(117, None), Potion5('p_fortify_attack_b_A1_8', 'p_fortify_attack_c_A1_8', 'p_fortify_attack_s_A1_8', 'p_fortify_attack_q_A1_8', 'p_fortify_attack_e_A1_8', 'p_fortify_attack_b_A1', 'p_fortify_attack_c_A1', 'p_fortify_attack_s_A1', 'p_fortify_attack_q_A1', 'p_fortify_attack_e', 'fortify_attack')),
    Kind(24, 'FortEndur', Effect(79, 5), Potion5('p_fortify_endurance_b_A1_8', 'p_fortify_endurance_c_A1_8', 'p_fortify_endurance_s_A1_8', 'p_fortify_endurance_q_A1_8', 'p_fortify_endurance_e_A1_8', 'p_fortify_endurance_b', 'p_fortify_endurance_c', 'p_fortify_endurance_s', 'p_fortify_endurance_q', 'p_fortify_endurance_e', 'fortify_endurance')),
    Kind(25, 'FortFatig', Effect(82, None), Potion5('p_fortify_fatigue_b_A1_8', 'p_fortify_fatigue_c_A1_8', 'p_fortify_fatigue_s_A1_8', 'p_fortify_fatigue_q_A1_8', 'p_fortify_fatigue_e_A1_8', 'p_fortify_fatigue_b', 'p_fortify_fatigue_c', 'p_fortify_fatigue_s', 'p_fortify_fatigue_q', 'p_fortify_fatigue_e', 'fortify_fatigue')),
    Kind(26, 'FortHealth', Effect(80, None), Potion5('p_fortify_health_b_A1_8', 'p_fortify_health_c_A1_8', 'p_fortify_health_s_A1_8', 'p_fortify_health_q_A1_8', 'p_fortify_health_e_A1_8', 'p_fortify_health_b', 'p_fortify_health_c', 'p_fortify_health_s', 'p_fortify_health_q', 'p_fortify_health_e', 'fortify_health')),
    Kind(27, 'FortIntel', Effect(79, 1), Potion5('p_fortify_intelligence_b_A1_8', 'p_fortify_intelligence_c_A1_8', 'p_fortify_intelligence_s_A1_8', 'p_fortify_intelligence_q_A1_8', 'p_fortify_intelligence_e_A1_8', 'p_fortify_intelligence_b', 'p_fortify_intelligence_c', 'p_fortify_intelligence_s', 'p_fortify_intelligence_q', 'p_fortify_intelligence_e', 'fortify_intelligence')),
    Kind(28, 'FortLuck', Effect(79, 7), Potion5('p_fortify_luck_b_A1_8', 'p_fortify_luck_c_A1_8', 'p_fortify_luck_s_A1_8', 'p_fortify_luck_q_A1_8', 'p_fortify_luck_e_A1_8', 'p_fortify_luck_b', 'p_fortify_luck_c', 'p_fortify_luck_s', 'p_fortify_luck_q', 'p_fortify_luck_e', 'fortify_luck')),
    Kind(29, 'FortPers', Effect(79, 6), Potion5('p_fortify_personality_b_A1_8', 'p_fortify_personality_c_A1_8', 'p_fortify_personality_s_A1_8', 'p_fortify_personality_q_A1_8', 'p_fortify_personality_e_A1_8', 'p_fortify_personality_b', 'p_fortify_personality_c', 'p_fortify_personality_s', 'p_fortify_personality_q', 'p_fortify_personality_e', 'fortify_personality')),
    Kind(30, 'FortSpeed', Effect(79, 4), Potion5('p_fortify_speed_b_A1_8', 'p_fortify_speed_c_A1_8', 'p_fortify_speed_s_A1_8', 'p_fortify_speed_q_A1_8', 'p_fortify_speed_e_A1_8', 'p_fortify_speed_b', 'p_fortify_speed_c', 'p_fortify_speed_s', 'p_fortify_speed_q', 'p_fortify_speed_e', 'fortify_speed')),
    Kind(31, 'FortStr', Effect(79, 0), Potion5('p_fortify_strength_b_A1_8', 'p_fortify_strength_c_A1_8', 'p_fortify_strength_s_A1_8', 'p_fortify_strength_q_A1_8', 'p_fortify_strength_e_A1_8', 'p_fortify_strength_b', 'p_fortify_strength_c', 'p_fortify_strength_s', 'p_fortify_strength_q', 'p_fortify_strength_e', 'fortify_strength')),
    Kind(32, 'FortWill', Effect(79, 2), Potion5('p_fortify_willpower_b_A1_8', 'p_fortify_willpower_c_A1_8', 'p_fortify_willpower_s_A1_8', 'p_fortify_willpower_q_A1_8', 'p_fortify_willpower_e_A1_8', 'p_fortify_willpower_b', 'p_fortify_willpower_c', 'p_fortify_willpower_s', 'p_fortify_willpower_q', 'p_fortify_willpower_e', 'fortify_willpower')),
    Kind(33, 'FrostResist', Effect(91, None), Potion5('p_frost_resistance_b_A1_8', 'p_frost_resistance_c_A1_8', 'p_frost_resistance_s_A1_8', 'p_frost_resistance_q_A1_8', 'p_frost_resistance_e_A1_8', 'p_frost_resistance_b', 'p_frost_resistance_c', 'p_frost_resistance_s', 'p_frost_resistance_q', 'p_frost_resistance_e', 'frost_resistance')),
    Kind(34, 'FrostSh', Effect(6, None), Potion5('p_frost_shield_b_A1_8', 'p_frost_shield_c_A1_8', 'p_frost_shield_s_A1_8', 'p_frost_shield_q_A1_8', 'p_frost_shield_e_A1_8', 'p_frost_shield_b', 'p_frost_shield_c', 'p_frost_shield_s', 'p_frost_shield_q', 'p_frost_shield_e', 'frost_shield')),
    Kind(35, 'Invis', Effect(39, None), Potion5('p_invisibility_b_A1_8', 'p_invisibility_c_A1_8', 'p_invisibility_s_A1_8', 'p_invisibility_q_A1_8', 'p_invisibility_e_A1_8', 'p_invisibility_b', 'p_invisibility_c', 'p_invisibility_s', 'p_invisibility_q', 'p_invisibility_e', 'invisibility')),
    Kind(36, 'LightSh', Effect(5, None), Potion5('"p_lightning shield_b_A1_8"', '"p_lightning shield_c_A1_8"', '"p_lightning shield_s_A1_8"', '"p_lightning shield_q_A1_8"', '"p_lightning shield_e_A1_8"', '"p_lightning shield_b"', '"p_lightning shield_c"', '"p_lightning shield_s"', '"p_lightning shield_q"', '"p_lightning shield_e"', 'lightning_shield')),
    Kind(37, 'MagicResist', Effect(93, None), Potion5('p_magicka_resistance_b_A1_8', 'p_magicka_resistance_c_A1_8', 'p_magicka_resistance_s_A1_8', 'p_magicka_resistance_q_A1_8', 'p_magicka_resistance_e_A1_8', 'p_magicka_resistance_b', 'p_magicka_resistance_c', 'p_magicka_resistance_s', 'p_magicka_resistance_q', 'p_magicka_resistance_e', 'magicka_resistance')),
    Kind(38, 'PoisonResist', Effect(97, None), Potion5('p_poison_resistance_b_A1_8', 'p_poison_resistance_c_A1_8', 'p_poison_resistance_s_A1_8', 'p_poison_resistance_q_A1_8', 'p_poison_resistance_e_A1_8', 'p_poison_resistance_b', 'p_poison_resistance_c', 'p_poison_resistance_s', 'p_poison_resistance_q', 'p_poison_resistance_e', 'poison_resistance')),
    Kind(39, 'Reflect', Effect(68, None), Potion5('p_reflection_b_A1_8', 'p_reflection_c_A1_8', 'p_reflection_s_A1_8', 'p_reflection_q_A1_8', 'p_reflection_e_A1_8', 'p_reflection_b', 'p_reflection_c', 'p_reflection_s', 'p_reflection_q', 'p_reflection_e', 'reflection')),
    Kind(40, 'RestoreAgility', Effect(74, 3), Potion5('p_restore_agility_b_A1_8', 'p_restore_agility_c_A1_8', 'p_restore_agility_s_A1_8', 'p_restore_agility_q_A1_8', 'p_restore_agility_e_A1_8', 'p_restore_agility_b', 'p_restore_agility_c', 'p_restore_agility_s', 'p_restore_agility_q', 'p_restore_agility_e', 'restore_agility')),
    Kind(41, 'RestoreEndur', Effect(74, 5), Potion5('p_restore_endurance_b_A1_8', 'p_restore_endurance_c_A1_8', 'p_restore_endurance_s_A1_8', 'p_restore_endurance_q_A1_8', 'p_restore_endurance_e_A1_8', 'p_restore_endurance_b', 'p_restore_endurance_c', 'p_restore_endurance_s', 'p_restore_endurance_q', 'p_restore_endurance_e', 'restore_endurance')),
    Kind(42, 'RestoreIntel', Effect(74, 1), Potion5('p_restore_intelligence_b_A1_8', 'p_restore_intelligence_c_A1_8', 'p_restore_intelligence_s_A1_8', 'p_restore_intelligence_q_A1_8', 'p_restore_intelligence_e_A1_8', 'p_restore_intelligence_b', 'p_restore_intelligence_c', 'p_restore_intelligence_s', 'p_restore_intelligence_q', 'p_restore_intelligence_e', 'restore_intelligence')),
    Kind(43, 'RestoreLuck', Effect(74, 7), Potion5('p_restore_luck_b_A1_8', 'p_restore_luck_c_A1_8', 'p_restore_luck_s_A1_8', 'p_restore_luck_q_A1_8', 'p_restore_luck_e_A1_8', 'p_restore_luck_b', 'p_restore_luck_c', 'p_restore_luck_s', 'p_restore_luck_q', 'p_restore_luck_e', 'restore_luck')),
    Kind(44, 'RestoreSpeed', Effect(74, 4), Potion5('p_restore_speed_b_A1_8', 'p_restore_speed_c_A1_8', 'p_restore_speed_s_A1_8', 'p_restore_speed_q_A1_8', 'p_restore_speed_e_A1_8', 'p_restore_speed_b', 'p_restore_speed_c', 'p_restore_speed_s', 'p_restore_speed_q', 'p_restore_speed_e', 'restore_speed')),
    Kind(45, 'RestoreStr', Effect(74, 0), Potion5('p_restore_strength_b_A1_8', 'p_restore_strength_c_A1_8', 'p_restore_strength_s_A1_8', 'p_restore_strength_q_A1_8', 'p_restore_strength_e_A1_8', 'p_restore_strength_b', 'p_restore_strength_c', 'p_restore_strength_s', 'p_restore_strength_q', 'p_restore_strength_e', 'restore_strength')),
    Kind(46, 'RestoreWill', Effect(74, 2), Potion5('p_restore_willpower_b_A1_8', 'p_restore_willpower_c_A1_8', 'p_restore_willpower_s_A1_8', 'p_restore_willpower_q_A1_8', 'p_restore_willpower_e_A1_8', 'p_restore_willpower_b', 'p_restore_willpower_c', 'p_restore_willpower_s', 'p_restore_willpower_q', 'p_restore_willpower_e', 'restore_willpower')),
    Kind(47, 'SpellAbs', Effect(67, None), Potion5('p_spell_absorption_b_A1_8', 'p_spell_absorption_c_A1_8', 'p_spell_absorption_s_A1_8', 'p_spell_absorption_q_A1_8', 'p_spell_absorption_e_A1_8', 'p_spell_absorption_b', 'p_spell_absorption_c', 'p_spell_absorption_s', 'p_spell_absorption_q', 'p_spell_absorption_e', 'spell_absorption')),
    Kind(48, 'SwitfSwim', Effect(1, None), Potion5('p_swift_swim_b_A1_8', 'p_swift_swim_c_A1_8', 'p_swift_swim_s_A1_8', 'p_swift_swim_q_A1_8', 'p_swift_swim_e_A1_8', 'p_swift_swim_b', 'p_swift_swim_c', 'p_swift_swim_s_A1', 'p_swift_swim_q', 'p_swift_swim_e', 'swift_swim')),
]

std_kinds = [
    Kind(49, 'ResCom', Effect(94, None), Potion5('p_disease_resistance_b_A1_8', 'p_disease_resistance_c_A1_8', 'p_disease_resistance_s_A1_8', 'p_disease_resistance_q_A1_8', 'p_disease_resistance_e_A1_8', 'p_disease_resistance_b', 'p_disease_resistance_c', 'p_disease_resistance_s', 'p_disease_resistance_q', 'p_disease_resistance_e', 'disease_resistance')),
]

eva_kinds = [
    Kind(49, 'Mark', Effect(60, None), Potion2('p_mark_s_A1_16', 'p_mark_s', 'mark', 40)),
    Kind(50, 'Recall', Effect(61, None), Potion2('p_recall_s_A1_16', 'p_recall_s', 'recall', 80)),
    Kind(51, 'ResCom', Effect(94, None), Potion5('p_disease_resistance_b_A1_8', 'p_disease_resistance_c_A1_8', 'p_disease_resistance_s_A1_8', 'p_disease_resistance_q_A1_8', 'p_disease_resistance_e_A1_8', 'p_disease_resistance_b', 'p_disease_resistance_c', 'p_disease_resistance_s', 'p_disease_resistance_q', 'p_disease_resistance_e', 'disease_resistance')),
]

kinds = list(chain(base_kinds, std_kinds))
kinds_eva = list(chain(base_kinds, eva_kinds))

positive_effects = list(map(lambda x: x.effect, kinds))
positive_effects_eva = list(map(lambda x: x.effect, kinds_eva))

def effect_value(effect, eva):
    if effect in negative_effects:
        return -1
    if effect in (neutral_effects_eva if eva else neutral_effects):
        return 0
    if effect in (positive_effects_eva if eva else positive_effects):
        return 1
    print('unknown effect ' + str(effect))
    sys.exit(1)

Ingredient = namedtuple('Ingredient', ['name', 'modl', 'itex', 'effects'])

def level(ingr, kind):
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

def parse_tes3(path):
    f = open(path, 'r')
    pos = f.tell()
    ingr = False
    while True:
        line = f.readline()
        newpos = f.tell()
        if newpos == pos:
            if ingr and not scri:
                yield Ingredient(name, modl, itex, effects)
            break
        pos = newpos
        line = line[:-1]
        if not ingr:
            if line == 'INGR' or line.startswith('INGR '):
                name = ''
                modl = ''
                itex = ''
                scri = False
                effects = None
                ingr = True
        else:
            if line.startswith('SCRI '):
                scri = True
            elif line.startswith('NAME '):
                name = line[len('NAME '):]
            elif line.startswith('MODL '):
                modl = line[len('MODL '):]
            elif line.startswith('ITEX '):
                itex = line[len('ITEX '):]
            elif line == 'IRDT':
                f.readline();
                ids = map(int, f.readline()[4:-1].split(' '));
                specs1 = map(int, f.readline()[4:-1].split(' '));
                specs2 = map(int, f.readline()[4:-1].split(' '));
                effects = list(map(lambda x: None if x[0] < 0 else Effect(x[0], x[1] if x[0] == 21 else x[2] if x[0] == 74 or x[0] == 79 or x[0] == 17 or x[0] == 22 else None), zip(ids, specs1, specs2)))
            elif not line:
                ingr = False
                if not scri:
                    yield Ingredient(name, modl, itex, effects)

def check_h_not_contains(s, eva):
    f = open('../' + ('h_eva' if eva else 'h'), 'r')
    pos = f.tell()
    while True:
        line = f.readline()
        newpos = f.tell()
        if newpos == pos:
            break
        pos = newpos
        line = line[:-1]
        if s in line:
            print('check_h_not_contains failed: ' + s)
            return False
    return True
    
def same_group(ingr1, ingr2, eva):
    return same_ingr(ingr1, ingr2) or list(filter(lambda x: x[0] == x[1] and x[0] != None and effect_value(x[0], eva) < 0, product(ingr1.effects, ingr2.effects)))

def pair_level(pair, kind):
    l1 = level(pair[0], kind)
    l2 = level(pair[1], kind)
    if l1 < l2:
        return l2
    else:
        return l1

def group_ingredients(ingrs, kind, eva):
    if len(ingrs) < 2:
        return None
    if len(ingrs) == 2:
        if same_group(ingrs[0], ingrs[1], eva):
            return None
        return ([], [(ingrs[0], ingrs[1])])
    links = list(map(lambda i: set([i]), range(0, len(ingrs))))
    for pair in filter(lambda pair: same_group(ingrs[pair[0]], ingrs[pair[1]], eva), combinations(range(0, len(ingrs)), 2)):
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
    special_pairs = list(chain.from_iterable(map(lambda group: filter(lambda pair: not same_group(ingrs[pair[0]], ingrs[pair[1]], eva), combinations(group, 2)), groups)))
    return (
        list(map(lambda g: list(sorted(map(lambda i: ingrs[i], g), key=lambda i: level(i, kind))), groups)),
        list(sorted(map(lambda s: (ingrs[s[0]], ingrs[s[1]]), special_pairs), key=lambda p: pair_level(p, kind)))
    )

def gen_add_script(kind, ingrs, eva):
    (groups, pairs) = group_ingredients(ingrs, kind, eva)
    add_name = 'A1V6_AAdd' + str(kind.index) + '_' + kind.name + '_sc'
    check_name = 'A1V6_ACheck' + str(kind.index) + '_' + kind.name + '_sc'
    s = open(add_name, 'w')
    s.write('SCTX\n')
    s.write('    Begin ' + add_name + '\n')
    s.write('    \n')
    if groups:
        s.write('    short in\n')
    s.write('    short add\n')
    s.write('    short state\n')
    s.write('    \n')
    s.write('    short PCSkipEquip\n')
    s.write('    short OnPCEquip\n')
    s.write('    \n')
    s.write('    set PCSkipEquip to 1\n')
    s.write('    \n')
    s.write('    if ( state == 2 )\n')
    s.write('    	set ' + check_name + '.AddPotion to 1\n')
    s.write('    	StartScript A1V6_AlchemyCheck_sc\n')
    s.write('    	set state to 0\n')
    s.write('    	return\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    if ( state == 1 )\n')
    s.write('    	if ( ScriptRunning A1V6_CalcAlchemy' + ('2' if type(kind.potion) == Potion2 else '5') + '_sc == 0 )\n')
    s.write('    		set state to 2\n')
    s.write('    	endif\n')
    s.write('    	return\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    if ( OnPCEquip == 1 )\n')
    s.write('    set OnPCEquip to 0\n')
    s.write('    \n')
    s.write('    set add to 0\n')
    if groups:
        s.write('    set in to 0\n')
        s.write('    \n')
        n_in = 0;
        for g in range(0, len(groups)):
            if g == 1 and g == len(groups) - 1:
                s.write('    if ( in > 0 )\n')
            elif g == len(groups) - 1:
                s.write('    if ( add == 0 )\n')
                s.write('    	if ( in > 0 )\n')
            elif g > 1:
                s.write('    if ( add == 0 )\n')
            for i in range(0, len(groups[g])):
                n_in += 1
                if g == 0 and i == 0:
                    s.write('    if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in to 1\n')
                elif g == 0:
                    s.write('    elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in to ' + str(n_in) + '\n')
                elif g == 1 and i == 0 and g == len(groups) - 1:
                    s.write('    	if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    		set add to 1\n')
                    s.write('    		player->RemoveItem "' + groups[g][i].name + '", 1\n')
                elif g == 1 and g == len(groups) - 1:
                    s.write('    	elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    		set add to 1\n')
                    s.write('    		player->RemoveItem "' + groups[g][i].name + '", 1\n')
                elif g == 1 and i == 0:
                    s.write('    if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	if ( in > 0 )\n')
                    s.write('    		set add to 1\n')
                    s.write('    		player->RemoveItem "' + groups[g][i].name + '", 1\n')
                    s.write('    	else\n')
                    s.write('    		set in to ' + str(n_in) + '\n')
                    s.write('    	endif\n')
                elif g == 1:
                    s.write('    elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	if ( in > 0 )\n')
                    s.write('    		set add to 1\n')
                    s.write('    		player->RemoveItem "' + groups[g][i].name + '", 1\n')
                    s.write('    	else\n')
                    s.write('    		set in to ' + str(n_in) + '\n')
                    s.write('    	endif\n')
                elif i == 0 and g == len(groups) - 1:
                    s.write('    		if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    			set add to 1\n')
                    s.write('    			player->RemoveItem "' + groups[g][i].name + '", 1\n')
                elif i == 0:
                    s.write('    	if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    		if ( in > 0 )\n')
                    s.write('    			set add to 1\n')
                    s.write('    			player->RemoveItem "' + groups[g][i].name + '", 1\n')
                    s.write('    		else\n')
                    s.write('    			set in to ' + str(n_in) + '\n')
                    s.write('    		endif\n')
                elif g == len(groups) - 1:
                    s.write('    		elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    			set add to 1\n')
                    s.write('    			player->RemoveItem "' + groups[g][i].name + '", 1\n')
                else:
                    s.write('    	elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    		if ( in > 0 )\n')
                    s.write('    			set add to 1\n')
                    s.write('    			player->RemoveItem "' + groups[g][i].name + '", 1\n')
                    s.write('    		else\n')
                    s.write('    			set in to ' + str(n_in) + '\n')
                    s.write('    		endif\n')
            if g == 1 and g == len(groups) - 1:
                s.write('    	endif\n')
            elif g == len(groups) - 1:
                s.write('    		endif\n')
                s.write('    	endif\n')
            elif g > 1:
                s.write('    	endif\n')
            s.write('    endif\n')
        s.write('    \n')
        s.write('    if ( add == 1 )\n')
        max_in = n_in
        n_in = 0
        if max_in == 2:
            s.write('    	player->RemoveItem "' + groups[1][0].name + '", 1\n')
        else:
            for g in range(0, len(groups)):
                for i in range(0, len(groups[g])):
                    n_in += 1
                    if n_in == 1:
                        s.write('    	if ( in == 1 )\n')
                    elif n_in == max_in - 1:
                        s.write('    	else\n')
                    elif n_in != max_in:
                        s.write('    	elseif ( in == ' + str(n_in) + ' )\n')
                    if n_in != max_in:
                        s.write('    		player->RemoveItem "' + groups[g][i].name + '", 1\n')
            s.write('    	endif\n')
        s.write('    endif\n')
    n_pair = 0
    for p in pairs:
        n_pair += 1
        if not groups and n_pair == 1:
            s.write('    if ( player->GetItemCount "' + p[0].name + '" > 0 )\n')
            s.write('    	if ( player->GetItemCount "' + p[1].name + '" > 0 )\n')
            s.write('    		player->RemoveItem "' + p[0].name + '", 1\n')
            s.write('    		player->RemoveItem "' + p[1].name + '", 1\n')
            s.write('    		set add to 1\n')
            s.write('    	endif\n')
            s.write('    endif\n')
        else:
            s.write('    if ( add == 0 )\n')
            s.write('    	if ( player->GetItemCount "' + p[0].name + '" > 0 )\n')
            s.write('    		if ( player->GetItemCount "' + p[1].name + '" > 0 )\n')
            s.write('    			player->RemoveItem "' + p[0].name + '", 1\n')
            s.write('    			player->RemoveItem "' + p[1].name + '", 1\n')
            s.write('    			set add to 1\n')
            s.write('    		endif\n')
            s.write('    	endif\n')
            s.write('    endif\n')
    s.write('    if ( add == 1 )\n')
    s.write('    	set state to 1\n')
    if type(kind.potion) == Potion2:
        s.write('    	set A1V6_CalcAlchemy2_sc.pin to ' + str(kind.potion.difficulty) + '\n')
    s.write('    	set A1V6_CalcAlchemy' + ('2' if type(kind.potion) == Potion2 else '5') + '_sc.in to 2\n')
    s.write('    	set A1V6_CalcAlchemy' + ('2' if type(kind.potion) == Potion2 else '5') + ' to 1\n')
    s.write('    else\n')
    s.write('    	StartScript A1V6_AlchemyCheck_sc\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    End\n')
    return add_name

def gen_check2_script(kind, ingrs_15, ingrs_30, ingrs_45, ingrs_60, eva):
    ingrs = list(chain(ingrs_15, ingrs_30, ingrs_45, ingrs_60))
    (groups, pairs) = group_ingredients(ingrs, kind, eva)
    check_name = 'A1V6_ACheck' + str(kind.index) + '_' + kind.name + '_sc'
    s = open(check_name, 'w')
    s.write('SCTX\n')
    s.write('    Begin ' + check_name + '\n')
    s.write('    \n')
    s.write('    short AddPotion\n')
    if groups:
        if ingrs_15:
            s.write('    short in15\n')
        if ingrs_30:
            s.write('    short in30\n')
        if ingrs_45:
            s.write('    short in45\n')
        if ingrs_60:
            s.write('    short in60\n')
    if len(pairs) > 1:
        s.write('    short pair\n')
    s.write('    \n')
    s.write('    if ( AddPotion == 1 )\n')
    s.write('    	if ( A1V6_PotionB == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionB == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionB == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionB == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionB == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionB == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionB == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionB == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionC == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionC == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionC == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionC == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionC == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionC == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionC == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionC == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionS == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionS == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionS == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionS == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionS == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionS == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionS == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionS == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionQ == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionQ == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionQ == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionQ == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionQ == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionQ == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionQ == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionQ == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_1_16 + ', 8\n')
    s.write('    	endif\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    set AddPotion to 0\n')
    s.write('    \n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_1_16 + ' >= 16 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_1_16 + ', 16\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_1_16 + ' >= 16 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_1_16 + ', 16\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_1_16 + ' >= 16 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_1_16 + ', 16\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_1_16 + ' >= 16 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_1_16 + ', 16\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    ')
    if ingrs_15:
        s.write('if ( player->GetItemCount "A1V6_L15_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L15_' + kind.potion.id_base + '", 1\n')
        if ingrs_30 or ingrs_45 or ingrs_60:
            s.write('    else')
    if ingrs_30:
        s.write('if ( player->GetItemCount "A1V6_L30_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L30_' + kind.potion.id_base + '", 1\n')
        if ingrs_45 or ingrs_60:
            s.write('    else')
    if ingrs_45:
        s.write('if ( player->GetItemCount "A1V6_L45_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L45_' + kind.potion.id_base + '", 1\n')
        if ingrs_60:
            s.write('    else')
    if ingrs_60:
        s.write('if ( player->GetItemCount "A1V6_L60_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L60_' + kind.potion.id_base + '", 1\n')
    s.write('    endif\n')
    s.write('    \n')
    if groups:
        if ingrs_15:
            s.write('    set in15 to 0\n')
        if ingrs_30:
            s.write('    set in30 to 0\n')
        if ingrs_45:
            s.write('    set in45 to 0\n')
        if ingrs_60:
            s.write('    set in60 to 0\n')
        s.write('    \n')
        for g in range(0, len(groups)):
            for i in range(0, len(groups[g])):
                if g == 0 and i == 0:
                    s.write('    if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to 1\n')
                elif g == 0:
                    s.write('    elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to 1\n')
                elif i == 0:
                    s.write('    if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to ( in' + str(level(groups[g][i], kind)) + ' + 1 )\n')
                else:
                    s.write('    elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to ( in' + str(level(groups[g][i], kind)) + ' + 1 )\n')
            s.write('    endif\n')
        s.write('    \n')
        if ingrs_30 and ingrs_15:
            s.write('    set in30 to ( in30 + in15 )\n')
        if ingrs_45:
            if ingrs_30:
                s.write('    set in45 to ( in45 + in30 )\n')
            elif ingrs_15:
                s.write('    set in45 to ( in45 + in15 )\n')
        if ingrs_60:
            if ingrs_45:
                s.write('    set in60 to ( in60 + in45 )\n')
            elif ingrs_30:
                s.write('    set in60 to ( in60 + in30 )\n')
            elif ingrs_15:
                s.write('    set in60 to ( in60 + in15 )\n')
        s.write('    \n')
        s.write('    ')
        if ingrs_15:
            s.write('if ( in15 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L15_' + kind.potion.id_base + '", 1\n')
            if ingrs_30 or ingrs_45 or ingrs_60 or pairs:
                s.write('    else')
        if ingrs_30:
            s.write('if ( in30 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L30_' + kind.potion.id_base + '", 1\n')
            if ingrs_45 or ingrs_60 or pairs:
                s.write('    else')
        if ingrs_45:
            s.write('if ( in45 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L45_' + kind.potion.id_base + '", 1\n')
            if ingrs_60 or pairs:
                s.write('    else')
        if ingrs_60:
            s.write('if ( in60 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L60_' + kind.potion.id_base + '", 1\n')
            if pairs:
                s.write('    else')
    if pairs:
        if groups:
            s.write('\n')
        tabs = '	' if groups else ''
        if len(pairs) > 1:
            s.write('    ' + tabs + 'set pair to 0\n')
        n_pair = 0
        for p in pairs:
            n_pair += 1
            if n_pair == 1:
                s.write('    ' + tabs + 'if ( player->GetItemCount "' + p[0].name + '" > 0 )\n')
                s.write('    ' + tabs + '	if ( player->GetItemCount "' + p[1].name + '" > 0 )\n')
                s.write('    ' + tabs + '		player->AddItem "A1V6_L' + str(pair_level(p, kind)) + '_' + kind.potion.id_base + '", 1\n')
                if n_pair < len(pairs):
                    s.write('    ' + tabs + '		set pair to 1\n')
                s.write('    ' + tabs + '	endif\n')
                s.write('    ' + tabs + 'endif\n')
            else:
                s.write('    ' + tabs + 'if ( pair == 0 )\n')
                s.write('    ' + tabs + '	if ( player->GetItemCount "' + p[0].name + '" > 0 )\n')
                s.write('    ' + tabs + '		if ( player->GetItemCount "' + p[1].name + '" > 0 )\n')
                s.write('    ' + tabs + '			player->AddItem "A1V6_L' + str(pair_level(p, kind)) + '_' + kind.potion.id_base + '", 1\n')
                if n_pair < len(pairs):
                    s.write('    ' + tabs + '			set pair to 1\n')
                s.write('    ' + tabs + '		endif\n')
                s.write('    ' + tabs + '	endif\n')
                s.write('    ' + tabs + 'endif\n')
    if groups:
        s.write('    endif\n')
    s.write('    \n')
    s.write('    StopScript ' + check_name + '\n')
    all_kinds = kinds_eva if eva else kinds
    if kind.index < len(all_kinds):
        s.write('    StartScript A1V6_ACheck' + str(kind.index + 1) + '_' + all_kinds[kind.index].name + '_sc\n')
    else:
        s.write('    if ( A1V6_AlchemyRes == 0 )\n')
        s.write('    	MessageBox "Готово"\n')
        s.write('    elseif ( A1V6_AlchemyRes == 1 )\n')
        s.write('    	PlaySound "potion success"\n')
        s.write('    elseif ( A1V6_AlchemyRes == 2 )\n')
        s.write('    	PlaySound "potion fail"\n')
        s.write('    endif\n')
        s.write('    set A1V6_AlchemyRes to 0\n')
    s.write('    \n')
    s.write('    End\n')
    return check_name

def gen_check5_script(kind, ingrs_15, ingrs_30, ingrs_45, ingrs_60, eva):
    ingrs = list(chain(ingrs_15, ingrs_30, ingrs_45, ingrs_60))
    (groups, pairs) = group_ingredients(ingrs, kind, eva)
    check_name = 'A1V6_ACheck' + str(kind.index) + '_' + kind.name + '_sc'
    s = open(check_name, 'w')
    s.write('SCTX\n')
    s.write('    Begin ' + check_name + '\n')
    s.write('    \n')
    s.write('    short AddPotion\n')
    if groups:
        if ingrs_15:
            s.write('    short in15\n')
        if ingrs_30:
            s.write('    short in30\n')
        if ingrs_45:
            s.write('    short in45\n')
        if ingrs_60:
            s.write('    short in60\n')
    if len(pairs) > 1:
        s.write('    short pair\n')
    s.write('    \n')
    s.write('    if ( AddPotion == 1 )\n')
    s.write('    	if ( A1V6_PotionB == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionB == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionB == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionB == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionB == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionB == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionB == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionB == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_broken_1_8 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionC == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionC == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionC == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionC == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionC == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionC == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionC == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionC == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_cheap_1_8 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionS == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionS == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionS == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionS == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionS == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionS == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionS == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionS == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_standard_1_8 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionQ == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionQ == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionQ == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionQ == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionQ == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionQ == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionQ == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionQ == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_qualitative_1_8 + ', 8\n')
    s.write('    	endif\n')
    s.write('    	if ( A1V6_PotionE == 1 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 1\n')
    s.write('    	elseif ( A1V6_PotionE == 2 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 2\n')
    s.write('    	elseif ( A1V6_PotionE == 3 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 3\n')
    s.write('    	elseif ( A1V6_PotionE == 4 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 4\n')
    s.write('    	elseif ( A1V6_PotionE == 5 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 5\n')
    s.write('    	elseif ( A1V6_PotionE == 6 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 6\n')
    s.write('    	elseif ( A1V6_PotionE == 7 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 7\n')
    s.write('    	elseif ( A1V6_PotionE == 8 )\n')
    s.write('    		player->AddItem ' + kind.potion.id_exclusive_1_8 + ', 8\n')
    s.write('    	endif\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    set AddPotion to 0\n')
    s.write('    \n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_broken_1_8 + ' >= 8 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_broken_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_broken_1_8 + ', 8\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_cheap_1_8 + ' >= 8 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_cheap_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_cheap_1_8 + ', 8\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_standard_1_8 + ' >= 8 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_standard_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_standard_1_8 + ', 8\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_qualitative_1_8 + ' >= 8 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_qualitative_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_qualitative_1_8 + ', 8\n')
    s.write('    endif\n')
    s.write('    if ( player->GetItemCount ' + kind.potion.id_exclusive_1_8 + ' >= 8 )\n')
    s.write('    	player->AddItem ' + kind.potion.id_exclusive_1 + ', 1\n')
    s.write('    	player->RemoveItem ' + kind.potion.id_exclusive_1_8 + ', 8\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    ')
    if ingrs_15:
        s.write('if ( player->GetItemCount "A1V6_L15_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L15_' + kind.potion.id_base + '", 1\n')
        if ingrs_30 or ingrs_45 or ingrs_60:
            s.write('    else')
    if ingrs_30:
        s.write('if ( player->GetItemCount "A1V6_L30_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L30_' + kind.potion.id_base + '", 1\n')
        if ingrs_45 or ingrs_60:
            s.write('    else')
    if ingrs_45:
        s.write('if ( player->GetItemCount "A1V6_L45_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L45_' + kind.potion.id_base + '", 1\n')
        if ingrs_60:
            s.write('    else')
    if ingrs_60:
        s.write('if ( player->GetItemCount "A1V6_L60_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L60_' + kind.potion.id_base + '", 1\n')
    s.write('    endif\n')
    s.write('    \n')
    if groups:
        if ingrs_15:
            s.write('    set in15 to 0\n')
        if ingrs_30:
            s.write('    set in30 to 0\n')
        if ingrs_45:
            s.write('    set in45 to 0\n')
        if ingrs_60:
            s.write('    set in60 to 0\n')
        s.write('    \n')
        for g in range(0, len(groups)):
            for i in range(0, len(groups[g])):
                if g == 0 and i == 0:
                    s.write('    if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to 1\n')
                elif g == 0:
                    s.write('    elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to 1\n')
                elif i == 0:
                    s.write('    if ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to ( in' + str(level(groups[g][i], kind)) + ' + 1 )\n')
                else:
                    s.write('    elseif ( player->GetItemCount "' + groups[g][i].name + '" > 0 )\n')
                    s.write('    	set in' + str(level(groups[g][i], kind)) + ' to ( in' + str(level(groups[g][i], kind)) + ' + 1 )\n')
            s.write('    endif\n')
        s.write('    \n')
        if ingrs_30 and ingrs_15:
            s.write('    set in30 to ( in30 + in15 )\n')
        if ingrs_45:
            if ingrs_30:
                s.write('    set in45 to ( in45 + in30 )\n')
            elif ingrs_15:
                s.write('    set in45 to ( in45 + in15 )\n')
        if ingrs_60:
            if ingrs_45:
                s.write('    set in60 to ( in60 + in45 )\n')
            elif ingrs_30:
                s.write('    set in60 to ( in60 + in30 )\n')
            elif ingrs_15:
                s.write('    set in60 to ( in60 + in15 )\n')
        s.write('    \n')
        s.write('    ')
        if ingrs_15:
            s.write('if ( in15 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L15_' + kind.potion.id_base + '", 1\n')
            if ingrs_30 or ingrs_45 or ingrs_60 or pairs:
                s.write('    else')
        if ingrs_30:
            s.write('if ( in30 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L30_' + kind.potion.id_base + '", 1\n')
            if ingrs_45 or ingrs_60 or pairs:
                s.write('    else')
        if ingrs_45:
            s.write('if ( in45 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L45_' + kind.potion.id_base + '", 1\n')
            if ingrs_60 or pairs:
                s.write('    else')
        if ingrs_60:
            s.write('if ( in60 > 1 )\n')
            s.write('    	player->AddItem "A1V6_L60_' + kind.potion.id_base + '", 1\n')
            if pairs:
                s.write('    else')
    if pairs:
        if groups:
            s.write('\n')
        tabs = '	' if groups else ''
        if len(pairs) > 1:
            s.write('    ' + tabs + 'set pair to 0\n')
        n_pair = 0
        for p in pairs:
            n_pair += 1
            if n_pair == 1:
                s.write('    ' + tabs + 'if ( player->GetItemCount "' + p[0].name + '" > 0 )\n')
                s.write('    ' + tabs + '	if ( player->GetItemCount "' + p[1].name + '" > 0 )\n')
                s.write('    ' + tabs + '		player->AddItem "A1V6_L' + str(pair_level(p, kind)) + '_' + kind.potion.id_base + '", 1\n')
                if n_pair < len(pairs):
                    s.write('    ' + tabs + '		set pair to 1\n')
                s.write('    ' + tabs + '	endif\n')
                s.write('    ' + tabs + 'endif\n')
            else:
                s.write('    ' + tabs + 'if ( pair == 0 )\n')
                s.write('    ' + tabs + '	if ( player->GetItemCount "' + p[0].name + '" > 0 )\n')
                s.write('    ' + tabs + '		if ( player->GetItemCount "' + p[1].name + '" > 0 )\n')
                s.write('    ' + tabs + '			player->AddItem "A1V6_L' + str(pair_level(p, kind)) + '_' + kind.potion.id_base + '", 1\n')
                if n_pair < len(pairs):
                    s.write('    ' + tabs + '			set pair to 1\n')
                s.write('    ' + tabs + '		endif\n')
                s.write('    ' + tabs + '	endif\n')
                s.write('    ' + tabs + 'endif\n')
    if groups:
        s.write('    endif\n')
    s.write('    \n')
    s.write('    StopScript ' + check_name + '\n')
    all_kinds = kinds_eva if eva else kinds
    if kind.index < len(all_kinds):
        s.write('    StartScript A1V6_ACheck' + str(kind.index + 1) + '_' + all_kinds[kind.index].name + '_sc\n')
    else:
        s.write('    if ( A1V6_AlchemyRes == 0 )\n')
        s.write('    	MessageBox "Готово"\n')
        s.write('    elseif ( A1V6_AlchemyRes == 1 )\n')
        s.write('    	PlaySound "potion success"\n')
        s.write('    elseif ( A1V6_AlchemyRes == 2 )\n')
        s.write('    	PlaySound "potion fail"\n')
        s.write('    endif\n')
        s.write('    set A1V6_AlchemyRes to 0\n')
    s.write('    \n')
    s.write('    End\n')
    return check_name

def gen_del_script(kind, eva):
    del_name = 'A1V6_ADel' + str(kind.index) + '_' + kind.name + '_sc'
    s = open(del_name, 'w')
    s.write('SCTX\n')
    s.write('    Begin ' + del_name + '\n')
    s.write('    \n')
    s.write('    ')
    if ingrs_15:
        s.write('if ( player->GetItemCount "A1V6_L15_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L15_' + kind.potion.id_base + '", 1\n')
        if ingrs_30 or ingrs_45 or ingrs_60:
            s.write('    else')
    if ingrs_30:
        s.write('if ( player->GetItemCount "A1V6_L30_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L30_' + kind.potion.id_base + '", 1\n')
        if ingrs_45 or ingrs_60:
            s.write('    else')
    if ingrs_45:
        s.write('if ( player->GetItemCount "A1V6_L45_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L45_' + kind.potion.id_base + '", 1\n')
        if ingrs_60:
            s.write('    else')
    if ingrs_60:
        s.write('if ( player->GetItemCount "A1V6_L60_' + kind.potion.id_base + '" == 1 )\n')
        s.write('    	player->RemoveItem "A1V6_L60_' + kind.potion.id_base + '", 1\n')
    s.write('    endif\n')
    s.write('    \n')
    s.write('    StopScript ' + del_name + '\n')
    all_kinds = kinds_eva if eva else kinds
    if kind.index < len(all_kinds):
        s.write('    StartScript A1V6_ADel' + str(kind.index + 1) + '_' + all_kinds[kind.index].name + '_sc\n')
    else:
        s.write('    StartScript A1V6_ADelPlus\n')
    s.write('    \n')
    s.write('    End\n')
    return del_name

morrowind_ingrs = { i.name: i for i in parse_tes3('../ingredients/Morrowind') }
tribunal_ingrs = { i.name: i for i in parse_tes3('../ingredients/Tribunal') }
bloodmoon_ingrs = { i.name: i for i in parse_tes3('../ingredients/Bloodmoon') }
eva_ingrs = { i.name: i for i in parse_tes3('../ingredients/EVA') }

ingrs = morrowind_ingrs.copy()
ingrs.update(tribunal_ingrs)
ingrs.update(bloodmoon_ingrs)

ingrs_eva = ingrs.copy()
ingrs_eva.update(eva_ingrs)

if sys.argv[1] == 'eva':
    eva = True
elif sys.argv[1] == 'std':
    eva = False
else:
    print('Parameter required')
    sys.exit(1)

add_scripts = []
check_scripts = []
del_scripts = []
for kind in kinds_eva if eva else kinds:
    all_ingrs = sorted(list(filter(lambda x: kind.effect in x.effects, (ingrs_eva if eva else ingrs).values())), key=lambda x: x.name)
    ingrs_15 = list(filter(lambda x: kind.effect == x.effects[0], all_ingrs))
    ingrs_30 = list(filter(lambda x: kind.effect == x.effects[1] and kind.effect != x.effects[0], all_ingrs))
    ingrs_45 = list(filter(lambda x: kind.effect == x.effects[2] and kind.effect != x.effects[1] and kind.effect != x.effects[0], all_ingrs))
    ingrs_60 = list(filter(lambda x: kind.effect == x.effects[3] and kind.effect != x.effects[2] and kind.effect != x.effects[1] and kind.effect != x.effects[0], all_ingrs))
    l15_name = 'A1V6_L15_' + kind.potion.id_base
    if not ingrs_15 and not check_h_not_contains(l15_name, eva):
        sys.exit(1)
    l30_name = 'A1V6_L30_' + kind.potion.id_base
    if not ingrs_30 and not check_h_not_contains(l30_name, eva):
        sys.exit(1)
    l45_name = 'A1V6_L45_' + kind.potion.id_base
    if not ingrs_45 and not check_h_not_contains(l45_name, eva):
        sys.exit(1)
    l60_name = 'A1V6_L60_' + kind.potion.id_base
    if not ingrs_60 and not check_h_not_contains(l60_name, eva):
        sys.exit(1)
    all_ingrs = list(chain(ingrs_15, ingrs_30, ingrs_45, ingrs_60))
    add_scripts.append(gen_add_script(kind, all_ingrs, eva))
    check_scripts.append(
        gen_check2_script(kind, ingrs_15, ingrs_30, ingrs_45, ingrs_60, eva) if type(kind.potion) == Potion2 else
        gen_check5_script(kind, ingrs_15, ingrs_30, ingrs_45, ingrs_60, eva)
    )
    del_scripts.append(gen_del_script(kind, eva))

scripts_list = open('../' + ('scripts_eva' if eva else 'scripts') + '.list', 'w')
scripts_list.writelines(map(lambda x: x + '\n', check_scripts))
scripts_list.writelines(map(lambda x: x + '\n', add_scripts))
scripts_list.writelines(map(lambda x: x + '\n', del_scripts))
