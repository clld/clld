from pathlib import Path

from clld.web.assets import environment

import {{cookiecutter.directory_name}}


environment.append_path(
    Path({{cookiecutter.directory_name}}.__file__).parent.joinpath('static').as_posix(),
    url='/{{cookiecutter.directory_name}}:static/')
environment.load_path = list(reversed(environment.load_path))
