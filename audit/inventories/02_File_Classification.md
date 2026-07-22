\# Noise Prediction Plugin File Classification



\## Classification definitions



\- Keep: useful and can remain mostly unchanged

\- Refactor: useful, but must be reorganized or cleaned

\- Replace: existing implementation should be replaced

\- Remove from release: development-only or obsolete file

\- Investigate: purpose or future use is not yet confirmed



\## Current files



| No. | File | Current purpose | Classification | Reason | Final action |

|---:|---|---|---|---|---|

| 1 | \_\_init\_\_.py | QGIS plugin entry factory | Investigate | Must verify how the plugin class is loaded | |

| 2 | Noise\_Prediction.py | Main plugin class and provider registration | Refactor | Currently designed mainly for Processing provider registration | |

| 3 | Noise\_Prediction\_provider.py | Registers Processing algorithms | Refactor | Should remain, but likely move into processing package | |

| 4 | Noise\_Prediction\_algorithm.py | Main noise prediction algorithm | Refactor | Core workflow should be separated from parameter and GUI logic | |

| 5 | get\_sampledata\_algorithm.py | Provides sample data | Investigate | Need to check whether data is embedded, downloaded, or created | |

| 6 | threshold\_limit\_algorithm.py | Threshold classification algorithm | Refactor | Useful supporting tool but needs compatibility review | |

| 7 | metadata.txt | QGIS plugin metadata | Refactor | Version, URLs, compatibility, description and changelog need updating | |

| 8 | icon.png | Plugin icon | Keep | Can remain unless redesigned | |

| 9 | help.png | Help image | Investigate | Need to check whether referenced by code or documentation | |

| 10 | sample.png | Sample/result image | Investigate | May be useful for documentation but probably not plugin runtime | |

| 11 | logo.png | Logo image | Investigate | Need to check where it is used | |

| 12 | ifc\_logo.png | Logo image | Investigate | Need to verify licensing and current use | |

| 13 | README.md | Main repository documentation | Refactor | Needs version 1.3 GUI instructions and updated architecture | |

| 14 | README.html | Generated or duplicate documentation | Remove from release | Likely generated from documentation source | |

| 15 | README.txt | Duplicate documentation | Remove from release | Avoid maintaining three README versions | |

| 16 | Makefile | Plugin Builder/build automation | Investigate | May still help packaging but may be outdated | |

| 17 | pb\_tool.cfg | Plugin Builder configuration | Investigate | Development-only; not required at runtime | |

| 18 | plugin\_upload.py | Plugin upload helper | Remove from release | Development/deployment utility, not runtime code | |

| 19 | pylintrc | Python lint configuration | Keep in repository | Useful for development but not required in release ZIP | |

| 20 | urls.py | URL handling or deployment helper | Investigate | Must inspect imports and usage | |

