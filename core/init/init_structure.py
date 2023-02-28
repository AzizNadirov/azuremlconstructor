from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from core.init.init import EnvBank
from confs.configs import BASE_DIR, TEMPLATES_DIR




class StructureInit:

    def __init__(self, pipe_name: str, path: Path, env: EnvBank):
        self.pipe_name = pipe_name
        base = Path(f'{path}/{self.pipe_name}')
        self.make_init_dirs(base)
        self.handle_env(env, base)
        self.create_conda_deps(base)
        self.create_setting_py(base, pipe_name)
        self.create_amlignore(base)
        self.j_env = Environment(loader=FileSystemLoader(f"{TEMPLATES_DIR}/init/"))
    

    def make_init_dirs(self, base):
        base.mkdir(exist_ok=True)
        (base / "/settings").mkdir(exist_ok=True)

    def handle_env(self, env: EnvBank or None, base: Path):
        dot_env_t = self.j_env.get_template("dot_env.txt")
        env_vars_t = self.j_env.get_template("env_vars.txt")
        if env is None:
            # write raw templates if no env passed.
            with ({base} / "/settings/.env").open('w+') as f:
                with open(f"{TEMPLATES_DIR}/init/dot_env.txt") as content_f:
                    content_de = content_f.read()
                f.write(content_de)

            with ({base} / "/settings/env_vars.py").open('w+') as f:
                with open(f"{TEMPLATES_DIR}/init/env_vars.txt") as content_f:
                    content_ev = content_f.read()
                f.write(content_ev)

        else:
            eb_dict = env.as_dict()

            content_de = dot_env_t.render(**eb_dict)
            content_ev = env_vars_t.render(**eb_dict)

            with ({base} / "/settings/env_vars.py").open('w+') as f:
                f.write(content_ev)
            
            with ({base} / "/settings/.env").open('w+') as f:
                f.write(content_de)



    def create_conda_deps(self, base):
        from src.tmps.tmp_init import conda_deps
        content = conda_deps
        with open(base + '/settings/conda_dependencies.yml', 'w') as f:
            f.write(content)

    def create_setting_py(self, base, pipe_name):
        from src.tmps.tmp_init import settings_py_tmp
        content = settings_py_tmp.format(pipe_name=pipe_name)
        with open(base + '/settings/settings.py', 'w') as f:
            f.write(content)

    def create_amlignore(self, base):
        from src.tmps.tmp_init import amlignore
        content = amlignore
        with open(base + '/.amlignore', 'w') as f:
            f.write(content)
