import json
import os
import csv
from pathlib import Path

ROOT_PATH :str = Path(__file__).parents[2]

class FileFunctions:
    def __init__(self, file_name: str = None, template_name: str = None):

        self.base_dict = {'template_name': template_name, 
                          'image_file_name': file_name,               
                        }
        
        self.latest_key: str
        self.latest_region: str

    def add_image_file_name(self, image_file_name: str):
        self.base_dict['image_file_name'] = image_file_name

    def add_region(self):
        region_number = len(self.base_dict) - 1
        self.base_dict[f'region_{region_number}'] = {'title': None, 'key_values': {}}
        self.latest_region = f'region_{region_number}'

    def add_template_name(self, template_name: str):
        self.base_dict['template_name'] = template_name

    def add_title(self, title):
        self.base_dict[self.latest_region]['title'] = title

    def add_title_by_region(self, title, region):
        self.base_dict[region]['title'] = title

    def add_key(self, key):
        self.base_dict[self.latest_region]['key_values'][f'{key}'] = 0
        self.latest_key = f'{key}'

    def add_value(self, value):
        self.base_dict[self.latest_region]['key_values'][self.latest_key] = value

    def add_value_by_key(self, value, key):
        self.base_dict[self.latest_region]['key_values'][key] = value

    def save_template_json(self):
        file_path = self.create_file_path(self.base_dict.get('template_name'), file_type='json')
        with open(file_path, 'w') as file:
            json.dump(self.base_dict, file)
        
    @staticmethod
    def create_file_path(template_name: str, file_type: str = 'json') -> str:

        if file_type == 'json':
            storage_directory = os.path.join(ROOT_PATH, 'templates')
            file_path = os.path.join(storage_directory, f'{template_name}.json')

        elif file_type == 'csv':
            storage_directory = os.path.join(ROOT_PATH, 'reports')
            file_path = os.path.join(storage_directory, f'{template_name}.csv')

        else:
            raise ValueError(f'File type {file_type} is not supported.')

        return file_path

    @staticmethod
    def export_json_csv(dict_result: dict, csv_file_path: str):

        data = dict_result

        number_of_regions = len(data) - 2
        dict_items = {}

        for region_num in range(number_of_regions):
            dict_items[f'region_{region_num+1}'] = data[f'region_{region_num+1}']['key_values'].items()
            
        file_name = os.path.splitext(dict_result.get("image_file_name"))[0]
        csv_file = os.path.join(csv_file_path, f'{file_name}.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['region_title', 'topic', 'value'])
            writer.writeheader()

            for key_value, value in dict_items.items():
                writer.writerow({'region_title': data[key_value]['title']})
                writer.writerows([{'topic': key, 'value': value} for key, value in value])
                writer.writerow({})

        print(f"CSV file exported successfully: {csv_file_path}")

if __name__ == '__main__':

# ----- Example of using the functions to create a JSON file -----

    template_name = input("What is the name of this template? ")

    dict = FileFunctions(template_name=template_name)

    while True:

        dict.add_title(input("What is the title of this region? "))

        while True:
            dict.add_key(input("What is the key? "))
            dict.add_value(input("What is the value? "))
            if input("Do you want to add another key? ") == 'no':
                break

        if input("Do you want to add another region? ") == 'no':
            print(dict.base_dict)
            dict.save_template_json()
            FileFunctions.export_json_csv(dict.base_dict.get('template_name'))
            break

        else:
            dict.add_region()
