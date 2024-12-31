import requests
import csv
import os
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
client_id = os.getenv("CONNECTWISE_CLIENT_ID")
api_token = os.getenv("CONNECTWISE_ACCESS_TOKEN")

def add_device(devices, name, client, location, processor, compatible):
    device = {
        "Name": name,
        "Client": client,
        "Location": location,
        "Processor": processor,
        "Compatible": compatible
    }

    devices.append(device)

def load_cpu_model_data(csv_file):

    compatible_cpus = {}

    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                manufacturer = row["Manufacturer"]
                product_line = row["ProductLine"]
                model = row["Model"]

                if model not in compatible_cpus and model != "":
                    compatible_cpus[model] = {
                        "Manufacturer": manufacturer,
                        "ProductLine": product_line,
                    }

        return compatible_cpus

    except Exception as e:
        print(f"Error loading CPU model data: {e}")
        return None

def is_compatible_cpu(processor_name, compatible_cpus):
    for model in compatible_cpus.keys():
        if model in processor_name:
            return True
        
    return False

def get_computers(page_size=200):
    devices = []
    page_number = 1
    
    while True:
        try:
            print(f"Getting page {page_number} of computers...")
            url = f"https://snrmm.securenetworkers.com/cwa/api/v1/computers?includefields=computername,client,location&orderby=id asc&pagesize={page_size}&page={page_number}"
            payload = {}
            headers = {
                "Content-Type": "application/json",
                "ClientID": client_id,
                "Authorization": f"Bearer {api_token}"
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            response_data = response.json()

            if len(response_data) == 0:
                break

            devices.extend(response_data)
            page_number += 1

        except Exception as e:
            print(f"Page Number: {page_number} - Error getting computers: {e}")
            return None
        
    return devices
    
def get_processor(computer_id, computer_name, failed_retry_list, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            url = f"https://snrmm.securenetworkers.com/cwa/api/v1/computers/{computer_id}/processors?includefields=processorname"
            payload = {}
            headers = {
                "Content-Type": "application/json",
                "ClientID": client_id,
                "Authorization": f"Bearer {api_token}"
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f"Computer ID: {computer_id} - Error getting processor: {response.text}")
                return None
            
            response_data = response.json()

            if not response_data or not isinstance(response_data, list) or len(response_data) == 0:
                print(f"Computer ID: {computer_id} Name: {computer_name} - No processor found")
                return None
            
            if "ProcessorName" not in response_data[0]:
                print(f"Computer ID: {computer_id} Name: {computer_name}- No processor name found")
                return None
            
            return response_data[0]["ProcessorName"]
        
        except Exception as e:
            attempt += 1
            print(f"Computer ID: {computer_id} Name: {computer_name} Attempt: {attempt} - Error getting processor: {e}")
            time.sleep(2 ** attempt)
            
    print(f"Computer ID: {computer_id} Name: {computer_name} - Out of retries")
    failed_retry_list.append(computer_id)
    return None
    
def get_computers_and_processors(failed_retry_list):
    devices = []
    compatible_cpus = load_cpu_model_data("cpu_support.csv")
    computers = get_computers()
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_computer = {
            executor.submit(get_processor, computer["Id"], failed_retry_list, computer["ComputerName"]): computer for computer in computers
        }
        for future in future_to_computer:
            computer = future_to_computer[future]
            try:
                processor = future.result()
                compatible = None
                if processor is not None:
                    compatible = is_compatible_cpu(processor, compatible_cpus)
                add_device(devices, computer["ComputerName"], computer["Client"]["Name"], computer["Location"]["Name"], processor, compatible)
            except Exception as e:
                print(f"ID: {computer['Id']} Name: {computer["ComputerName"]} - Error getting processor: {e}")
                add_device(devices, computer["ComputerName"], computer["Client"]["Name"], computer["Location"]["Name"], None, None)

    return devices
    
def write_devices_to_csv(devices):
    try:
        with open('windows_11_compatibility.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(devices[0].keys())
            for device in devices:
                writer.writerow(device.values())
    except Exception as e:
        print(f"Error writing devices to CSV: {e}")

def main():
    failed_retry_list = []
    all_devices = get_computers_and_processors(failed_retry_list)
    if len(failed_retry_list) > 0:
        for computer_id in failed_retry_list:
            print(f"Failed Computer ID: {computer_id}")
    write_devices_to_csv(all_devices)

if __name__ == "__main__":
    main()
    