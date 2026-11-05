import sys
sys.path.insert(0, '.')
from scripts.render_stair_crops import render_crop

# Crop of the North building stairs (X in [400, 800], Y in [200, 800])
render_crop((450, 200, 850, 800), 'crop_stair_north_building')

