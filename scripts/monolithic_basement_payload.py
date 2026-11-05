# === MONOLITHIC INTEGRATED BASEMENT MODEL ===
# Single Flat Slab + Monolithically Unified Columns & Walls + Partitions + 3 Authentic Stairs
groups.clear()

# Ensure layers exist
layer_names = [l.name for l in layers]
for lname in ['Slabs', 'Structure_and_Walls', 'Partitions', 'Stairs']:
    if lname not in layer_names:
        layers.append(Layer(lname))

# 1. SINGLE UNIFIED FLAT BASEMENT SLAB (Z = 0.00m, thickness 0.20m, 4043.59 m^2)
slab_poly = [(-26.0, -0.35), (-18.849, -15.533), (-18.913, -17.107), (-18.132, -17.136), (-17.351, -17.162), (-16.57, -17.183), (-15.789, -17.2), (-15.007, -17.211), (-14.226, -17.22), (-13.444, -17.224), (-12.663, -17.223), (-11.881, -17.219), (-11.1, -17.209), (-10.319, -17.195), (-9.537, -17.179), (-8.756, -17.156), (-7.975, -17.13), (-7.193, -17.099), (-6.413, -17.064), (-5.632, -17.025), (-4.852, -16.982), (-4.072, -16.933), (-3.292, -16.881), (-2.512, -16.825), (-1.734, -16.764), (-0.955, -16.699), (-0.177, -16.629), (0.602, -16.556), (1.379, -16.478), (2.157, -16.396), (2.934, -16.31), (3.709, -16.219), (3.71, -14.0), (2.0, -14.0), (2.0, -22.0), (10.0, -22.0), (10.0, -14.0), (14.0, -10.0), (66.0, 6.0), (66.0, 22.0), (32.0, 22.0), (32.0, 44.0), (-26.0, 44.0)]
g_slab = extrude(slab_poly, -0.20, 0.0, name='Basement_Floor_Slab', color=(0.78, 0.80, 0.82, 1.0))
g_slab.layer = 'Slabs'

# 2. MONOLITHIC COLUMNS AND WALLS (Height: 3.50m, perfectly dissolved seams)
g_0 = extrude([(-7.689, -14.492), (-7.239, -14.473), (-7.197, -15.523), (-7.646, -15.541), (-7.689, -14.492)], 0.0, 3.50, name='Structural_Column_00', color=(0.88, 0.86, 0.84, 1.0))
g_0.layer = 'Structure_and_Walls'
g_1 = extrude([(-18.35, -14.302), (-18.4, -15.551), (-18.849, -15.533), (-18.8, -14.284), (-18.35, -14.302)], 0.0, 3.50, name='Structural_Column_01', color=(0.88, 0.86, 0.84, 1.0))
g_1.layer = 'Structure_and_Walls'
g_2 = extrude([(-23.726, -14.594), (-23.777, -15.243), (-24.225, -15.207), (-24.174, -14.559), (-23.726, -14.594)], 0.0, 3.50, name='Structural_Column_02', color=(0.88, 0.86, 0.84, 1.0))
g_2.layer = 'Structure_and_Walls'
g_3 = extrude([(-17.993, -5.148), (-18.018, -5.798), (-18.468, -5.78), (-18.443, -5.132), (-17.993, -5.148)], 0.0, 3.50, name='Structural_Column_03', color=(0.88, 0.86, 0.84, 1.0))
g_3.layer = 'Structure_and_Walls'
g_4 = extrude([(-7.63, -4.922), (-7.586, -5.971), (-8.036, -5.99), (-8.079, -4.94), (-7.63, -4.922)], 0.0, 3.50, name='Structural_Column_04', color=(0.88, 0.86, 0.84, 1.0))
g_4.layer = 'Structure_and_Walls'
g_5 = extrude([(-22.939, -4.666), (-23.022, -5.713), (-23.471, -5.678), (-23.388, -4.63), (-22.939, -4.666)], 0.0, 3.50, name='Structural_Column_05', color=(0.88, 0.86, 0.84, 1.0))
g_5.layer = 'Structure_and_Walls'
g_6 = extrude([(-17.85, -1.502), (-18.3, -1.484), (-18.251, -0.236), (-17.801, -0.254), (-17.85, -1.502)], 0.0, 3.50, name='Structural_Column_06', color=(0.88, 0.86, 0.84, 1.0))
g_6.layer = 'Structure_and_Walls'
g_7 = extrude([(-8.271, -0.244), (-7.821, -0.226), (-7.795, -0.875), (-8.244, -0.894), (-8.271, -0.244)], 0.0, 3.50, name='Structural_Column_07', color=(0.88, 0.86, 0.84, 1.0))
g_7.layer = 'Structure_and_Walls'
g_8 = extrude([(-22.571, 0.016), (-22.622, -0.633), (-23.071, -0.597), (-23.02, 0.051), (-22.571, 0.016)], 0.0, 3.50, name='Structural_Column_08', color=(0.88, 0.86, 0.84, 1.0))
g_8.layer = 'Structure_and_Walls'
g_9 = extrude([(-6.016, 3.77), (-5.567, 3.735), (-5.602, 3.286), (-6.05, 3.321), (-6.016, 3.77)], 0.0, 3.50, name='Structural_Column_09', color=(0.88, 0.86, 0.84, 1.0))
g_9.layer = 'Structure_and_Walls'
g_10 = extrude([(-10.583, 3.68), (-10.576, 3.781), (-6.043, 3.421), (-6.05, 3.321), (-10.583, 3.68)], 0.0, 3.50, name='Structural_Column_10', color=(0.88, 0.86, 0.84, 1.0))
g_10.layer = 'Structure_and_Walls'
g_11 = extrude([(-11.035, 3.716), (-10.597, 9.249), (-8.676, 9.097), (-8.684, 8.997), (-10.156, 9.114), (-10.199, 8.565), (-10.548, 8.593), (-10.9, 4.157), (-10.551, 4.13), (-10.587, 3.681), (-11.035, 3.716)], 0.0, 3.50, name='Monolithic_Core_Assembly_11', color=(0.84, 0.82, 0.79, 1.0))
g_11.layer = 'Structure_and_Walls'
g_12 = extrude([(-15.984, 4.56), (-15.535, 4.525), (-15.571, 4.076), (-16.019, 4.111), (-15.984, 4.56)], 0.0, 3.50, name='Structural_Column_12', color=(0.88, 0.86, 0.84, 1.0))
g_12.layer = 'Structure_and_Walls'
g_13 = extrude([(-22.313, 5.079), (-21.868, 5.006), (-21.941, 4.562), (-22.386, 4.635), (-22.313, 5.079)], 0.0, 3.50, name='Structural_Column_13', color=(0.88, 0.86, 0.84, 1.0))
g_13.layer = 'Structure_and_Walls'
g_14 = extrude([(-7.093, 8.871), (-7.084, 8.971), (-5.612, 8.854), (-5.621, 8.755), (-7.093, 8.871)], 0.0, 3.50, name='Structural_Column_14', color=(0.88, 0.86, 0.84, 1.0))
g_14.layer = 'Structure_and_Walls'
g_15 = extrude([(-15.133, 9.608), (-15.184, 8.96), (-15.633, 8.996), (-15.581, 9.644), (-15.133, 9.608)], 0.0, 3.50, name='Structural_Column_15', color=(0.88, 0.86, 0.84, 1.0))
g_15.layer = 'Structure_and_Walls'
g_16 = extrude([(-21.504, 10.03), (-21.06, 9.958), (-21.133, 9.514), (-21.577, 9.587), (-21.504, 10.03)], 0.0, 3.50, name='Structural_Column_16', color=(0.88, 0.86, 0.84, 1.0))
g_16.layer = 'Structure_and_Walls'
g_17 = extrude([(-19.993, 16.493), (-20.098, 15.852), (-20.542, 15.925), (-20.437, 16.566), (-19.993, 16.493)], 0.0, 3.50, name='Structural_Column_17', color=(0.88, 0.86, 0.84, 1.0))
g_17.layer = 'Structure_and_Walls'
g_18 = extrude([(-9.24, 20.678), (-9.292, 20.029), (-9.74, 20.065), (-9.689, 20.713), (-9.24, 20.678)], 0.0, 3.50, name='Structural_Column_18', color=(0.88, 0.86, 0.84, 1.0))
g_18.layer = 'Structure_and_Walls'
g_19 = extrude([(-14.225, 21.073), (-14.276, 20.424), (-14.725, 20.46), (-14.674, 21.108), (-14.225, 21.073)], 0.0, 3.50, name='Structural_Column_19', color=(0.88, 0.86, 0.84, 1.0))
g_19.layer = 'Structure_and_Walls'
g_20 = extrude([(-19.666, 21.403), (-19.217, 21.367), (-19.252, 20.918), (-19.701, 20.954), (-19.666, 21.403)], 0.0, 3.50, name='Structural_Column_20', color=(0.88, 0.86, 0.84, 1.0))
g_20.layer = 'Structure_and_Walls'
g_21 = extrude([(-9.822, 27.532), (-9.822, 40.131), (-9.398, 40.131), (-9.398, 40.032), (-9.723, 40.032), (-9.723, 37.932), (-5.073, 37.932), (-5.073, 40.032), (-5.397, 40.032), (-5.397, 40.131), (-4.973, 40.131), (-4.973, 37.932), (-1.748, 37.932), (-1.748, 37.832), (-9.723, 37.832), (-9.723, 36.182), (-9.373, 36.182), (-9.373, 35.532), (-9.723, 35.532), (-9.723, 30.832), (-8.823, 30.832), (-8.823, 30.732), (-9.723, 30.732), (-9.723, 28.182), (-9.373, 28.182), (-9.373, 27.632), (-6.698, 27.632), (-6.698, 27.532), (-9.822, 27.532)], 0.0, 3.50, name='Monolithic_Core_Assembly_21', color=(0.84, 0.82, 0.79, 1.0))
g_21.layer = 'Structure_and_Walls'
g_22 = extrude([(-18.273, 27.632), (-18.723, 27.632), (-18.723, 28.082), (-18.273, 28.082), (-18.273, 27.632)], 0.0, 3.50, name='Structural_Column_22', color=(0.88, 0.86, 0.84, 1.0))
g_22.layer = 'Structure_and_Walls'
g_23 = extrude([(-7.123, 30.732), (-7.223, 30.732), (-7.223, 30.832), (-7.123, 30.832), (-7.123, 30.732)], 0.0, 3.50, name='Structural_Column_23', color=(0.88, 0.86, 0.84, 1.0))
g_23.layer = 'Structure_and_Walls'
g_24 = extrude([(-16.572, 35.632), (-17.023, 35.632), (-17.023, 36.082), (-16.572, 36.082), (-16.572, 35.632)], 0.0, 3.50, name='Structural_Column_24', color=(0.88, 0.86, 0.84, 1.0))
g_24.layer = 'Structure_and_Walls'
g_25 = extrude([(-14.873, 43.082), (-14.873, 42.632), (-15.323, 42.632), (-15.323, 43.082), (-14.873, 43.082)], 0.0, 3.50, name='Structural_Column_25', color=(0.88, 0.86, 0.84, 1.0))
g_25.layer = 'Structure_and_Walls'
g_26 = extrude([(-9.273, 42.632), (-9.923, 42.632), (-9.923, 43.082), (-9.273, 43.082), (-9.273, 42.632)], 0.0, 3.50, name='Structural_Column_26', color=(0.88, 0.86, 0.84, 1.0))
g_26.layer = 'Structure_and_Walls'
g_27 = extrude([(-15.298, 43.482), (0.177, 43.482), (0.177, 43.107), (0.077, 43.107), (0.077, 43.381), (-15.298, 43.381), (-15.298, 43.482)], 0.0, 3.50, name='Monolithic_Core_Assembly_27', color=(0.84, 0.82, 0.79, 1.0))
g_27.layer = 'Structure_and_Walls'
g_28 = extrude([(-0.663, -0.397), (-0.674, -0.297), (1.744, -0.003), (1.677, 0.543), (2.125, 0.597), (2.191, 0.052), (4.09, 0.283), (4.103, 0.183), (-0.663, -0.397)], 0.0, 3.50, name='Structural_Column_28', color=(0.88, 0.86, 0.84, 1.0))
g_28.layer = 'Structure_and_Walls'
g_29 = extrude([(-1.031, 3.375), (-0.582, 3.34), (-0.618, 2.892), (-0.965, 2.919), (-0.762, 1.254), (-0.861, 1.242), (-1.067, 2.927), (-5.602, 3.286), (-5.594, 3.386), (-1.059, 3.026), (-1.031, 3.375)], 0.0, 3.50, name='Monolithic_Core_Assembly_29', color=(0.84, 0.82, 0.79, 1.0))
g_29.layer = 'Structure_and_Walls'
pts3d_30 = [QVector3D(1.067, 2.958, 0.0), QVector3D(1.205, 4.704, 0.0), QVector3D(1.306, 4.695, 0.0), QVector3D(1.172, 3.003, 0.0), QVector3D(1.176, 3.05, 0.0), QVector3D(2.122, 2.975, 0.0), QVector3D(2.12, 2.942, 0.0), QVector3D(2.253, 4.62, 0.0), QVector3D(2.353, 4.613, 0.0), QVector3D(2.198, 2.668, 0.0), QVector3D(-0.618, 2.892, 0.0), QVector3D(-0.602, 3.091, 0.0), QVector3D(0.021, 3.041, 0.0), QVector3D(0.159, 4.786, 0.0), QVector3D(0.259, 4.778, 0.0), QVector3D(0.121, 3.034, 0.0), QVector3D(1.067, 2.958, 0.0)]
holes_30 = [[QVector3D(0.013, 2.942, 0.0), QVector3D(0.014, 2.942, 0.0), QVector3D(0.021, 3.041, 0.0), QVector3D(0.013, 2.942, 0.0)], [QVector3D(1.16, 2.851, 0.0), QVector3D(2.107, 2.776, 0.0), QVector3D(2.115, 2.876, 0.0), QVector3D(1.168, 2.951, 0.0), QVector3D(1.16, 2.851, 0.0)], [QVector3D(1.059, 2.859, 0.0), QVector3D(0.088, 2.936, 0.0), QVector3D(1.066, 2.858, 0.0), QVector3D(1.059, 2.859, 0.0)]]
g_30 = prism(pts3d_30, QVector3D(0, 0, 3.50), holes=holes_30, name='Monolithic_Core_Assembly_30', color=(0.84, 0.82, 0.79, 1.0))
g_30.layer = 'Structure_and_Walls'
g_31 = extrude([(-0.679, 7.812), (-0.58, 7.803), (-0.931, 3.368), (-1.031, 3.375), (-0.679, 7.812)], 0.0, 3.50, name='Structural_Column_31', color=(0.88, 0.86, 0.84, 1.0))
g_31.layer = 'Structure_and_Walls'
g_32 = extrude([(-0.223, 7.875), (1.447, 7.743), (1.439, 7.644), (0.492, 7.719), (0.349, 5.925), (0.25, 5.932), (0.393, 7.726), (0.474, 7.72), (-0.231, 7.776), (-0.223, 7.875)], 0.0, 3.50, name='Structural_Column_32', color=(0.88, 0.86, 0.84, 1.0))
g_32.layer = 'Structure_and_Walls'
g_33 = extrude([(-5.664, 8.207), (-5.564, 8.198), (-5.915, 3.763), (-6.016, 3.77), (-5.664, 8.207)], 0.0, 3.50, name='Structural_Column_33', color=(0.88, 0.86, 0.84, 1.0))
g_33.layer = 'Structure_and_Walls'
g_34 = extrude([(-2.598, 8.615), (-0.18, 8.424), (-0.231, 7.776), (-0.679, 7.812), (-0.637, 8.36), (-2.607, 8.516), (-2.598, 8.615)], 0.0, 3.50, name='Structural_Column_34', color=(0.88, 0.86, 0.84, 1.0))
g_34.layer = 'Structure_and_Walls'
g_35 = extrude([(-5.215, 8.171), (-5.664, 8.207), (-5.612, 8.854), (-4.19, 8.742), (-4.198, 8.642), (-5.172, 8.719), (-5.215, 8.171)], 0.0, 3.50, name='Structural_Column_35', color=(0.88, 0.86, 0.84, 1.0))
g_35.layer = 'Structure_and_Walls'
g_36 = extrude([(0.728, 19.889), (0.677, 19.24), (0.229, 19.276), (0.279, 19.923), (0.728, 19.889)], 0.0, 3.50, name='Structural_Column_36', color=(0.88, 0.86, 0.84, 1.0))
g_36.layer = 'Structure_and_Walls'
g_37 = extrude([(-4.256, 20.283), (-4.307, 19.635), (-4.756, 19.671), (-4.704, 20.318), (-4.256, 20.283)], 0.0, 3.50, name='Structural_Column_37', color=(0.88, 0.86, 0.84, 1.0))
g_37.layer = 'Structure_and_Walls'
g_38 = extrude([(0.252, 24.819), (0.252, 23.632), (0.152, 23.632), (0.152, 24.819), (0.252, 24.819)], 0.0, 3.50, name='Structural_Column_38', color=(0.88, 0.86, 0.84, 1.0))
g_38.layer = 'Structure_and_Walls'
g_39 = extrude([(0.627, 27.532), (0.252, 27.532), (0.252, 26.42), (0.152, 26.42), (0.152, 27.532), (0.177, 27.532), (0.177, 28.182), (0.627, 28.182), (0.627, 27.532)], 0.0, 3.50, name='Structural_Column_39', color=(0.88, 0.86, 0.84, 1.0))
g_39.layer = 'Structure_and_Walls'
g_40 = extrude([(-0.848, 27.632), (0.152, 27.632), (0.152, 27.532), (-0.848, 27.532), (-0.848, 27.632)], 0.0, 3.50, name='Structural_Column_40', color=(0.88, 0.86, 0.84, 1.0))
g_40.layer = 'Structure_and_Walls'
g_41 = extrude([(-2.448, 27.532), (-3.848, 27.532), (-3.848, 27.632), (-2.448, 27.632), (-2.448, 27.532)], 0.0, 3.50, name='Structural_Column_41', color=(0.88, 0.86, 0.84, 1.0))
g_41.layer = 'Structure_and_Walls'
g_42 = extrude([(0.152, 30.732), (-7.098, 30.732), (-7.098, 30.832), (0.152, 30.832), (0.152, 30.732)], 0.0, 3.50, name='Structural_Column_42', color=(0.88, 0.86, 0.84, 1.0))
g_42.layer = 'Structure_and_Walls'
g_43 = extrude([(0.627, 35.532), (0.177, 35.532), (0.177, 36.182), (0.627, 36.182), (0.627, 35.532)], 0.0, 3.50, name='Structural_Column_43', color=(0.88, 0.86, 0.84, 1.0))
g_43.layer = 'Structure_and_Walls'
g_44 = extrude([(0.152, 37.832), (-0.148, 37.832), (-0.148, 37.932), (0.152, 37.932), (0.152, 37.832)], 0.0, 3.50, name='Structural_Column_44', color=(0.88, 0.86, 0.84, 1.0))
g_44.layer = 'Structure_and_Walls'
g_45 = extrude([(0.727, 42.632), (0.077, 42.632), (0.077, 43.082), (0.727, 43.082), (0.727, 42.632)], 0.0, 3.50, name='Structural_Column_45', color=(0.88, 0.86, 0.84, 1.0))
g_45.layer = 'Structure_and_Walls'
g_46 = extrude([(3.866, -13.757), (3.969, -14.6), (3.522, -14.655), (3.419, -13.811), (3.866, -13.757)], 0.0, 3.50, name='Structural_Column_46', color=(0.88, 0.86, 0.84, 1.0))
g_46.layer = 'Structure_and_Walls'
g_47 = extrude([(4.947, -6.838), (4.931, -6.735), (12.793, -5.464), (12.809, -5.562), (4.947, -6.838)], 0.0, 3.50, name='Structural_Column_47', color=(0.88, 0.86, 0.84, 1.0))
g_47.layer = 'Structure_and_Walls'
g_48 = extrude([(4.931, -6.735), (4.547, -3.591), (4.646, -3.579), (4.825, -5.033), (6.479, -4.765), (6.495, -4.864), (4.837, -5.134), (5.029, -6.722), (4.931, -6.735)], 0.0, 3.50, name='Structural_Column_48', color=(0.88, 0.86, 0.84, 1.0))
g_48.layer = 'Structure_and_Walls'
g_49 = extrude([(2.359, -5.066), (2.256, -4.221), (1.756, -0.101), (1.855, -0.09), (2.356, -4.209), (2.703, -4.167), (2.794, -4.912), (4.679, -4.683), (4.692, -4.782), (2.359, -5.066)], 0.0, 3.50, name='Monolithic_Core_Assembly_49', color=(0.84, 0.82, 0.79, 1.0))
g_49.layer = 'Structure_and_Walls'
g_50 = extrude([(2.205, -2.968), (2.193, -2.87), (4.423, -2.599), (4.435, -2.698), (2.205, -2.968)], 0.0, 3.50, name='Structural_Column_50', color=(0.88, 0.86, 0.84, 1.0))
g_50.layer = 'Structure_and_Walls'
g_51 = extrude([(4.423, -2.598), (4.522, -2.586), (4.534, -2.686), (4.435, -2.697), (4.423, -2.598)], 0.0, 3.50, name='Structural_Column_51', color=(0.88, 0.86, 0.84, 1.0))
g_51.layer = 'Structure_and_Walls'
g_52 = extrude([(4.191, 0.274), (4.09, 0.283), (4.188, 1.507), (4.287, 1.5), (4.191, 0.274)], 0.0, 3.50, name='Structural_Column_52', color=(0.88, 0.86, 0.84, 1.0))
g_52.layer = 'Structure_and_Walls'
g_53 = extrude([(3.217, 1.283), (3.118, 1.292), (3.228, 2.687), (3.925, 2.631), (3.918, 2.532), (3.32, 2.58), (3.217, 1.283)], 0.0, 3.50, name='Structural_Column_53', color=(0.88, 0.86, 0.84, 1.0))
g_53.layer = 'Structure_and_Walls'
pts3d_54 = [QVector3D(3.448, 4.826, 0.0), QVector3D(3.455, 4.926, 0.0), QVector3D(4.452, 4.848, 0.0), QVector3D(4.653, 7.389, 0.0), QVector3D(2.586, 7.553, 0.0), QVector3D(2.593, 7.653, 0.0), QVector3D(2.443, 5.759, 0.0), QVector3D(2.343, 5.766, 0.0), QVector3D(2.478, 7.462, 0.0), QVector3D(1.53, 7.537, 0.0), QVector3D(1.4, 5.891, 0.0), QVector3D(1.549, 5.879, 0.0), QVector3D(1.546, 5.83, 0.0), QVector3D(1.296, 5.85, 0.0), QVector3D(1.447, 7.743, 0.0), QVector3D(1.471, 7.741, 0.0), QVector3D(-0.223, 7.875, 0.0), QVector3D(-0.215, 7.976, 0.0), QVector3D(4.321, 7.616, 0.0), QVector3D(4.356, 8.065, 0.0), QVector3D(4.805, 8.029, 0.0), QVector3D(4.402, 2.946, 0.0), QVector3D(4.751, 2.917, 0.0), QVector3D(4.743, 2.818, 0.0), QVector3D(4.394, 2.845, 0.0), QVector3D(4.367, 2.497, 0.0), QVector3D(3.918, 2.532, 0.0), QVector3D(3.954, 2.981, 0.0), QVector3D(4.302, 2.954, 0.0), QVector3D(4.445, 4.747, 0.0), QVector3D(3.448, 4.826, 0.0)]
holes_54 = [[QVector3D(1.546, 7.735, 0.0), QVector3D(1.532, 7.559, 0.0), QVector3D(1.539, 7.636, 0.0), QVector3D(2.485, 7.561, 0.0), QVector3D(2.493, 7.661, 0.0), QVector3D(1.546, 7.735, 0.0)]]
g_54 = prism(pts3d_54, QVector3D(0, 0, 3.50), holes=holes_54, name='Monolithic_Core_Assembly_54', color=(0.84, 0.82, 0.79, 1.0))
g_54.layer = 'Structure_and_Walls'
g_55 = extrude([(1.302, 4.645), (1.306, 4.695), (1.455, 4.683), (1.451, 4.634), (1.302, 4.645)], 0.0, 3.50, name='Structural_Column_55', color=(0.88, 0.86, 0.84, 1.0))
g_55.layer = 'Structure_and_Walls'
g_56 = extrude([(5.713, 19.494), (5.661, 18.845), (5.212, 18.881), (5.264, 19.529), (5.713, 19.494)], 0.0, 3.50, name='Structural_Column_56', color=(0.88, 0.86, 0.84, 1.0))
g_56.layer = 'Structure_and_Walls'
pts3d_57 = [QVector3D(9.379, -12.967, 0.0), QVector3D(9.483, -13.609, 0.0), QVector3D(10.962, -13.308, 0.0), QVector3D(10.954, -13.309, 0.0), QVector3D(9.954, -7.14, 0.0), QVector3D(10.052, -7.123, 0.0), QVector3D(11.051, -13.289, 0.0), QVector3D(14.063, -12.676, 0.0), QVector3D(12.892, -5.448, 0.0), QVector3D(12.793, -5.464, 0.0), QVector3D(12.36, -2.798, 0.0), QVector3D(10.584, -3.087, 0.0), QVector3D(10.539, -2.803, 0.0), QVector3D(10.588, -2.795, 0.0), QVector3D(10.618, -2.979, 0.0), QVector3D(12.247, -2.716, 0.0), QVector3D(11.906, -0.619, 0.0), QVector3D(10.277, -0.882, 0.0), QVector3D(10.302, -1.03, 0.0), QVector3D(10.252, -1.039, 0.0), QVector3D(10.229, -0.891, 0.0), QVector3D(10.27, -0.883, 0.0), QVector3D(10.229, -0.89, 0.0), QVector3D(10.213, -0.791, 0.0), QVector3D(12.088, -0.488, 0.0), QVector3D(11.682, 2.014, 0.0), QVector3D(11.691, 1.955, 0.0), QVector3D(10.063, 1.691, 0.0), QVector3D(10.135, 1.247, 0.0), QVector3D(11.763, 1.512, 0.0), QVector3D(11.779, 1.412, 0.0), QVector3D(10.052, 1.133, 0.0), QVector3D(9.964, 1.675, 0.0), QVector3D(8.463, 1.432, 0.0), QVector3D(8.551, 0.889, 0.0), QVector3D(6.823, 0.609, 0.0), QVector3D(6.971, -0.304, 0.0), QVector3D(8.698, -0.024, 0.0), QVector3D(8.715, -0.122, 0.0), QVector3D(6.987, -0.403, 0.0), QVector3D(7.132, -1.292, 0.0), QVector3D(9.007, -0.987, 0.0), QVector3D(9.023, -1.085, 0.0), QVector3D(7.345, -1.358, 0.0), QVector3D(7.512, -2.382, 0.0), QVector3D(9.09, -2.126, 0.0), QVector3D(9.098, -2.176, 0.0), QVector3D(7.52, -2.432, 0.0), QVector3D(7.686, -3.455, 0.0), QVector3D(7.586, -3.471, 0.0), QVector3D(7.246, -1.374, 0.0), QVector3D(7.148, -1.39, 0.0), QVector3D(7.488, -3.488, 0.0), QVector3D(7.833, -3.432, 0.0), QVector3D(7.969, -4.27, 0.0), QVector3D(7.623, -4.327, 0.0), QVector3D(7.679, -4.672, 0.0), QVector3D(7.581, -4.688, 0.0), QVector3D(7.405, -3.602, 0.0), QVector3D(5.727, -3.874, 0.0), QVector3D(5.711, -3.776, 0.0), QVector3D(7.389, -3.504, 0.0), QVector3D(6.621, 1.234, 0.0), QVector3D(9.314, 1.671, 0.0), QVector3D(9.217, 1.68, 0.0), QVector3D(9.236, 1.912, 0.0), QVector3D(9.336, 1.904, 0.0), QVector3D(9.317, 1.672, 0.0), QVector3D(11.676, 2.055, 0.0), QVector3D(10.817, 7.353, 0.0), QVector3D(9.774, 7.435, 0.0), QVector3D(9.781, 7.535, 0.0), QVector3D(10.8, 7.454, 0.0), QVector3D(10.476, 9.456, 0.0), QVector3D(10.476, 18.564, 0.0), QVector3D(10.206, 18.586, 0.0), QVector3D(10.24, 19.034, 0.0), QVector3D(10.476, 19.015, 0.0), QVector3D(10.476, 27.532, 0.0), QVector3D(10.177, 27.532, 0.0), QVector3D(10.177, 28.182, 0.0), QVector3D(10.627, 28.182, 0.0), QVector3D(10.627, 27.632, 0.0), QVector3D(10.676, 27.632, 0.0), QVector3D(10.676, 18.999, 0.0), QVector3D(10.689, 18.998, 0.0), QVector3D(10.676, 18.836, 0.0), QVector3D(10.676, 9.462, 0.0), QVector3D(14.292, -12.834, 0.0), QVector3D(9.515, -13.806, 0.0), QVector3D(9.071, -13.878, 0.0), QVector3D(8.934, -13.039, 0.0), QVector3D(9.379, -12.967, 0.0)]
holes_57 = [[QVector3D(7.153, 0.763, 0.0), QVector3D(8.436, 0.972, 0.0), QVector3D(8.364, 1.416, 0.0), QVector3D(7.081, 1.208, 0.0), QVector3D(7.065, 1.306, 0.0), QVector3D(7.153, 0.763, 0.0)], [QVector3D(12.444, -2.684, 0.0), QVector3D(12.104, -0.586, 0.0), QVector3D(12.006, -0.602, 0.0), QVector3D(12.345, -2.7, 0.0), QVector3D(12.444, -2.684, 0.0)]]
g_57 = prism(pts3d_57, QVector3D(0, 0, 3.50), holes=holes_57, name='Monolithic_Core_Assembly_57', color=(0.84, 0.82, 0.79, 1.0))
g_57.layer = 'Structure_and_Walls'
g_58 = extrude([(9.794, -6.153), (9.778, -6.054), (9.876, -6.038), (9.892, -6.137), (9.794, -6.153)], 0.0, 3.50, name='Structural_Column_58', color=(0.88, 0.86, 0.84, 1.0))
g_58.layer = 'Structure_and_Walls'
g_59 = extrude([(7.85, -3.53), (7.833, -3.432), (9.314, -3.191), (9.284, -3.006), (9.333, -2.998), (9.379, -3.282), (7.85, -3.53)], 0.0, 3.50, name='Structural_Column_59', color=(0.88, 0.86, 0.84, 1.0))
g_59.layer = 'Structure_and_Walls'
g_60 = extrude([(9.148, -2.167), (9.197, -2.16), (9.221, -2.307), (9.172, -2.315), (9.148, -2.167)], 0.0, 3.50, name='Structural_Column_60', color=(0.88, 0.86, 0.84, 1.0))
g_60.layer = 'Structure_and_Walls'
g_61 = extrude([(9.11, -1.933), (9.159, -1.925), (9.19, -2.11), (9.14, -2.117), (9.11, -1.933)], 0.0, 3.50, name='Structural_Column_61', color=(0.88, 0.86, 0.84, 1.0))
g_61.layer = 'Structure_and_Walls'
g_62 = extrude([(8.974, -1.094), (9.023, -1.085), (9.047, -1.234), (8.998, -1.242), (8.974, -1.094)], 0.0, 3.50, name='Structural_Column_62', color=(0.88, 0.86, 0.84, 1.0))
g_62.layer = 'Structure_and_Walls'
g_63 = extrude([(10.2, 0.219), (11.927, 0.5), (11.943, 0.4), (10.216, 0.121), (10.2, 0.219)], 0.0, 3.50, name='Structural_Column_63', color=(0.88, 0.86, 0.84, 1.0))
g_63.layer = 'Structure_and_Walls'
g_64 = extrude([(6.56, 2.238), (6.461, 2.222), (6.385, 2.687), (6.484, 2.703), (6.56, 2.238)], 0.0, 3.50, name='Structural_Column_64', color=(0.88, 0.86, 0.84, 1.0))
g_64.layer = 'Structure_and_Walls'
g_65 = extrude([(6.296, 2.795), (6.289, 2.696), (5.939, 2.723), (5.947, 2.823), (6.296, 2.795)], 0.0, 3.50, name='Structural_Column_65', color=(0.88, 0.86, 0.84, 1.0))
g_65.layer = 'Structure_and_Walls'
g_66 = extrude([(9.222, 3.017), (9.546, 7.102), (9.746, 7.086), (9.422, 3.001), (9.222, 3.017)], 0.0, 3.50, name='Monolithic_Core_Assembly_66', color=(0.84, 0.82, 0.79, 1.0))
g_66.layer = 'Structure_and_Walls'
pts3d_67 = [QVector3D(5.947, 2.823, 0.0), QVector3D(5.748, 2.839, 0.0), QVector3D(6.111, 7.425, 0.0), QVector3D(6.135, 7.723, 0.0), QVector3D(6.434, 7.7, 0.0), QVector3D(6.41, 7.4, 0.0), QVector3D(6.311, 7.408, 0.0), QVector3D(5.947, 2.823, 0.0)]
holes_67 = [[QVector3D(6.21, 7.416, 0.0), QVector3D(6.261, 7.412, 0.0), QVector3D(6.111, 7.425, 0.0), QVector3D(6.21, 7.416, 0.0)]]
g_67 = prism(pts3d_67, QVector3D(0, 0, 3.50), holes=holes_67, name='Monolithic_Core_Assembly_67', color=(0.84, 0.82, 0.79, 1.0))
g_67.layer = 'Structure_and_Walls'
g_68 = extrude([(6.442, 7.799), (9.781, 7.535), (9.746, 7.086), (9.297, 7.122), (9.316, 7.371), (6.426, 7.6), (6.442, 7.799)], 0.0, 3.50, name='Structural_Column_68', color=(0.88, 0.86, 0.84, 1.0))
g_68.layer = 'Structure_and_Walls'
g_69 = extrude([(9.846, 14.05), (10.294, 14.015), (10.258, 13.566), (9.811, 13.601), (9.846, 14.05)], 0.0, 3.50, name='Structural_Column_69', color=(0.88, 0.86, 0.84, 1.0))
g_69.layer = 'Structure_and_Walls'
g_70 = extrude([(20.287, -10.729), (20.49, -11.555), (20.053, -11.662), (19.85, -10.837), (20.287, -10.729)], 0.0, 3.50, name='Structural_Column_70', color=(0.88, 0.86, 0.84, 1.0))
g_70.layer = 'Structure_and_Walls'
g_71 = extrude([(30.823, -8.576), (30.619, -7.959), (31.045, -7.818), (31.25, -8.435), (30.823, -8.576)], 0.0, 3.50, name='Structural_Column_71', color=(0.88, 0.86, 0.84, 1.0))
g_71.layer = 'Structure_and_Walls'
g_72 = extrude([(41.475, -3.866), (41.729, -4.464), (41.314, -4.639), (41.061, -4.041), (41.475, -3.866)], 0.0, 3.50, name='Structural_Column_72', color=(0.88, 0.86, 0.84, 1.0))
g_72.layer = 'Structure_and_Walls'
g_73 = extrude([(10.364, -1.729), (10.414, -1.722), (10.444, -1.906), (11.974, -1.658), (11.982, -1.708), (10.452, -1.956), (10.476, -2.104), (10.427, -2.112), (10.364, -1.729)], 0.0, 3.50, name='Structural_Column_73', color=(0.88, 0.86, 0.84, 1.0))
g_73.layer = 'Structure_and_Walls'
g_74 = extrude([(17.985, -1.348), (18.187, -2.173), (17.75, -2.28), (17.548, -1.455), (17.985, -1.348)], 0.0, 3.50, name='Structural_Column_74', color=(0.88, 0.86, 0.84, 1.0))
g_74.layer = 'Structure_and_Walls'
g_75 = extrude([(51.557, 0.906), (51.857, 0.331), (51.458, 0.122), (51.158, 0.699), (51.557, 0.906)], 0.0, 3.50, name='Structural_Column_75', color=(0.88, 0.86, 0.84, 1.0))
g_75.layer = 'Structure_and_Walls'
g_76 = extrude([(27.747, 0.686), (27.543, 1.303), (27.97, 1.445), (28.175, 0.828), (27.747, 0.686)], 0.0, 3.50, name='Structural_Column_76', color=(0.88, 0.86, 0.84, 1.0))
g_76.layer = 'Structure_and_Walls'
g_77 = extrude([(16.84, 3.314), (16.997, 2.683), (16.561, 2.575), (16.403, 3.206), (16.84, 3.314)], 0.0, 3.50, name='Structural_Column_77', color=(0.88, 0.86, 0.84, 1.0))
g_77.layer = 'Structure_and_Walls'
g_78 = extrude([(57.506, 4.091), (57.893, 4.319), (58.122, 3.932), (57.734, 3.703), (57.506, 4.091)], 0.0, 3.50, name='Structural_Column_78', color=(0.88, 0.86, 0.84, 1.0))
g_78.layer = 'Structure_and_Walls'
g_79 = extrude([(37.67, 5.122), (37.923, 4.524), (37.508, 4.348), (37.255, 4.946), (37.67, 5.122)], 0.0, 3.50, name='Structural_Column_79', color=(0.88, 0.86, 0.84, 1.0))
g_79.layer = 'Structure_and_Walls'
g_80 = extrude([(26.139, 5.527), (25.999, 5.956), (26.428, 6.094), (26.566, 5.667), (26.139, 5.527)], 0.0, 3.50, name='Structural_Column_80', color=(0.88, 0.86, 0.84, 1.0))
g_80.layer = 'Structure_and_Walls'
g_81 = extrude([(63.713, 7.954), (64.088, 8.202), (64.336, 7.827), (63.961, 7.578), (63.713, 7.954)], 0.0, 3.50, name='Structural_Column_81', color=(0.88, 0.86, 0.84, 1.0))
g_81.layer = 'Structure_and_Walls'
g_82 = extrude([(46.756, 8.925), (47.333, 9.227), (47.54, 8.828), (46.965, 8.526), (46.756, 8.925)], 0.0, 3.50, name='Structural_Column_82', color=(0.88, 0.86, 0.84, 1.0))
g_82.layer = 'Structure_and_Walls'
g_83 = extrude([(35.345, 9.459), (35.759, 9.634), (35.935, 9.219), (35.52, 9.044), (35.345, 9.459)], 0.0, 3.50, name='Structural_Column_83', color=(0.88, 0.86, 0.84, 1.0))
g_83.layer = 'Structure_and_Walls'
g_84 = extrude([(52.554, 12.501), (52.942, 12.73), (53.171, 12.343), (52.782, 12.114), (52.554, 12.501)], 0.0, 3.50, name='Structural_Column_84', color=(0.88, 0.86, 0.84, 1.0))
g_84.layer = 'Structure_and_Walls'
g_85 = extrude([(44.381, 13.698), (44.78, 13.907), (44.989, 13.508), (44.59, 13.299), (44.381, 13.698)], 0.0, 3.50, name='Structural_Column_85', color=(0.88, 0.86, 0.84, 1.0))
g_85.layer = 'Structure_and_Walls'
g_86 = extrude([(58.577, 15.719), (58.328, 16.093), (58.704, 16.342), (58.951, 15.966), (58.577, 15.719)], 0.0, 3.50, name='Structural_Column_86', color=(0.88, 0.86, 0.84, 1.0))
g_86.layer = 'Structure_and_Walls'
g_87 = extrude([(50.018, 16.811), (50.405, 17.038), (50.634, 16.651), (50.245, 16.423), (50.018, 16.811)], 0.0, 3.50, name='Structural_Column_87', color=(0.88, 0.86, 0.84, 1.0))
g_87.layer = 'Structure_and_Walls'
g_88 = extrude([(20.726, 19.567), (20.077, 19.567), (20.077, 20.018), (20.726, 20.018), (20.726, 19.567)], 0.0, 3.50, name='Structural_Column_88', color=(0.88, 0.86, 0.84, 1.0))
g_88.layer = 'Structure_and_Walls'
g_89 = extrude([(30.727, 19.567), (30.077, 19.567), (30.077, 20.018), (30.727, 20.018), (30.727, 19.567)], 0.0, 3.50, name='Structural_Column_89', color=(0.88, 0.86, 0.84, 1.0))
g_89.layer = 'Structure_and_Walls'
g_90 = extrude([(55.57, 20.264), (55.945, 20.512), (56.193, 20.137), (55.818, 19.889), (55.57, 20.264)], 0.0, 3.50, name='Structural_Column_90', color=(0.88, 0.86, 0.84, 1.0))
g_90.layer = 'Structure_and_Walls'
g_91 = extrude([(20.726, 27.632), (20.077, 27.632), (20.077, 28.082), (20.726, 28.082), (20.726, 27.632)], 0.0, 3.50, name='Structural_Column_91', color=(0.88, 0.86, 0.84, 1.0))
g_91.layer = 'Structure_and_Walls'
g_92 = extrude([(30.727, 27.632), (30.077, 27.632), (30.077, 28.082), (30.727, 28.082), (30.727, 27.632)], 0.0, 3.50, name='Structural_Column_92', color=(0.88, 0.86, 0.84, 1.0))
g_92.layer = 'Structure_and_Walls'
g_93 = extrude([(10.627, 35.532), (10.177, 35.532), (10.177, 36.182), (10.627, 36.182), (10.627, 35.532)], 0.0, 3.50, name='Structural_Column_93', color=(0.88, 0.86, 0.84, 1.0))
g_93.layer = 'Structure_and_Walls'
g_94 = extrude([(20.726, 35.632), (20.077, 35.632), (20.077, 36.082), (20.726, 36.082), (20.726, 35.632)], 0.0, 3.50, name='Structural_Column_94', color=(0.88, 0.86, 0.84, 1.0))
g_94.layer = 'Structure_and_Walls'
g_95 = extrude([(30.727, 35.632), (30.077, 35.632), (30.077, 36.082), (30.727, 36.082), (30.727, 35.632)], 0.0, 3.50, name='Structural_Column_95', color=(0.88, 0.86, 0.84, 1.0))
g_95.layer = 'Structure_and_Walls'
g_96 = extrude([(10.727, 42.632), (10.076, 42.632), (10.076, 43.082), (10.727, 43.082), (10.727, 42.632)], 0.0, 3.50, name='Structural_Column_96', color=(0.88, 0.86, 0.84, 1.0))
g_96.layer = 'Structure_and_Walls'
g_97 = extrude([(20.726, 42.632), (20.077, 42.632), (20.077, 43.082), (20.726, 43.082), (20.726, 42.632)], 0.0, 3.50, name='Structural_Column_97', color=(0.88, 0.86, 0.84, 1.0))
g_97.layer = 'Structure_and_Walls'
g_98 = extrude([(30.727, 42.632), (30.077, 42.632), (30.077, 43.082), (30.727, 43.082), (30.727, 42.632)], 0.0, 3.50, name='Structural_Column_98', color=(0.88, 0.86, 0.84, 1.0))
g_98.layer = 'Structure_and_Walls'

# 3. RESTROOM PARTITIONS (Height: 2.20m, Thickness: 0.10m)
p_0 = wall((7.775, 3.731), (8.364, 3.684), height=2.20, thickness=0.10, name='Partition_00', color=(0.76, 0.79, 0.83, 1.0))
p_0.layer = 'Partitions'
p_1 = wall((8.68, 3.66), (9.27, 3.612), height=2.20, thickness=0.10, name='Partition_01', color=(0.76, 0.79, 0.83, 1.0))
p_1.layer = 'Partitions'
p_2 = wall((-4.105, 8.735), (-2.683, 8.623), height=2.20, thickness=0.10, name='Partition_02', color=(0.76, 0.79, 0.83, 1.0))
p_2.layer = 'Partitions'
p_3 = wall((6.143, 7.822), (4.796, 7.929), height=2.20, thickness=0.10, name='Partition_03', color=(0.76, 0.79, 0.83, 1.0))
p_3.layer = 'Partitions'
p_4 = wall((7.335, -2.55), (7.458, -3.305), height=2.20, thickness=0.10, name='Partition_04', color=(0.76, 0.79, 0.83, 1.0))
p_4.layer = 'Partitions'
p_5 = wall((7.699, 5.944), (7.11, 5.991), height=2.20, thickness=0.10, name='Partition_05', color=(0.76, 0.79, 0.83, 1.0))
p_5.layer = 'Partitions'
p_6 = wall((6.793, 6.016), (6.204, 6.062), height=2.20, thickness=0.10, name='Partition_06', color=(0.76, 0.79, 0.83, 1.0))
p_6.layer = 'Partitions'
p_7 = wall((7.795, 3.981), (8.384, 3.934), height=2.20, thickness=0.10, name='Partition_07', color=(0.76, 0.79, 0.83, 1.0))
p_7.layer = 'Partitions'
p_8 = wall((8.701, 3.909), (9.29, 3.862), height=2.20, thickness=0.10, name='Partition_08', color=(0.76, 0.79, 0.83, 1.0))
p_8.layer = 'Partitions'
p_9 = wall((7.814, 4.229), (8.403, 4.183), height=2.20, thickness=0.10, name='Partition_09', color=(0.76, 0.79, 0.83, 1.0))
p_9.layer = 'Partitions'
p_10 = wall((8.72, 4.159), (9.309, 4.111), height=2.20, thickness=0.10, name='Partition_10', color=(0.76, 0.79, 0.83, 1.0))
p_10.layer = 'Partitions'
p_11 = wall((7.834, 4.479), (8.423, 4.433), height=2.20, thickness=0.10, name='Partition_11', color=(0.76, 0.79, 0.83, 1.0))
p_11.layer = 'Partitions'
p_12 = wall((8.74, 4.407), (9.329, 4.361), height=2.20, thickness=0.10, name='Partition_12', color=(0.76, 0.79, 0.83, 1.0))
p_12.layer = 'Partitions'
p_13 = wall((7.854, 4.728), (8.443, 4.681), height=2.20, thickness=0.10, name='Partition_13', color=(0.76, 0.79, 0.83, 1.0))
p_13.layer = 'Partitions'
p_14 = wall((8.76, 4.657), (9.349, 4.609), height=2.20, thickness=0.10, name='Partition_14', color=(0.76, 0.79, 0.83, 1.0))
p_14.layer = 'Partitions'
p_15 = wall((7.873, 4.978), (8.462, 4.931), height=2.20, thickness=0.10, name='Partition_15', color=(0.76, 0.79, 0.83, 1.0))
p_15.layer = 'Partitions'
p_16 = wall((8.779, 4.906), (9.368, 4.859), height=2.20, thickness=0.10, name='Partition_16', color=(0.76, 0.79, 0.83, 1.0))
p_16.layer = 'Partitions'
p_17 = wall((7.893, 5.226), (8.483, 5.18), height=2.20, thickness=0.10, name='Partition_17', color=(0.76, 0.79, 0.83, 1.0))
p_17.layer = 'Partitions'
p_18 = wall((8.799, 5.154), (9.388, 5.108), height=2.20, thickness=0.10, name='Partition_18', color=(0.76, 0.79, 0.83, 1.0))
p_18.layer = 'Partitions'
p_19 = wall((7.913, 5.476), (8.503, 5.43), height=2.20, thickness=0.10, name='Partition_19', color=(0.76, 0.79, 0.83, 1.0))
p_19.layer = 'Partitions'
p_20 = wall((8.819, 5.404), (9.409, 5.358), height=2.20, thickness=0.10, name='Partition_20', color=(0.76, 0.79, 0.83, 1.0))
p_20.layer = 'Partitions'
p_21 = wall((7.932, 5.725), (8.522, 5.678), height=2.20, thickness=0.10, name='Partition_21', color=(0.76, 0.79, 0.83, 1.0))
p_21.layer = 'Partitions'
p_22 = wall((8.838, 5.653), (9.428, 5.606), height=2.20, thickness=0.10, name='Partition_22', color=(0.76, 0.79, 0.83, 1.0))
p_22.layer = 'Partitions'
p_23 = wall((7.952, 5.975), (8.542, 5.928), height=2.20, thickness=0.10, name='Partition_23', color=(0.76, 0.79, 0.83, 1.0))
p_23.layer = 'Partitions'
p_24 = wall((8.858, 5.903), (9.448, 5.856), height=2.20, thickness=0.10, name='Partition_24', color=(0.76, 0.79, 0.83, 1.0))
p_24.layer = 'Partitions'
p_25 = wall((7.679, 5.695), (7.09, 5.742), height=2.20, thickness=0.10, name='Partition_25', color=(0.76, 0.79, 0.83, 1.0))
p_25.layer = 'Partitions'
p_26 = wall((6.773, 5.767), (6.184, 5.814), height=2.20, thickness=0.10, name='Partition_26', color=(0.76, 0.79, 0.83, 1.0))
p_26.layer = 'Partitions'
p_27 = wall((7.659, 5.445), (7.071, 5.492), height=2.20, thickness=0.10, name='Partition_27', color=(0.76, 0.79, 0.83, 1.0))
p_27.layer = 'Partitions'
p_28 = wall((6.754, 5.517), (6.165, 5.564), height=2.20, thickness=0.10, name='Partition_28', color=(0.76, 0.79, 0.83, 1.0))
p_28.layer = 'Partitions'
p_29 = wall((7.64, 5.197), (7.051, 5.243), height=2.20, thickness=0.10, name='Partition_29', color=(0.76, 0.79, 0.83, 1.0))
p_29.layer = 'Partitions'
p_30 = wall((6.734, 5.269), (6.145, 5.315), height=2.20, thickness=0.10, name='Partition_30', color=(0.76, 0.79, 0.83, 1.0))
p_30.layer = 'Partitions'
p_31 = wall((7.62, 4.947), (7.031, 4.994), height=2.20, thickness=0.10, name='Partition_31', color=(0.76, 0.79, 0.83, 1.0))
p_31.layer = 'Partitions'
p_32 = wall((6.714, 5.019), (6.125, 5.066), height=2.20, thickness=0.10, name='Partition_32', color=(0.76, 0.79, 0.83, 1.0))
p_32.layer = 'Partitions'
p_33 = wall((4.303, 4.858), (4.505, 7.402), height=2.20, thickness=0.10, name='Partition_33', color=(0.76, 0.79, 0.83, 1.0))
p_33.layer = 'Partitions'
p_34 = wall((11.769, -2.894), (12.2, -5.56), height=2.20, thickness=0.10, name='Partition_34', color=(0.76, 0.79, 0.83, 1.0))
p_34.layer = 'Partitions'
p_35 = wall((12.311, -2.806), (12.743, -5.472), height=2.20, thickness=0.10, name='Partition_35', color=(0.76, 0.79, 0.83, 1.0))
p_35.layer = 'Partitions'
p_36 = wall((12.321, -2.804), (12.753, -5.47), height=2.20, thickness=0.10, name='Partition_36', color=(0.76, 0.79, 0.83, 1.0))
p_36.layer = 'Partitions'
p_37 = wall((3.228, 2.687), (2.207, 2.768), height=2.20, thickness=0.10, name='Partition_37', color=(0.76, 0.79, 0.83, 1.0))
p_37.layer = 'Partitions'
p_38 = wall((8.859, -1.011), (8.715, -0.122), height=2.20, thickness=0.10, name='Partition_38', color=(0.76, 0.79, 0.83, 1.0))
p_38.layer = 'Partitions'
p_39 = wall((8.551, 0.889), (8.698, -0.024), height=2.20, thickness=0.10, name='Partition_39', color=(0.76, 0.79, 0.83, 1.0))
p_39.layer = 'Partitions'
p_40 = wall((10.36, -0.768), (10.216, 0.121), height=2.20, thickness=0.10, name='Partition_40', color=(0.76, 0.79, 0.83, 1.0))
p_40.layer = 'Partitions'
p_41 = wall((10.052, 1.133), (10.2, 0.219), height=2.20, thickness=0.10, name='Partition_41', color=(0.76, 0.79, 0.83, 1.0))
p_41.layer = 'Partitions'
p_42 = wall((0.349, 5.925), (1.296, 5.85), height=2.20, thickness=0.10, name='Partition_42', color=(0.76, 0.79, 0.83, 1.0))
p_42.layer = 'Partitions'
p_43 = wall((0.25, 5.932), (-0.722, 6.01), height=2.20, thickness=0.10, name='Partition_43', color=(0.76, 0.79, 0.83, 1.0))
p_43.layer = 'Partitions'
p_44 = wall((0.259, 4.778), (1.205, 4.704), height=2.20, thickness=0.10, name='Partition_44', color=(0.76, 0.79, 0.83, 1.0))
p_44.layer = 'Partitions'
p_45 = wall((0.159, 4.786), (-0.813, 4.863), height=2.20, thickness=0.10, name='Partition_45', color=(0.76, 0.79, 0.83, 1.0))
p_45.layer = 'Partitions'

# 4. ST-1: PRIMARY FIRE EGRESS STAIR CORE (Layer P-2 (0.15))
for s in range(5):
    z = round(s * 0.175, 3)
    y_pos = round(5.05 + s * 0.25, 3)
    st = box((6.15, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_West_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))
    st.layer = 'Stairs'
st1_mid = box((6.15, 6.28, 0.00), (3.30, 1.25, 0.875), name='ST1_Mid_Landing', color=(0.82, 0.76, 0.70, 1.0))
st1_mid.layer = 'Stairs'
st1_rail = box((7.65, 3.50, 0.00), (0.10, 2.75, 1.20), name='ST1_Center_Rail', color=(0.50, 0.52, 0.55, 1.0))
st1_rail.layer = 'Stairs'
for s in range(10):
    z = round(0.875 + s * 0.175, 3)
    y_pos = round(6.00 - s * 0.25, 3)
    st = box((7.75, y_pos, 0.00), (1.50, 0.28, z + 0.175), name=f'ST1_East_Step_{s+1}', color=(0.82, 0.76, 0.70, 1.0))
    st.layer = 'Stairs'

# 5. ST-2: CENTRAL OPEN STAIR NEAR LOCKERS (Layer A-stair)
for s in range(4):
    z = round(s * 0.175, 3)
    x_pos = round(8.00 + s * 0.25, 3)
    st = box((x_pos, -13.15, 0.00), (0.28, 1.45, z + 0.175), name=f'ST2_Entrance_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))
    st.layer = 'Stairs'
st2_low = box((8.85, -13.15, 0.00), (1.50, 1.65, 0.70), name='ST2_Lower_Landing', color=(0.75, 0.78, 0.85, 1.0))
st2_low.layer = 'Stairs'
for s in range(10):
    z = round(0.70 + s * 0.175, 3)
    y_pos = round(-11.45 + s * 0.25, 3)
    st = box((8.90, y_pos, 0.00), (1.45, 0.28, z + 0.175), name=f'ST2_Main_Step_{s+1}', color=(0.75, 0.78, 0.85, 1.0))
    st.layer = 'Stairs'
st2_mid = box((8.90, -8.95, 0.00), (1.50, 1.20, 2.45), name='ST2_Mid_Landing', color=(0.75, 0.78, 0.85, 1.0))
st2_mid.layer = 'Stairs'

# 6. ST-3: SOUTH OUTDOOR LANDSCAPE STAIR (Layer A-stair)
for s in range(16):
    z = round((s + 1) * 0.15, 3)
    x_pos = round(4.15 + s * 0.30, 3)
    y_pos = round(-21.15 + s * 0.038, 3)
    st = box((x_pos, y_pos, 0.00), (0.33, 2.60, z), name=f'ST3_Landscape_Step_{s+1:02d}', color=(0.86, 0.82, 0.76, 1.0))
    st.layer = 'Stairs'

# 7. VIEWPORT CAMERA & UPDATE
viewport.camera.target = QVector3D(8.0, -3.0, 1.5)
viewport.camera.distance = 55.0
viewport.camera.yaw = -0.75
viewport.camera.pitch = 0.55
viewport.update()
print('Monolithic Integrated Basement Model built successfully! Total groups:', len(groups))