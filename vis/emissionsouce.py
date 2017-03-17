import json


def create_source_info_json(sources, filepath):
    data = {'sources': []}
    for source in sources:
        data['sources'].append(source)
    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    with open(filepath, 'w') as fileout:
        fileout.write(json_data)
    return json_data