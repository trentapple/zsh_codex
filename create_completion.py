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

system_use_local_server = True

# If you don't see your organization ID in the file you can get it from the
# OpenAI web site: https://openai.com/organizations
def create_template_ini_file():
    """
    If the ini file does not exist create it and add the organization_id and
    secret_key
    """
    if system_use_local_server:
        return

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

def initialize_openai_api(use_local_server=system_use_local_server):
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

organization_id, api_key, model, api_url = initialize_openai_api(use_local_server=system_use_local_server)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

data = {
    'model': model,
    'prompt': full_command,
    #'max_tokens': 1024,
    'max_tokens': 512,
    'temperature': 0.5,
    'n': 1,
    'stop': '\n',
}

if system_use_local_server:
    response = requests.post(f'{api_url}/completion', headers=headers, data=json.dumps(data))
else:
    response = requests.post(f'{api_url}/v1/completions', headers=headers, data=json.dumps(data))

response_data = response.json()
if 'choices' in response_data:
    completed_command = response_data['choices'][0]['text']
else:
    completed_command = response_data['content']

#sys.stdout.write(f"\n{completed_command.replace(prompt_prefix, '', 1)}")

sys.stdout.write(f"{completed_command.replace(prompt_prefix, '', 1)}")
