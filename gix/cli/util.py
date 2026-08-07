from gix.manager.CRUD import RepoCRUDEngine
from gix.manager.get_active_gix import fetch_deepest_gix_repo
from rich.console import Console

console = Console()


def build_engine_from_parent_gix_repo(current_dir):
    gix_path = fetch_deepest_gix_repo(current_dir)
    return gix_path, RepoCRUDEngine(gix_path)
