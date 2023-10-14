# BEGIN: 7d8f6a5gjwq1
#!/usr/bin/env python3

import requests
import json
import sys
import os
import configparser

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

# Read the organization_id and secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<your organization ID>
# secret_key=<your secret key>

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations
def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')
            f.write('model=gpt-3.5-turbo-0613\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
               'need to register for OpenAI Codex: \n'
                'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api(use_local_server=False):
    """
    Initialize the OpenAI API
    """
    if use_local_server:
        api_url = 'http://localhost:8080'
    else:
        api_url = 'https://api.openai.com'

    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    organization_id = config['openai']['organization_id'].strip('"').strip("'")
    api_key = config['openai']['secret_key'].strip('"').strip("'")

    if 'model' in config['openai']:
        model = config['openai']['model'].strip('"').strip("'")
    else:
        model = 'gpt-3.5-turbo'

    return organization_id, api_key, model, api_url


cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix

# Use the OpenAI API by default
organization_id, api_key, model, api_url = initialize_openai_api(use_local_server=False)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

data = {
    'model': model,
    'prompt': full_command,
    'max_tokens': 1024,
    'temperature': 0.5,
    'n': 1,
    'stop': '\n',
}

if use_local_server:
    response = requests.post(f'{api_url}/completions', headers=headers, data=json.dumps(data))
else:
    response = requests.post(f'{api_url}/v1/completions', headers=headers, data=json.dumps(data))

completed_command = response.json()['choices'][0]['text']

sys.stdout.write(f"\n{completed_command.replace(prompt_prefix, '', 1)}")
# END: 7d8f6a5gjwq1

import openai
import sys
import os
import configparser

# Get config dir from environment or default to ~/.config
CONFIG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
API_KEYS_LOCATION = os.path.join(CONFIG_DIR, 'openaiapirc')

# Read the organization_id and secret_key from the ini file ~/.config/openaiapirc
# The format is:
# [openai]
# organization_id=<your organization ID>
# secret_key=<your secret key>

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations
def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if not os.path.isfile(API_KEYS_LOCATION):
        with open(API_KEYS_LOCATION, 'w') as f:
            f.write('[openai]\n')
            f.write('organization_id=\n')
            f.write('secret_key=\n')
            f.write('model=gpt-3.5-turbo-0613\n')

        print('OpenAI API config file created at {}'.format(API_KEYS_LOCATION))
        print('Please edit it and add your organization ID and secret key')
        print('If you do not yet have an organization ID and secret key, you\n'
               'need to register for OpenAI Codex: \n'
                'https://openai.com/blog/openai-codex/')
        sys.exit(1)


def initialize_openai_api():
    """
    Initialize the OpenAI API
    """
    # Check if file at API_KEYS_LOCATION exists
    create_template_ini_file()
    config = configparser.ConfigParser()
    config.read(API_KEYS_LOCATION)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")

    if 'model' in config['openai']:
        model = config['openai']['model'].strip('"').strip("'")
    else:
        model = 'gpt-3.5-turbo'

    return model

model = initialize_openai_api()

cursor_position_char = int(sys.argv[1])

# Read the input prompt from stdin.
buffer = sys.stdin.read()
prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
prompt_suffix = buffer[cursor_position_char:]
full_command = prompt_prefix + prompt_suffix
response = openai.ChatCompletion.create(model=model, messages=[
    {
        "role":'system',
        "content": "You are a zsh shell expert, please help me complete the following command, you should only output the completed command, no need to include any other explanation",
    },
    {
        "role":'user',
        "content": full_command,
    }
])
completed_command = response['choices'][0]['message']['content']

sys.stdout.write(f"\n{completed_command.replace(prompt_prefix, '', 1)}")

