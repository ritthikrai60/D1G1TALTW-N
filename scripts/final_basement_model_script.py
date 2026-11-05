# === UPDATED BASEMENT MODEL: TRUE 24-RISER CORE STAIR + 16-STEP SOUTH STAIR ===
# Clear scene
scene.clear()

# Ensure layers exist
layer_names = [l.name for l in layers]
for lname in ['Slabs', 'Columns', 'Stairs']:
    if lname not in layer_names:
        layers.append(Layer(lname))

# 1. SINGLE UNIFIED CONTINUOUS BASEMENT SLAB (NO ELEVATION DIFFERENCE)
g_slab = extrude([(-26.0, -0.35), (-18.849, -15.533), (-18.913, -17.107), (-18.132, -17.136), (-17.351, -17.162), (-16.57, -17.183), (-15.789, -17.2), (-15.007, -17.211), (-14.226, -17.22), (-13.444, -17.224), (-12.663, -17.223), (-11.881, -17.219), (-11.1, -17.209), (-10.319, -17.195), (-9.537, -17.179), (-8.756, -17.156), (-7.975, -17.13), (-7.193, -17.099), (-6.413, -17.064), (-5.632, -17.025), (-4.852, -16.982), (-4.072, -16.933), (-3.292, -16.881), (-2.512, -16.825), (-1.734, -16.764), (-0.955, -16.699), (-0.177, -16.629), (0.602, -16.556), (1.379, -16.478), (2.157, -16.396), (2.934, -16.31), (3.709, -16.219), (3.71, -14.0), (2.0, -14.0), (2.0, -22.0), (10.0, -22.0), (10.0, -14.0), (14.0, -10.0), (66.0, 6.0), (66.0, 22.0), (32.0, 22.0), (32.0, 44.0), (-26.0, 44.0)], -0.20, 0.0, name='Basement_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))
g_slab.layer = 'Slabs'

# 2. ALL 77 STRUCTURAL COLUMNS (EXTRUDE Z: 0.00 -> +3.50m)
g_col_0 = extrude([(6.111, 7.425), (6.41, 7.4), (6.434, 7.7), (6.135, 7.723)], 0.0, 3.50, name='Col_00_A-col_0', color=(0.88, 0.86, 0.84, 1.0))
g_col_0.layer = 'Columns'
g_col_1 = extrude([(9.274, 3.663), (9.25, 3.364), (9.45, 3.348), (9.473, 3.647)], 0.0, 3.50, name='Col_01_A-col_16', color=(0.88, 0.86, 0.84, 1.0))
g_col_1.layer = 'Columns'
g_col_2 = extrude([(-17.993, -5.148), (-18.443, -5.132), (-18.468, -5.78), (-18.018, -5.798)], 0.0, 3.50, name='Col_02_A-col_17', color=(0.88, 0.86, 0.84, 1.0))
g_col_2.layer = 'Columns'
g_col_3 = extrude([(46.756, 8.925), (46.965, 8.526), (47.54, 8.828), (47.333, 9.227)], 0.0, 3.50, name='Col_03_A-col_18', color=(0.88, 0.86, 0.84, 1.0))
g_col_3.layer = 'Columns'
g_col_4 = extrude([(55.57, 20.264), (55.818, 19.889), (56.193, 20.137), (55.945, 20.512)], 0.0, 3.50, name='Col_04_A-col_19', color=(0.88, 0.86, 0.84, 1.0))
g_col_4.layer = 'Columns'
g_col_5 = extrude([(58.328, 16.093), (58.577, 15.719), (58.951, 15.966), (58.704, 16.342)], 0.0, 3.50, name='Col_05_A-col_20', color=(0.88, 0.86, 0.84, 1.0))
g_col_5.layer = 'Columns'
g_col_6 = extrude([(63.713, 7.954), (63.961, 7.578), (64.336, 7.827), (64.088, 8.202)], 0.0, 3.50, name='Col_06_A-col_21', color=(0.88, 0.86, 0.84, 1.0))
g_col_6.layer = 'Columns'
g_col_7 = extrude([(50.018, 16.811), (50.245, 16.423), (50.634, 16.651), (50.405, 17.038)], 0.0, 3.50, name='Col_07_A-col_22', color=(0.88, 0.86, 0.84, 1.0))
g_col_7.layer = 'Columns'
g_col_8 = extrude([(52.554, 12.501), (52.782, 12.114), (53.171, 12.343), (52.942, 12.73)], 0.0, 3.50, name='Col_08_A-col_23', color=(0.88, 0.86, 0.84, 1.0))
g_col_8.layer = 'Columns'
g_col_9 = extrude([(57.506, 4.091), (57.734, 3.703), (58.122, 3.932), (57.893, 4.319)], 0.0, 3.50, name='Col_09_A-col_24', color=(0.88, 0.86, 0.84, 1.0))
g_col_9.layer = 'Columns'
g_col_10 = extrude([(51.557, 0.906), (51.158, 0.699), (51.458, 0.122), (51.857, 0.331)], 0.0, 3.50, name='Col_10_A-col_25', color=(0.88, 0.86, 0.84, 1.0))
g_col_10.layer = 'Columns'
g_col_11 = extrude([(44.381, 13.698), (44.59, 13.299), (44.989, 13.508), (44.78, 13.907)], 0.0, 3.50, name='Col_11_A-col_26', color=(0.88, 0.86, 0.84, 1.0))
g_col_11.layer = 'Columns'
g_col_12 = extrude([(41.475, -3.866), (41.061, -4.041), (41.314, -4.639), (41.729, -4.464)], 0.0, 3.50, name='Col_12_A-col_27', color=(0.88, 0.86, 0.84, 1.0))
g_col_12.layer = 'Columns'
g_col_13 = extrude([(37.67, 5.122), (37.255, 4.946), (37.508, 4.348), (37.923, 4.524)], 0.0, 3.50, name='Col_13_A-col_28', color=(0.88, 0.86, 0.84, 1.0))
g_col_13.layer = 'Columns'
g_col_14 = extrude([(35.345, 9.459), (35.52, 9.044), (35.935, 9.219), (35.759, 9.634)], 0.0, 3.50, name='Col_14_A-col_29', color=(0.88, 0.86, 0.84, 1.0))
g_col_14.layer = 'Columns'
g_col_15 = extrude([(26.139, 5.527), (26.566, 5.667), (26.428, 6.094), (25.999, 5.956)], 0.0, 3.50, name='Col_15_A-col_30', color=(0.88, 0.86, 0.84, 1.0))
g_col_15.layer = 'Columns'
g_col_16 = extrude([(27.747, 0.686), (28.175, 0.828), (27.97, 1.445), (27.543, 1.303)], 0.0, 3.50, name='Col_16_A-col_31', color=(0.88, 0.86, 0.84, 1.0))
g_col_16.layer = 'Columns'
g_col_17 = extrude([(30.823, -8.576), (31.25, -8.435), (31.045, -7.818), (30.619, -7.959)], 0.0, 3.50, name='Col_17_A-col_32', color=(0.88, 0.86, 0.84, 1.0))
g_col_17.layer = 'Columns'
g_col_18 = extrude([(3.866, -13.757), (3.419, -13.811), (3.522, -14.655), (3.969, -14.6)], 0.0, 3.50, name='Col_18_A-col_33', color=(0.88, 0.86, 0.84, 1.0))
g_col_18.layer = 'Columns'
g_col_19 = extrude([(-7.239, -14.473), (-7.689, -14.492), (-7.646, -15.541), (-7.197, -15.523)], 0.0, 3.50, name='Col_19_A-col_34', color=(0.88, 0.86, 0.84, 1.0))
g_col_19.layer = 'Columns'
g_col_20 = extrude([(-7.63, -4.922), (-8.079, -4.94), (-8.036, -5.99), (-7.586, -5.971)], 0.0, 3.50, name='Col_20_A-col_35', color=(0.88, 0.86, 0.84, 1.0))
g_col_20.layer = 'Columns'
g_col_21 = extrude([(-18.35, -14.302), (-18.8, -14.284), (-18.849, -15.533), (-18.4, -15.551)], 0.0, 3.50, name='Col_21_A-col_36', color=(0.88, 0.86, 0.84, 1.0))
g_col_21.layer = 'Columns'
g_col_22 = extrude([(-19.666, 21.403), (-19.701, 20.954), (-19.252, 20.918), (-19.217, 21.367)], 0.0, 3.50, name='Col_22_A-col_37', color=(0.88, 0.86, 0.84, 1.0))
g_col_22.layer = 'Columns'
g_col_23 = extrude([(-21.504, 10.03), (-21.577, 9.587), (-21.133, 9.514), (-21.06, 9.958)], 0.0, 3.50, name='Col_23_A-col_38', color=(0.88, 0.86, 0.84, 1.0))
g_col_23.layer = 'Columns'
g_col_24 = extrude([(10.24, 19.034), (10.206, 18.586), (10.653, 18.55), (10.689, 18.998)], 0.0, 3.50, name='Col_24_A-col_39', color=(0.88, 0.86, 0.84, 1.0))
g_col_24.layer = 'Columns'
g_col_25 = extrude([(9.846, 14.05), (9.811, 13.601), (10.258, 13.566), (10.294, 14.015)], 0.0, 3.50, name='Col_25_A-col_40', color=(0.88, 0.86, 0.84, 1.0))
g_col_25.layer = 'Columns'
g_col_26 = extrude([(9.332, 7.571), (9.297, 7.122), (9.746, 7.086), (9.781, 7.535)], 0.0, 3.50, name='Col_26_A-col_41', color=(0.88, 0.86, 0.84, 1.0))
g_col_26.layer = 'Columns'
g_col_27 = extrude([(-14.225, 21.073), (-14.674, 21.108), (-14.725, 20.46), (-14.276, 20.424)], 0.0, 3.50, name='Col_27_A-col_42', color=(0.88, 0.86, 0.84, 1.0))
g_col_27.layer = 'Columns'
g_col_28 = extrude([(-0.18, 8.424), (-0.629, 8.46), (-0.679, 7.812), (-0.231, 7.776)], 0.0, 3.50, name='Col_28_A-col_43', color=(0.88, 0.86, 0.84, 1.0))
g_col_28.layer = 'Columns'
g_col_29 = extrude([(-5.164, 8.818), (-5.612, 8.854), (-5.664, 8.207), (-5.215, 8.171)], 0.0, 3.50, name='Col_29_A-col_44', color=(0.88, 0.86, 0.84, 1.0))
g_col_29.layer = 'Columns'
g_col_30 = extrude([(-10.148, 9.213), (-10.597, 9.249), (-10.648, 8.601), (-10.199, 8.565)], 0.0, 3.50, name='Col_30_A-col_45', color=(0.88, 0.86, 0.84, 1.0))
g_col_30.layer = 'Columns'
g_col_31 = extrude([(-15.133, 9.608), (-15.581, 9.644), (-15.633, 8.996), (-15.184, 8.96)], 0.0, 3.50, name='Col_31_A-col_46', color=(0.88, 0.86, 0.84, 1.0))
g_col_31.layer = 'Columns'
g_col_32 = extrude([(-22.313, 5.079), (-22.386, 4.635), (-21.941, 4.562), (-21.868, 5.006)], 0.0, 3.50, name='Col_32_A-col_47', color=(0.88, 0.86, 0.84, 1.0))
g_col_32.layer = 'Columns'
g_col_33 = extrude([(4.805, 8.029), (4.356, 8.065), (4.305, 7.417), (4.753, 7.381)], 0.0, 3.50, name='Col_33_A-col_48', color=(0.88, 0.86, 0.84, 1.0))
g_col_33.layer = 'Columns'
g_col_34 = extrude([(-15.984, 4.56), (-16.019, 4.111), (-15.571, 4.076), (-15.535, 4.525)], 0.0, 3.50, name='Col_34_A-col_49', color=(0.88, 0.86, 0.84, 1.0))
g_col_34.layer = 'Columns'
g_col_35 = extrude([(-10.999, 4.165), (-11.035, 3.716), (-10.587, 3.681), (-10.551, 4.13)], 0.0, 3.50, name='Col_35_A-col_50', color=(0.88, 0.86, 0.84, 1.0))
g_col_35.layer = 'Columns'
g_col_36 = extrude([(-6.016, 3.77), (-6.05, 3.321), (-5.602, 3.286), (-5.567, 3.735)], 0.0, 3.50, name='Col_36_A-col_51', color=(0.88, 0.86, 0.84, 1.0))
g_col_36.layer = 'Columns'
g_col_37 = extrude([(-1.031, 3.375), (-1.067, 2.927), (-0.618, 2.892), (-0.582, 3.34)], 0.0, 3.50, name='Col_37_A-col_52', color=(0.88, 0.86, 0.84, 1.0))
g_col_37.layer = 'Columns'
g_col_38 = extrude([(3.954, 2.981), (3.918, 2.532), (4.367, 2.497), (4.402, 2.946)], 0.0, 3.50, name='Col_38_A-col_53', color=(0.88, 0.86, 0.84, 1.0))
g_col_38.layer = 'Columns'
g_col_39 = extrude([(-23.726, -14.594), (-24.174, -14.559), (-24.225, -15.207), (-23.777, -15.243)], 0.0, 3.50, name='Col_39_A-col_54', color=(0.88, 0.86, 0.84, 1.0))
g_col_39.layer = 'Columns'
g_col_40 = extrude([(-22.571, 0.016), (-23.02, 0.051), (-23.071, -0.597), (-22.622, -0.633)], 0.0, 3.50, name='Col_40_A-col_55', color=(0.88, 0.86, 0.84, 1.0))
g_col_40.layer = 'Columns'
g_col_41 = extrude([(-17.801, -0.254), (-18.251, -0.236), (-18.3, -1.484), (-17.85, -1.502)], 0.0, 3.50, name='Col_41_A-col_56', color=(0.88, 0.86, 0.84, 1.0))
g_col_41.layer = 'Columns'
g_col_42 = extrude([(-7.821, -0.226), (-8.271, -0.244), (-8.244, -0.894), (-7.795, -0.875)], 0.0, 3.50, name='Col_42_A-col_57', color=(0.88, 0.86, 0.84, 1.0))
g_col_42.layer = 'Columns'
g_col_43 = extrude([(2.703, -4.167), (2.256, -4.221), (2.359, -5.066), (2.806, -5.011)], 0.0, 3.50, name='Col_43_A-col_58', color=(0.88, 0.86, 0.84, 1.0))
g_col_43.layer = 'Columns'
g_col_44 = extrude([(2.125, 0.597), (1.677, 0.543), (1.756, -0.101), (2.203, -0.047)], 0.0, 3.50, name='Col_44_A-col_59', color=(0.88, 0.86, 0.84, 1.0))
g_col_44.layer = 'Columns'
g_col_45 = extrude([(7.065, 1.306), (6.621, 1.234), (6.725, 0.593), (7.169, 0.665)], 0.0, 3.50, name='Col_45_A-col_60', color=(0.88, 0.86, 0.84, 1.0))
g_col_45.layer = 'Columns'
g_col_46 = extrude([(7.833, -3.432), (7.389, -3.504), (7.525, -4.343), (7.969, -4.27)], 0.0, 3.50, name='Col_46_A-col_61', color=(0.88, 0.86, 0.84, 1.0))
g_col_46.layer = 'Columns'
g_col_47 = extrude([(9.379, -12.967), (8.934, -13.039), (9.071, -13.878), (9.515, -13.806)], 0.0, 3.50, name='Col_47_A-col_62', color=(0.88, 0.86, 0.84, 1.0))
g_col_47.layer = 'Columns'
g_col_48 = extrude([(20.287, -10.729), (19.85, -10.837), (20.053, -11.662), (20.49, -11.555)], 0.0, 3.50, name='Col_48_A-col_63', color=(0.88, 0.86, 0.84, 1.0))
g_col_48.layer = 'Columns'
g_col_49 = extrude([(17.985, -1.348), (17.548, -1.455), (17.75, -2.28), (18.187, -2.173)], 0.0, 3.50, name='Col_49_A-col_64', color=(0.88, 0.86, 0.84, 1.0))
g_col_49.layer = 'Columns'
g_col_50 = extrude([(16.84, 3.314), (16.403, 3.206), (16.561, 2.575), (16.997, 2.683)], 0.0, 3.50, name='Col_50_A-col_65', color=(0.88, 0.86, 0.84, 1.0))
g_col_50.layer = 'Columns'
g_col_51 = extrude([(-19.993, 16.493), (-20.437, 16.566), (-20.542, 15.925), (-20.098, 15.852)], 0.0, 3.50, name='Col_51_A-col_66', color=(0.88, 0.86, 0.84, 1.0))
g_col_51.layer = 'Columns'
g_col_52 = extrude([(-22.939, -4.666), (-23.388, -4.63), (-23.471, -5.678), (-23.022, -5.713)], 0.0, 3.50, name='Col_52_A-col_67', color=(0.88, 0.86, 0.84, 1.0))
g_col_52.layer = 'Columns'
g_col_53 = extrude([(-9.24, 20.678), (-9.689, 20.713), (-9.74, 20.065), (-9.292, 20.029)], 0.0, 3.50, name='Col_53_A-col_68', color=(0.88, 0.86, 0.84, 1.0))
g_col_53.layer = 'Columns'
g_col_54 = extrude([(-4.256, 20.283), (-4.704, 20.318), (-4.756, 19.671), (-4.307, 19.635)], 0.0, 3.50, name='Col_54_A-col_69', color=(0.88, 0.86, 0.84, 1.0))
g_col_54.layer = 'Columns'
g_col_55 = extrude([(0.728, 19.889), (0.279, 19.923), (0.229, 19.276), (0.677, 19.24)], 0.0, 3.50, name='Col_55_A-col_70', color=(0.88, 0.86, 0.84, 1.0))
g_col_55.layer = 'Columns'
g_col_56 = extrude([(5.713, 19.494), (5.264, 19.529), (5.212, 18.881), (5.661, 18.845)], 0.0, 3.50, name='Col_56_A-col_71', color=(0.88, 0.86, 0.84, 1.0))
g_col_56.layer = 'Columns'
g_col_57 = extrude([(-14.873, 42.632), (-14.873, 43.082), (-15.323, 43.082), (-15.323, 42.632)], 0.0, 3.50, name='Col_57_P-1_0', color=(0.88, 0.86, 0.84, 1.0))
g_col_57.layer = 'Columns'
g_col_58 = extrude([(-16.572, 35.632), (-16.572, 36.082), (-17.023, 36.082), (-17.023, 35.632)], 0.0, 3.50, name='Col_58_P-1_1', color=(0.88, 0.86, 0.84, 1.0))
g_col_58.layer = 'Columns'
g_col_59 = extrude([(-18.273, 27.632), (-18.273, 28.082), (-18.723, 28.082), (-18.723, 27.632)], 0.0, 3.50, name='Col_59_P-1_2', color=(0.88, 0.86, 0.84, 1.0))
g_col_59.layer = 'Columns'
g_col_60 = extrude([(10.727, 42.632), (10.727, 43.082), (10.076, 43.082), (10.076, 42.632)], 0.0, 3.50, name='Col_60_P-1_3', color=(0.88, 0.86, 0.84, 1.0))
g_col_60.layer = 'Columns'
g_col_61 = extrude([(0.727, 42.632), (0.727, 43.082), (0.077, 43.082), (0.077, 42.632)], 0.0, 3.50, name='Col_61_P-1_16', color=(0.88, 0.86, 0.84, 1.0))
g_col_61.layer = 'Columns'
g_col_62 = extrude([(0.627, 35.532), (0.627, 36.182), (0.177, 36.182), (0.177, 35.532)], 0.0, 3.50, name='Col_62_P-1_17', color=(0.88, 0.86, 0.84, 1.0))
g_col_62.layer = 'Columns'
g_col_63 = extrude([(10.627, 35.532), (10.627, 36.182), (10.177, 36.182), (10.177, 35.532)], 0.0, 3.50, name='Col_63_P-1_18', color=(0.88, 0.86, 0.84, 1.0))
g_col_63.layer = 'Columns'
g_col_64 = extrude([(0.627, 27.532), (0.627, 28.182), (0.177, 28.182), (0.177, 27.532)], 0.0, 3.50, name='Col_64_P-1_21', color=(0.88, 0.86, 0.84, 1.0))
g_col_64.layer = 'Columns'
g_col_65 = extrude([(10.627, 27.532), (10.627, 28.182), (10.177, 28.182), (10.177, 27.532)], 0.0, 3.50, name='Col_65_P-1_22', color=(0.88, 0.86, 0.84, 1.0))
g_col_65.layer = 'Columns'
g_col_66 = extrude([(-9.373, 27.532), (-9.373, 28.182), (-9.822, 28.182), (-9.822, 27.532)], 0.0, 3.50, name='Col_66_P-1_23', color=(0.88, 0.86, 0.84, 1.0))
g_col_66.layer = 'Columns'
g_col_67 = extrude([(20.726, 42.632), (20.726, 43.082), (20.077, 43.082), (20.077, 42.632)], 0.0, 3.50, name='Col_67_P-1_24', color=(0.88, 0.86, 0.84, 1.0))
g_col_67.layer = 'Columns'
g_col_68 = extrude([(30.727, 42.632), (30.727, 43.082), (30.077, 43.082), (30.077, 42.632)], 0.0, 3.50, name='Col_68_P-1_25', color=(0.88, 0.86, 0.84, 1.0))
g_col_68.layer = 'Columns'
g_col_69 = extrude([(20.726, 35.632), (20.726, 36.082), (20.077, 36.082), (20.077, 35.632)], 0.0, 3.50, name='Col_69_P-1_26', color=(0.88, 0.86, 0.84, 1.0))
g_col_69.layer = 'Columns'
g_col_70 = extrude([(30.727, 35.632), (30.727, 36.082), (30.077, 36.082), (30.077, 35.632)], 0.0, 3.50, name='Col_70_P-1_27', color=(0.88, 0.86, 0.84, 1.0))
g_col_70.layer = 'Columns'
g_col_71 = extrude([(20.726, 27.632), (20.726, 28.082), (20.077, 28.082), (20.077, 27.632)], 0.0, 3.50, name='Col_71_P-1_28', color=(0.88, 0.86, 0.84, 1.0))
g_col_71.layer = 'Columns'
g_col_72 = extrude([(30.727, 27.632), (30.727, 28.082), (30.077, 28.082), (30.077, 27.632)], 0.0, 3.50, name='Col_72_P-1_29', color=(0.88, 0.86, 0.84, 1.0))
g_col_72.layer = 'Columns'
g_col_73 = extrude([(20.726, 19.567), (20.726, 20.018), (20.077, 20.018), (20.077, 19.567)], 0.0, 3.50, name='Col_73_P-1_30', color=(0.88, 0.86, 0.84, 1.0))
g_col_73.layer = 'Columns'
g_col_74 = extrude([(30.727, 19.567), (30.727, 20.018), (30.077, 20.018), (30.077, 19.567)], 0.0, 3.50, name='Col_74_P-1_31', color=(0.88, 0.86, 0.84, 1.0))
g_col_74.layer = 'Columns'
g_col_75 = extrude([(-9.273, 42.632), (-9.273, 43.082), (-9.923, 43.082), (-9.923, 42.632)], 0.0, 3.50, name='Col_75_P-1_36', color=(0.88, 0.86, 0.84, 1.0))
g_col_75.layer = 'Columns'
g_col_76 = extrude([(-9.373, 35.532), (-9.373, 36.182), (-9.822, 36.182), (-9.822, 35.532)], 0.0, 3.50, name='Col_76_P-1_37', color=(0.88, 0.86, 0.84, 1.0))
g_col_76.layer = 'Columns'

# 3. INTERNAL CORE STAIRCASE (FULL 24 RISERS: 4 ENTRANCE + 10 NORTH + 10 SOUTH)
# Flight 1: 4 steps stepping East from corridor (0.00 -> +0.76m)
g_f1_0 = extrude([(8.075, -11.678), (7.954, -11.678), (8.195, -13.159), (8.075, -13.159)], 0.0, 0.19, name='Core_Stair_F1_Step_1', color=(0.82, 0.83, 0.85, 1.0))
g_f1_0.layer = 'Stairs'
g_f1_1 = extrude([(8.195, -13.159), (8.441, -13.119), (8.217, -11.737), (7.954, -11.678)], 0.0, 0.38, name='Core_Stair_F1_Step_2', color=(0.82, 0.83, 0.85, 1.0))
g_f1_1.layer = 'Stairs'
g_f1_2 = extrude([(8.441, -13.119), (8.688, -13.079), (8.465, -11.697), (8.217, -11.737)], 0.0, 0.57, name='Core_Stair_F1_Step_3', color=(0.82, 0.83, 0.85, 1.0))
g_f1_2.layer = 'Stairs'
g_f1_3 = extrude([(8.688, -13.079), (8.934, -13.039), (8.711, -11.657), (8.465, -11.697)], 0.0, 0.76, name='Core_Stair_F1_Step_4', color=(0.82, 0.83, 0.85, 1.0))
g_f1_3.layer = 'Stairs'

# Lower Intermediate Landing (+0.76m)
g_l_land = extrude([(8.934, -13.039), (10.619, -12.8), (10.6, -11.45), (8.711, -11.45)], 0.0, 0.76, name='Core_Stair_Lower_Landing', color=(0.80, 0.81, 0.83, 1.0))
g_l_land.layer = 'Stairs'

# Flight 2: 10 steps stepping North along East wall (+0.76m -> +2.13m, riser 0.137m)
g_f2_0 = extrude([(10.6, -11.45), (10.619, -11.247), (9.237, -11.47), (9.6, -11.45)], 0.0, 0.897, name='Core_Stair_F2_Step_1', color=(0.82, 0.83, 0.85, 1.0))
g_f2_0.layer = 'Stairs'
g_f2_1 = extrude([(10.619, -11.247), (10.579, -11.0), (9.197, -11.223), (9.237, -11.47)], 0.0, 1.034, name='Core_Stair_F2_Step_2', color=(0.82, 0.83, 0.85, 1.0))
g_f2_1.layer = 'Stairs'
g_f2_2 = extrude([(10.579, -11.0), (10.539, -10.752), (9.158, -10.977), (9.197, -11.223)], 0.0, 1.171, name='Core_Stair_F2_Step_3', color=(0.82, 0.83, 0.85, 1.0))
g_f2_2.layer = 'Stairs'
g_f2_3 = extrude([(10.539, -10.752), (10.499, -10.506), (9.118, -10.73), (9.158, -10.977)], 0.0, 1.308, name='Core_Stair_F2_Step_4', color=(0.82, 0.83, 0.85, 1.0))
g_f2_3.layer = 'Stairs'
g_f2_4 = extrude([(10.499, -10.506), (10.46, -10.259), (9.077, -10.483), (9.118, -10.73)], 0.0, 1.445, name='Core_Stair_F2_Step_5', color=(0.82, 0.83, 0.85, 1.0))
g_f2_4.layer = 'Stairs'
g_f2_5 = extrude([(10.46, -10.259), (10.419, -10.013), (9.037, -10.237), (9.077, -10.483)], 0.0, 1.582, name='Core_Stair_F2_Step_6', color=(0.82, 0.83, 0.85, 1.0))
g_f2_5.layer = 'Stairs'
g_f2_6 = extrude([(10.419, -10.013), (10.379, -9.766), (8.997, -9.989), (9.037, -10.237)], 0.0, 1.719, name='Core_Stair_F2_Step_7', color=(0.82, 0.83, 0.85, 1.0))
g_f2_6.layer = 'Stairs'
g_f2_7 = extrude([(10.379, -9.766), (10.339, -9.519), (8.958, -9.743), (8.997, -9.989)], 0.0, 1.856, name='Core_Stair_F2_Step_8', color=(0.82, 0.83, 0.85, 1.0))
g_f2_7.layer = 'Stairs'
g_f2_8 = extrude([(10.339, -9.519), (10.299, -9.272), (8.918, -9.496), (8.958, -9.743)], 0.0, 1.993, name='Core_Stair_F2_Step_9', color=(0.82, 0.83, 0.85, 1.0))
g_f2_8.layer = 'Stairs'
g_f2_9 = extrude([(10.299, -9.272), (10.259, -9.025), (8.877, -9.249), (8.918, -9.496)], 0.0, 2.13, name='Core_Stair_F2_Step_10', color=(0.82, 0.83, 0.85, 1.0))
g_f2_9.layer = 'Stairs'

# Upper Half-Landing (+2.13m)
g_u_land = extrude([(8.877, -9.025), (10.259, -9.025), (10.259, -7.8), (8.877, -7.8)], 0.0, 2.13, name='Core_Stair_Upper_Landing', color=(0.80, 0.81, 0.83, 1.0))
g_u_land.layer = 'Stairs'

# Flight 3: Complete 10 steps returning South (+2.13m -> +3.50m, riser 0.137m)
g_f3_0 = extrude([(8.83, -8.953), (8.869, -9.2), (9.403, -9.113), (9.502, -8.844)], 0.0, 2.267, name='Core_Stair_F3_Step_1', color=(0.82, 0.83, 0.85, 1.0))
g_f3_0.layer = 'Stairs'
g_f3_1 = extrude([(8.869, -9.2), (8.909, -9.446), (9.444, -9.361), (9.403, -9.113)], 0.0, 2.404, name='Core_Stair_F3_Step_2', color=(0.82, 0.83, 0.85, 1.0))
g_f3_1.layer = 'Stairs'
g_f3_2 = extrude([(8.909, -9.446), (8.949, -9.694), (9.484, -9.607), (9.444, -9.361)], 0.0, 2.541, name='Core_Stair_F3_Step_3', color=(0.82, 0.83, 0.85, 1.0))
g_f3_2.layer = 'Stairs'
g_f3_3 = extrude([(8.949, -9.694), (8.989, -9.941), (9.524, -9.854), (9.484, -9.607)], 0.0, 2.678, name='Core_Stair_F3_Step_4', color=(0.82, 0.83, 0.85, 1.0))
g_f3_3.layer = 'Stairs'
g_f3_4 = extrude([(8.989, -9.941), (9.03, -10.187), (9.563, -10.1), (9.524, -9.854)], 0.0, 2.815, name='Core_Stair_F3_Step_5', color=(0.82, 0.83, 0.85, 1.0))
g_f3_4.layer = 'Stairs'
g_f3_5 = extrude([(9.03, -10.187), (9.069, -10.434), (9.603, -10.347), (9.563, -10.1)], 0.0, 2.952, name='Core_Stair_F3_Step_6', color=(0.82, 0.83, 0.85, 1.0))
g_f3_5.layer = 'Stairs'
g_f3_6 = extrude([(9.069, -10.434), (9.109, -10.68), (9.644, -10.594), (9.603, -10.347)], 0.0, 3.089, name='Core_Stair_F3_Step_7', color=(0.82, 0.83, 0.85, 1.0))
g_f3_6.layer = 'Stairs'
g_f3_7 = extrude([(9.109, -10.68), (9.149, -10.927), (9.684, -10.841), (9.644, -10.594)], 0.0, 3.226, name='Core_Stair_F3_Step_8', color=(0.82, 0.83, 0.85, 1.0))
g_f3_7.layer = 'Stairs'
g_f3_8 = extrude([(9.149, -10.927), (9.19, -11.175), (9.724, -11.088), (9.684, -10.841)], 0.0, 3.363, name='Core_Stair_F3_Step_9', color=(0.82, 0.83, 0.85, 1.0))
g_f3_8.layer = 'Stairs'
g_f3_9 = extrude([(9.19, -11.175), (9.23, -11.421), (9.763, -11.334), (9.724, -11.088)], 0.0, 3.5, name='Core_Stair_F3_Step_10', color=(0.82, 0.83, 0.85, 1.0))
g_f3_9.layer = 'Stairs'

# Center divider rail
g_rail = extrude([(9.568, -12.45), (9.6, -12.45), (9.6, -6.5), (9.568, -6.5)], 0.76, 3.50, name='Core_Stair_Center_Rail', color=(0.60, 0.65, 0.70, 1.0))
g_rail.layer = 'Stairs'

# 4. SOUTH STAIRCASE (16 STEPS, ASCENDING 0.00 -> +2.40m)
g_out_step_0 = extrude([(4.13, -21.204), (5.619, -21.023), (5.316, -18.538), (3.828, -18.723)], 0.0, 0.15, name='South_Stair_Step_01', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_0.layer = 'Stairs'
g_out_step_1 = extrude([(5.619, -21.023), (5.916, -20.987), (5.614, -18.499), (5.316, -18.538)], 0.0, 0.3, name='South_Stair_Step_02', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_1.layer = 'Stairs'
g_out_step_2 = extrude([(5.916, -20.987), (6.213, -20.951), (5.912, -18.46), (5.614, -18.499)], 0.0, 0.45, name='South_Stair_Step_03', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_2.layer = 'Stairs'
g_out_step_3 = extrude([(6.213, -20.951), (6.512, -20.914), (6.209, -18.42), (5.912, -18.46)], 0.0, 0.6, name='South_Stair_Step_04', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_3.layer = 'Stairs'
g_out_step_4 = extrude([(6.512, -20.914), (6.809, -20.878), (6.506, -18.38), (6.209, -18.42)], 0.0, 0.75, name='South_Stair_Step_05', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_4.layer = 'Stairs'
g_out_step_5 = extrude([(6.809, -20.878), (7.108, -20.842), (6.803, -18.338), (6.506, -18.38)], 0.0, 0.9, name='South_Stair_Step_06', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_5.layer = 'Stairs'
g_out_step_6 = extrude([(7.108, -20.842), (7.405, -20.806), (7.1, -18.296), (6.803, -18.338)], 0.0, 1.05, name='South_Stair_Step_07', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_6.layer = 'Stairs'
g_out_step_7 = extrude([(7.405, -20.806), (7.703, -20.77), (7.398, -18.254), (7.1, -18.296)], 0.0, 1.2, name='South_Stair_Step_08', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_7.layer = 'Stairs'
g_out_step_8 = extrude([(7.703, -20.77), (8.001, -20.735), (7.693, -18.199), (7.398, -18.254)], 0.0, 1.35, name='South_Stair_Step_09', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_8.layer = 'Stairs'
g_out_step_9 = extrude([(8.001, -20.735), (8.298, -20.697), (7.991, -18.167), (7.693, -18.199)], 0.0, 1.5, name='South_Stair_Step_10', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_9.layer = 'Stairs'
g_out_step_10 = extrude([(8.298, -20.697), (8.597, -20.661), (8.288, -18.124), (7.991, -18.167)], 0.0, 1.65, name='South_Stair_Step_11', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_10.layer = 'Stairs'
g_out_step_11 = extrude([(8.597, -20.661), (8.894, -20.626), (8.585, -18.078), (8.288, -18.124)], 0.0, 1.8, name='South_Stair_Step_12', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_11.layer = 'Stairs'
g_out_step_12 = extrude([(8.585, -18.078), (3.534, -16.242), (3.64, -17.133), (8.894, -20.626)], 0.0, 1.95, name='South_Stair_Step_13', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_12.layer = 'Stairs'
g_out_step_13 = extrude([(3.64, -17.133), (2.642, -21.384), (8.894, -20.626), (3.534, -16.242)], 0.0, 2.1, name='South_Stair_Step_14', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_13.layer = 'Stairs'
g_out_step_14 = extrude([(8.894, -20.626), (-9.798, 28.831), (-11.798, 28.831), (2.642, -21.384)], 0.0, 2.25, name='South_Stair_Step_15', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_14.layer = 'Stairs'
g_out_step_15 = extrude([(-9.798, 28.831), (-9.798, 29.832), (-11.798, 29.832), (-11.798, 28.831)], 0.0, 2.4, name='South_Stair_Step_16', color=(0.75, 0.77, 0.80, 1.0))
g_out_step_15.layer = 'Stairs'

# South Stair Upper Landing (+2.40m)
g_out_top_land = extrude([(8.894, -20.626), (10.3, -20.45), (10.0, -17.9), (8.585, -18.078)], 0.0, 2.40, name='South_Stair_Top_Landing', color=(0.73, 0.75, 0.78, 1.0))
g_out_top_land.layer = 'Stairs'

print('Updated Complete Basement Model Complete!')
print(f'Total groups in scene: {len(scene.groups)}')


# === 3. ST-1: PRIMARY FIRE EGRESS STAIR CORE (Layer P-2 (0.15)) ===
# Location: X in [6.1, 9.5], Y in [3.5, 6.2]
# West Flight: 5 steps climbing North from Z = 0.00m to Mid-Landing (Z = 0.875m)
for s in range(5):
    z = round(s * 0.175, 3)
    y_pos = round(5.05 + s * 0.25, 3)
    st = box((6.15, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_West_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))
    st.layer = 'Stairs'

# ST-1 Mid-Landing at North (Z = 0.875m)
st1_mid = box((6.15, 6.28, 0.00), (3.30, 1.25, 0.875), name='ST1_Mid_Landing', color=(0.82, 0.76, 0.70, 1.0))
st1_mid.layer = 'Stairs'

# ST-1 Center Divider Rail
st1_rail = box((7.65, 3.50, 0.00), (0.10, 2.75, 1.20), name='ST1_Center_Rail', color=(0.50, 0.52, 0.55, 1.0))
st1_rail.layer = 'Stairs'

# ST-1 East Flight: 10 steps climbing North to South (overhead to Floor 01, Z = 0.875m to 2.625m)
for s in range(10):
    z = round(0.875 + s * 0.175, 3)
    y_pos = round(6.00 - s * 0.25, 3)
    st = box((7.75, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_East_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))
    st.layer = 'Stairs'

# === 4. ST-2: CENTRAL OPEN STAIR NEAR LOCKERS (Layer A-stair) ===
# Location: X in [7.9, 10.6], Y in [-13.2, -9.0]
# Entrance flight: 4 steps stepping East from Z = 0.00m to Lower Landing (Z = 0.70m)
for s in range(4):
    z = round(s * 0.175, 3)
    x_pos = round(8.00 + s * 0.25, 3)
    st = box((x_pos, -13.15, 0.00), (0.28, 1.45, z + 0.175), name=f'ST2_Entrance_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))
    st.layer = 'Stairs'

# ST-2 Lower Landing (Z = 0.70m)
st2_low = box((8.85, -13.15, 0.00), (1.50, 1.65, 0.70), name='ST2_Lower_Landing', color=(0.75, 0.78, 0.85, 1.0))
st2_low.layer = 'Stairs'

# ST-2 Main Flight: 10 steps climbing North from Z = 0.70m up to 2.45m
for s in range(10):
    z = round(0.70 + s * 0.175, 3)
    y_pos = round(-11.45 + s * 0.25, 3)
    st = box((8.90, y_pos, 0.00), (1.45, 0.28, z + 0.175), name=f'ST2_Main_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))
    st.layer = 'Stairs'

# ST-2 Mid-Landing at North (Z = 2.45m)
st2_mid = box((8.90, -8.95, 0.00), (1.50, 1.20, 2.45), name='ST2_Mid_Landing', color=(0.75, 0.78, 0.85, 1.0))
st2_mid.layer = 'Stairs'

# === 5. ST-3: SOUTH OUTDOOR LANDSCAPE STAIR (Layer A-stair) ===
# Location: X in [4.1, 8.9], Y in [-21.2, -18.0]
# 16 angled parallel steps climbing East from Z = 0.00m up to +2.40m
for s in range(16):
    z = round((s + 1) * 0.15, 3)
    x_pos = round(4.15 + s * 0.30, 3)
    y_pos = round(-21.15 + s * 0.038, 3)
    st = box((x_pos, y_pos, 0.00), (0.33, 2.60, z), name=f'ST3_Landscape_Step_{s+1:02d}', color=(0.86, 0.82, 0.76, 1.0))
    st.layer = 'Stairs'

# Viewport update
viewport.camera.target = QVector3D(8.0, -4.0, 1.5)
viewport.camera.distance = 55.0
viewport.camera.yaw = -0.75
viewport.camera.pitch = 0.55
viewport.update()
print(f'Model built perfectly! Total groups: {len(groups)}')
