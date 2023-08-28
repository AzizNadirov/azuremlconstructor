from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from azuremlconstructor.confs.configs import BASE_DIR, TEMPLATES_DIR




class StructureInit:

    def __init__(self, pipe_name: str, path: Path, env):
        self.pipe_name = pipe_name
        self.path = path
        self.env = env
        

        self.j_env = Environment(loader=FileSystemLoader(f"{TEMPLATES_DIR}/init/"))
        print(f"{TEMPLATES_DIR}/init/")
    

    def start(self):
        base = self.path / self.pipe_name
        self.make_init_dirs(base)
        self.handle_env(self.env, base)
        self.create_conda_deps(base)
        self.create_setting_py(base)
        self.create_amlignore(base)


    def make_init_dirs(self, base: Path):
        (base / "settings/").mkdir(exist_ok=True, mode=0o770, parents=True)


    def handle_env(self, env, base: Path):
        dot_env_t = self.j_env.get_template("dot_env")
        if env is None:             # env not passed
            # write raw templates if no env passed.
            with open(f"{TEMPLATES_DIR}/init/dot_env") as content_f:
                content_de = content_f.read()

            with (base / "settings/.env").open(mode='w') as f:
                f.write(content_de)

            with (base / "settings/env_vars.py").open('w') as f:
                with open(f"{TEMPLATES_DIR}/init/env_vars") as content_f:
                    content_ev = content_f.read()
                f.write(content_ev)

        else:       # env passed
            eb_dict = env.as_dict()
            eb_dict['ENVIRONMENT_FILE'] = (base / 'settings/conda_dependencies.yml').resolve()  # abs path

            content_de = dot_env_t.render(**eb_dict)

            with (base / "settings/.env").open('w') as f:
                f.write(content_de)



    def create_conda_deps(self, base: Path):
        with open(f"{TEMPLATES_DIR}/init/conda_dependencies") as f:
            content = f.read()

        with (base / 'settings/conda_dependencies.yml').open('w+') as f:
            f.write(content)


    def create_setting_py(self, base: Path):
        settings_t = self.j_env.get_template('settings')
        content = settings_t.render(pipe_name=self.pipe_name)

        with (base / 'settings/settings.py').open('w+') as f:
            f.write(content)


    def create_amlignore(self, base: Path):

        with open(f"{TEMPLATES_DIR}/init/dot_amlignore") as f:
            content = f.read()

        with (base / 'settings/.amlignore').open('w+') as f:
            f.write(content)
