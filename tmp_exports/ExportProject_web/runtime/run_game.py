from runtime.game_loop import GameRuntime
from ui.actions.project_io import load_project
import sys

def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else 'data/project.gep'
    project = load_project(project_path)
    GameRuntime(project).run()

if __name__ == '__main__':
    main()
