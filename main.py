import copy
import json


def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{file_path}'.")
        return None


def load_ndjson_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = [json.loads(line) for line in file]
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{file_path}'.")
        return None


# Function to search for objects by key
def search_array_by_key(array, key, value):
    for item in array:
        if item.get(key) == value:
            return item
    return None


def search_object_by_key(json_data, object_key, object_value):
    # Iterate through each object in the JSON data
    for obj in json_data:
        # Check if the '_id' field of the object matches the desired ID
        if object_key in obj and obj[object_key] == object_value:
            return obj
    # If the object with the specified ID is not found, return None
    return None


def find_modifier_option_by_key(data, key, value):
    res = None
    for obj in data:
        res = search_array_by_key(obj['option_values'], key, value)

        if res:
            break

    return res


def main():
    # file_path = "staging_products.json"  # Adjust the file path as needed

    prodData = load_json_file("data/production_merged.json")
    stagData = load_json_file("data/sandbox_merged.json")
    sanityDataset = load_ndjson_file("data/backup.ndjson")

    # if prodData:
    #     print(prodData[0]['id'])
    #
    # if stagData:
    #     print(stagData[0]['id'])
    count = 1
    json_objects = []

    if sanityDataset and stagData and prodData:
        with open('data-v4.ndjson', 'w') as file:

            for dataset in sanityDataset:
                tempObj = copy.deepcopy(dataset)
                if 'id' in dataset:

                    prodObj = search_object_by_key(prodData, 'id', dataset['id'])

                    if prodObj:

                        stagObj = search_object_by_key(stagData, 'name', prodObj['name'])

                        tempObj['id'] = stagObj['id']

                        # UPDATE MODIFIERS IDs START HERE
                        if 'modifierGroups' in tempObj:
                            for modifierGroups in tempObj['modifierGroups']:

                                for modifier in modifierGroups['modifiers']:
                                    prodModifier = search_array_by_key(prodObj['modifiers'], 'id', modifier['id'])
                                    stagModifier = search_array_by_key(stagObj['modifiers'], 'display_name',
                                                                       prodModifier['display_name'])
                                    modifier['id'] = stagModifier['id']
                        # UPDATE MODIFIERS IDs ENDS HERE

                        # UPDATE INCOMPATIBILITIES IDs START HERE
                        if 'incompatibilities' in tempObj:

                            for incompatibility in tempObj['incompatibilities']:

                                prodModifierValue = find_modifier_option_by_key(prodObj['modifiers'], 'id',
                                                                                incompatibility['modifierValueId'])

                                stagModifierValue = None
                                if prodModifierValue:
                                    stagModifierValue = find_modifier_option_by_key(stagObj['modifiers'], 'label',
                                                                                    prodModifierValue['label'])

                                if stagModifierValue:
                                    incompatibility['modifierValueId'] = stagModifierValue['id']

                                # UPDATE INCOMPATIBILITIES IDs ENDS HERE

                                # UPDATE incompatibleModifierValueIds IDs START HERE
                                tempIncompatibleModifierValueIds = []
                                if 'incompatibleModifierValueIds' in incompatibility:

                                    for incompatibleModifierValueId in incompatibility['incompatibleModifierValueIds']:
                                        prodIncompatibleModifierValueIdObj = find_modifier_option_by_key(
                                            prodObj['modifiers'], 'id', incompatibleModifierValueId)

                                        stagIncompatibleModifierValueIdObj = None
                                        if prodIncompatibleModifierValueIdObj:
                                            stagIncompatibleModifierValueIdObj = find_modifier_option_by_key(
                                                stagObj['modifiers'], 'label',
                                                prodIncompatibleModifierValueIdObj['label'])
                                        if stagIncompatibleModifierValueIdObj:
                                            tempIncompatibleModifierValueIds.append(
                                                stagIncompatibleModifierValueIdObj['id'])

                                incompatibility['incompatibleModifierValueIds'] = tempIncompatibleModifierValueIds
                                # UPDATE incompatibleModifierValueIds IDs ENDS HERE

                file.write(json.dumps(tempObj) + '\n')

    else:
        print('Whoops ! Something Went Wrong')

    print('Done')


if __name__ == "__main__":
    main()
