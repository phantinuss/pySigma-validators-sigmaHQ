# Version 0.1.0
# Author: frack113
# Date: 2025/05/28

import json
from sys import stderr, stdout
from pprint import pformat
from sigma.rule import SigmaLogSource


def core_logsource(source: SigmaLogSource) -> SigmaLogSource:
    return SigmaLogSource(product=source.product, category=source.category, service=source.service)


def key_logsource(source: dict) -> str:
    product = source["product"] if source["product"] else "none"
    category = source["category"] if source["category"] else "none"
    service = source["service"] if source["service"] else "none"
    return f"{product}_{category}_{service}"


#
# sigmahq_filename.json
#
with open("tools/sigmahq_filename.json", "r", encoding="UTF-8") as file:
    json_dict = json.load(file)

    filename_version = json_dict["version"]
    filename_info = dict()

    temp = {key_logsource(v["logsource"]): v for v in json_dict["pattern"].values()}
    for key in sorted(temp.keys(), key=str.casefold):
        value = temp[key]
        logsource = core_logsource(SigmaLogSource.from_dict(value["logsource"]))
        filename_info[logsource] = value["prefix"]

#
# sigma.json
#
with open("tools/sigma.json", "r", encoding="UTF-8") as file:
    json_dict = json.load(file)

    taxonomy_version = json_dict["version"]
    taxonomy_info = dict()
    taxonomy_definition = dict()

    temp = {key_logsource(v["logsource"]): v for v in json_dict["taxonomy"].values()}
    for key in sorted(temp.keys(), key=str.casefold):
        value = temp[key]
        logsource = core_logsource(SigmaLogSource.from_dict(value["logsource"]))
        fieldlist = []
        fieldlist.extend(value["field"]["native"])
        fieldlist.extend(value["field"]["custom"])
        taxonomy_info[logsource] = sorted(fieldlist, key=str.casefold)
        taxonomy_definition[logsource] = value["logsource"]["definition"]

    taxonomy_info_unicast = {k: [v.lower() for v in l] for k, l in taxonomy_info.items()}

#
# sigmahq_windows_validator.json
#
with open("tools/sigmahq_windows_validator.json", "r", encoding="UTF-8") as file:
    json_dict = json.load(file)

    windows_version = json_dict["version"]
    windows_provider_name = dict()

    for category in sorted(json_dict["category_provider_name"], key=str.casefold):
        windows_provider_name[
            SigmaLogSource(product="windows", category=category, service=None)
        ] = json_dict["category_provider_name"][category]
    windows_no_eventid = sorted(json_dict["category_no_eventid"], key=str.casefold)


# python data
with open("sigma/validators/sigmahq/sigmahq_data.py", "wt", encoding="utf-8", newline="") as file:
    print("from typing import Dict, List", file=file)
    print("from sigma.rule import SigmaLogSource", file=file)
    print(f'\nfile_pattern_version: str = "{filename_version}"', file=file)
    print(
        "ref_sigmahq_logsource_filepattern: Dict[SigmaLogSource, str] = "
        + pformat(filename_info, indent=4, sort_dicts=False),
        file=file,
    )
    print(f'\ntaxonomy_version: str = "{taxonomy_version}"', file=file)
    print(
        "ref_sigmahq_fieldsname: Dict[SigmaLogSource, List[str]] = "
        + pformat(taxonomy_info, indent=4, sort_dicts=False),
        file=file,
    )
    print(
        "ref_sigmahq_fieldsname_unicast: Dict[SigmaLogSource, List[str]] = "
        + pformat(taxonomy_info_unicast, indent=4, sort_dicts=False),
        file=file,
    )
    print(
        "ref_sigmahq_logsource_definition: Dict[SigmaLogSource, str] = "
        + pformat(taxonomy_definition, indent=4, sort_dicts=False, width=200),
        file=file,
    )
    print(f'\nwindows_version: str = "{windows_version}"', file=file)
    print(
        "ref_windows_provider_name: Dict[SigmaLogSource, List[str]] = "
        + pformat(windows_provider_name, indent=4, sort_dicts=False),
        file=file,
    )
    print(
        "ref_windows_no_eventid: List[str] = "
        + pformat(windows_no_eventid, indent=4, sort_dicts=False),
        file=file,
    )
