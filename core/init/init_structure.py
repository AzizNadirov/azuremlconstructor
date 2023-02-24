import os


class InitCreator:
    def __init__(self, pipe_name, dot_env, read_me):
        self.pipe_name = pipe_name
        base = 'pipelines/' + self.pipe_name
        self.make_init_dirs(base)
        self.handle_env(dot_env, base)
        self.create_conda_deps(base)
        self.create_setting_py(base, pipe_name)
        self.create_amlignore(base)
        if read_me in (None, 1): self.create_readme(base)

        

    def make_init_dirs(self, base):
        os.makedirs(base, exist_ok=True)
        os.makedirs(f"{base}/settings", exist_ok=True)
    
    def handle_env(self, dot_env, base):
        from src.tmps.tmp_init import env_vars
        with open(f"{base}/settings/env_vars.py", 'w') as f:
                f.write(env_vars)

        if dot_env in (None, 0):
            from src.tmps.tmp_init import dot_env_tmp
            with open(f"{base}/settings/.env", 'w') as f:
                f.write(dot_env_tmp)

        elif dot_env == 1:
            from src.tmps.tmp_init import dot_env_filled
            with open(f"{base}/settings/.env", 'w') as f:
                content = dot_env_filled.format(pipe_name=self.pipe_name)
                f.write(content)
        
        else:
            raise ValueError(f'Incorrect value for dot_env var: {dot_env} of type: {type(dot_env)}')

    def create_readme(self, base):
        content = f" # {self.pipe_name}"
        with open(f"{base}/README.md", 'w') as f:
            f.write(content)

    
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

    
        


