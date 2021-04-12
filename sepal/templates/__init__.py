from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=__path__[0])  # type: ignore  # mypy issue #1422
get_template = templates.get_template
