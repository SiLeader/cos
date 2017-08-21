Automatic Creation System
=====
Copyright (C) 2017 SiLeader. All rights reserved.

## features
+ full suffix rule system
+ auto multi threading
+ runner support
+ JSON setting file
+ debug and release support (clean support)

## Usage
```bash
python3 main.py [sub command] [options]
```

| sub command | behavior |
|:-----------:|:---------|
| build | build project |
| rebuild | clear and build project |
| clean | clear temporary files and output file |
| show | show setting |

type `-h` or `--help` option to look other ones.

## setting.json
Setting file

sample
```json
{
  "rules": {
    "debug": [
      {
        "suffix": ".cpp",
        "compiler": "clang++",
        "options": "-std=c++14 -O3"
      }
    ],
    "release": [
      {
        "suffix": ".cpp",
        "compiler": "clang++",
        "options": "-std=c++14 -g3"
      }
    ],
    "link": {
      "linker": "clang++",
      "options": "",
      "output": "a.elf"
    }
  },
  "run": "./a.elf"
}
```

## Requirement
Python3 (3.5.2 is tested)

## License
[Mozilla Public License 2.0](https://github.com/SiLeader/cos/blob/master/LICENSE)

## Author
[SiLeader](https://github.com/SiLeader)