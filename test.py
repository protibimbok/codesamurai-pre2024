import requests
import json

BASE_URL = 'http://localhost:8000'

def run_tests(test_cases):
    score = 0
    results = ''
    no = 0
    for test_case in test_cases:
        no += 1
        test_score = 0
        path = test_case['url']
        method = test_case['method']
        json_body = None
        print("Test %d: %s %s" % (no, method, path))
        if method == 'PUT':
            json_body = json.loads(test_case['body'])
            response = requests.put(BASE_URL + path, json = json_body)
        elif method == 'POST':
            json_body = json.loads(test_case['body'])
            response = requests.post(BASE_URL + path, json = json_body)
        else:
            response = requests.get(BASE_URL + path)
        body = response.json()
        # if response.status_code == test_case['status']:
        #     test_score += 50
        #     if json.dumps(body) == json.dumps(test_case['expected']):
        #         test_score += 50
        results += 'Test ' + str(no) + ': '+method+' ' + path + '\n'
        # results += 'Expected: ' + json.dumps({
        #     'status': test_case['status'],
        #     'body': test_case['expected']
        # }) + '\n'
        results += 'Recieved: ' + json.dumps({
            'status': response.status_code,
            'body': body
        }) + '\n'
        # results += 'Score: ' + str(test_score)
        results += '\n\n'
        # score += test_score
        # print("Score: " + str(test_score) + "\n")
    # results += 'Total Score: ' + str(score) + '/' + str(no * 100)
    return results

if __name__ == "__main__":
    test_cases = []
    with open('preli_test_cases.log.txt') as f:
        test_case = {}
        is_jsoning = False
        is_test_case = False
        body = ''
        for line in f:
            line = line.strip()
            if is_jsoning:
                body += line
                if len(line) > 0:
                    continue
                is_jsoning = False
                is_test_case = False
                test_case['body'] = body
                test_cases.append(test_case)
                continue
            if is_test_case:
                [method, url] = line.split(' ', maxsplit = 2)
                test_case = {
                    'method': method,
                    'url': url
                }
                body = ''
                is_jsoning = True
                continue
            if line[:4] == 'Test':
                is_test_case = True

    with open('test_requests.log', 'w+') as file:
        file.write(json.dumps(test_cases, indent=2))
    
    with open('test_results.log', 'w+') as file:
        file.write(run_tests(test_cases))
    