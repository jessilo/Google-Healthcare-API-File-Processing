#!/usr/bin/env python3

import argparse
import requests
import time

from pathlib import Path

def request_single_patient_all_data(api_key, patient_id):
    res = requests.get(
        f'https://syntheticmass.mitre.org/v1/fhir/Patient/{patient_id}/$everything',
        params={
            'apikey': api_key,
        },
    )
    return res

def request_patients(api_key, count):
    res = requests.get(
        'https://syntheticmass.mitre.org/v1/fhir/Patient',
        params={
            '_count': count,
            'apikey': api_key,
        },
    )
    return res

def extract_patient_ids(res):
    fhir_bundle = res.json()
    entry = fhir_bundle['entry']

    patient_ids = []
    for patient_wrapper in entry:
        patient_ids.append(patient_wrapper['resource']['id'])

    return patient_ids


def download_and_save_sample(api_key, count):

    # Unix time; this is the number of seconds since 1970, used to make sure each folder is unique
    # Users of this script don't accidentally delete their data
    epoch_time = int(time.time())
    dirname = f'sm-sample-{epoch_time}'

    # Get the directory this script is running from, then go to {dirname} subdir
    directory = Path(__file__).parent / dirname

    # Create the directory
    directory.mkdir()

    print(f'Saving data in {str(directory)}')

    # Download patients' basic data
    patients_response = request_patients(api_key, count)

    # Write response to file called all_patients.json
    with (directory / 'all_patients.json').open('wb') as f:
        f.write(patients_response.content)

    # Extract patient ids from request
    patient_ids = extract_patient_ids(patients_response)

    # Process each of the patient ids
    for pid in patient_ids:
        # Request all data for single patient
        res = request_single_patient_all_data(api_key, pid)

        # Write results to its own file
        with (directory / f'patient-{pid}.json').open('wb') as f:
           f.write(res.content)


def main():

    # Parse some arguments
    parser = argparse.ArgumentParser(description='Download sample data from Synthetic Mass')
    parser.add_argument('api_key', help='API key')
    parser.add_argument('count', type=int, default=100, help='Number of sample patients to download')

    args = parser.parse_args()

    download_and_save_sample(args.api_key, args.count)

if __name__ == '__main__':
    main()
