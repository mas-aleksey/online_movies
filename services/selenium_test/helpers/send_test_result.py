import os
import json
import base64
import requests
from helpers.settings import ALLURE_URL, PROJECT_ID

# This directory is where you have all your results locally, generally named as `allure-results`
allure_results_directory = '/allure-results'
# This url is where the Allure container is deployed. We are using localhost as example
allure_server = ALLURE_URL
# Project ID according to existent projects in your Allure container
# Check endpoint for project creation >> `[POST]/projects`
project_id = PROJECT_ID
# project_id = 'my-project-id'


current_directory = os.path.dirname(os.path.realpath(__file__))
project_directory = os.path.dirname(current_directory)
results_directory = project_directory + allure_results_directory


def clear_result_dir():
    files = os.listdir(results_directory)
    count = len(files)
    for file in files:
        full_path = os.path.join(results_directory, file)
        if os.path.exists(full_path):
            os.remove(full_path)
    print(f'Test results files \'{count}\' was deleted')


def send_results():
    print('RESULTS DIRECTORY PATH: ' + results_directory)

    files = os.listdir(results_directory)

    print('FILES:')
    results = []
    for file in files:
        result = {}

        file_path = results_directory + "/" + file
        print(file_path)

        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    if content.strip():
                        b64_content = base64.b64encode(content)
                        result['file_name'] = file
                        result['content_base64'] = b64_content.decode('UTF-8')
                        results.append(result)
                    else:
                        print('Empty File skipped: ' + file_path)
            finally:
                f.close()
        else:
            print('Directory skipped: ' + file_path)

    headers = {'Content-type': 'application/json'}
    request_body = {
        "results": results
    }
    json_request_body = json.dumps(request_body)

    ssl_verification = True

    print("----------------START-SEND-RESULTS----------------")
    res = requests.get(allure_server)
    print(res.text)
    response = requests.post(
        allure_server + '/allure-docker-service/send-results?project_id=' + project_id,
        headers=headers,
        data=json_request_body,
        verify=ssl_verification
    )
    print("STATUS CODE:")
    print(response.status_code)
    print("RESPONSE:")
    json_response_body = json.loads(response.content)
    json_prettier_response_body = json.dumps(json_response_body, indent=4, sort_keys=True)
    print(json_prettier_response_body)
    print("---------------FINISH-SEND-RESULTS---------------")

    # If you want to generate reports on demand use the endpoint `GET /generate-report`
    # and disable the Automatic Execution >> `CHECK_RESULTS_EVERY_SECONDS: NONE`
    """
    print("------------------GENERATE-REPORT------------------")
    execution_name = 'execution from my script'
    execution_from = 'http://google.com'
    execution_type = 'teamcity'
    response = requests.get(allure_server + '/allure-docker-service/generate-report?project_id=' + project_id + \
    '&execution_name=' + execution_name + '&execution_from=' + execution_from, '&execution_type=' + execution_type, \
    headers=headers, data=json_request_body, verify=ssl_verification)
    print("STATUS CODE:")
    print(response.status_code)
    print("RESPONSE:")
    json_response_body = json.loads(response.content)
    json_prettier_response_body = json.dumps(json_response_body, indent=4, sort_keys=True)
    print(json_prettier_response_body)
    print('ALLURE REPORT URL:')
    print(json_response_body['data']['report_url'])
    """


send_results()
clear_result_dir()
