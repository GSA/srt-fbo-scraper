from copy import deepcopy
from typing import Callable, List
from .parser import make_parser
from yaml import safe_load, YAMLError
from .dotdict import DotDict
import sys
from pathlib import Path

config_defaults = """
estimator: estimator.pkl
"""

config = DotDict()


class OptionsError(Exception):
    ...


def yaml_loader(cfg_str):
    return safe_load(cfg_str)


def merge_into(cfg: DotDict, f: Path, merge: bool = True) -> dict:
    cfg_f = None
    with f.open("r") as cfg_file:
        try:
            cfg_f = safe_load(cfg_file.read())
        except YAMLError as exc:
            raise OptionsError("Error Loading Config Yaml") from exc
    if merge:
        cfg.merge(cfg_f)

    return DotDict(cfg_f)


def pre_main(
    app_name: str,
    app_version: str,
    args: List[str] = [],
    _make_parser: Callable = make_parser,
    cfg_default: dict = config_defaults,
):
    config.app = app_name
    config.app_version = app_version
    if cfg_default:
        cfg_default = yaml_loader(cfg_default)
        config.merge(cfg_default)

    if _make_parser:
        parser = _make_parser()
    else:
        parser = make_parser()

    cli = parser.parse_args(args)

    config.merge(cli)
    merge_into(config, config._config)
    copy_config = deepcopy(config)
    for k, v in copy_config.items():
        if str(v).endswith(".yml"):
            p_v = Path(v)
            if not p_v.is_file():
                p_v = Path(sys.prefix, "config", v)
            config[k] = merge_into(config, p_v, merge=False)

    config.prefix = sys.prefix

    return config
