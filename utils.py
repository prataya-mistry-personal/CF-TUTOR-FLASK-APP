import random
import time
import hashlib

secret = '6ff906edd568e92953b150d085705c1f79ab1213'
key = '6ee48c1d17ce8849d9826ec5b485a74ba7d2d8fa'

def generate_sha512_hex(input_string):
    # return sha512 hash for the last part of api signature
    return hashlib.sha512(input_string.encode('utf-8')).hexdigest()

def generate_url(method_name:str, params:dict = {}) -> str:
    now_time = str(int(time.time()))
    curr_rand = str(random.randint(100000, 999999))
    params['time'] = now_time
    params['apiKey'] = key
    param_string = str
    param_string = '&'.join([f'{param}={params[param]}' for param in sorted(params)])
    param_string_2 = '&'.join([f'{param}={params[param]}' for param in params])
    # param_string += '&'
    api_signature = f'{curr_rand}{generate_sha512_hex(f'{curr_rand}/{method_name}?{param_string}#{secret}')}'
    url = f'https://codeforces.com/api/{method_name}?{param_string}&apiSig={api_signature}'

    print(f'{curr_rand}/{method_name}?apiKey={key}&{param_string}&time={now_time}#{secret}')
    print(generate_sha512_hex(f'{curr_rand}/{method_name}?apiKey={key}&{param_string}&time={now_time}#{secret}'))


    return url

def main():
    params = {
        'contestId': 566,
        'from': 1,
        'count': 1
    }
    # params = {'contestId': 566}

    MethodName = 'contest.standings'
    print(generate_url(MethodName, params))
    # a = generate_url('contest.standings', params)
    # print(a)

if __name__ == '__main__':
    main()

