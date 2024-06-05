from addict import Addict
from argparse import Namespace
from types import SimpleNamespace

standard = object()


class DotDict(Addict):
    def merge(self, merg_dict: dict):
        if merg_dict:
            if isinstance(merg_dict, Namespace):
                merg_dict = self.from_dict(vars(merg_dict))
                #print(merg_dict)
            
            for key, value in merg_dict.items():
                if isinstance(value, (dict, self.__class__)):
                    value = self.from_dict(value)
                if key in self and isinstance(self[key], self.__class__):
                    self[key].merge(value)
                elif value is standard:
                    pass
                else:
                    self[key] = value

    @classmethod
    def from_dict(cls, d: dict):
        _cls = cls()
        for key, value in d.items():
            if value is None:
                continue
            if isinstance(value, (dict, cls)):
                value = cls.from_dict(value)
            elif isinstance(value, Namespace):
                value = cls.from_dict(vars(value))
            else:
                parts = key.split('.')
                current = _cls
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = cls()
                    current = current[part]
                current[parts[-1]] = value
            _cls[key] = value
        return _cls

    def __repr__(self) -> str:
        name = type(self).__name__
        args = []
        for _name, _value in sorted(self.items()):
            args.append(f"{_name}={_value}")
        return f"{name}({','.join(args)})"
    
    @classmethod
    def from_dot_key(cls, key, value):
        _cls = cls()
        if "." in key:
            parts = key.split('.')
            for part in parts:
                value = cls.from_dot_key(part, value)
        _cls[key] = value
        return _cls
