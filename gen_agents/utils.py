import os

# Copy and paste your OpenAI API Key
openai_api_key = os.environ.get('OPENAI_API_KEY')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

maze_assets_loc = os.path.join(ROOT_DIR, "frontend_server/static_dirs/assets")
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = os.path.join(ROOT_DIR, "frontend_server/storage")
fs_temp_storage = os.path.join(ROOT_DIR, "frontend_server/temp_storage")

collision_block_id = "32125"

# Verbose
debug = True
