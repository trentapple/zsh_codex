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

# Use the OpenAI API by default
organization_id, api_key, model, api_url = initialize_openai_api()

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}

save_var_grammar = (
#root ::= (
#    zsh-shell | zsh-command | zsh-conditional | zsh-loop | zsh-function | zsh-variable | zsh-alias | zsh-history | zsh-job | zsh-process | zsh-expansion | zsh-redirection | zsh-pipeline | zsh-subshell | zsh-arithmetic | zsh-completion | zsh-module | zsh-utility
#)
r"""

zsh-shell ::= zsh-command | zsh-conditional | zsh-loop | zsh-function | zsh-variable | zsh-alias | zsh-history | zsh-job | zsh-process | zsh-expansion | zsh-redirection | zsh-pipeline | zsh-subshell | zsh-arithmetic | zsh-completion | zsh-module | zsh-utility

zsh-command ::= "cd" | "ls" | "echo" | "mkdir" | "rm" | "touch" | "cat" | "grep" | "sed" | "awk" | "ps" | "kill" | "source" | "export" | "unalias" | "type" | "which" | "man" | "apropos" | "history" | "fc" | "bg" | "fg" | "jobs" | "disown" | "nohup" | "time" | "ulimit" | "exec" | "wait" | "true" | "false" | "test" | "builtin" | "command" | "declare" | "typeset" | "readonly" | "shift" | "return" | "break" | "continue"

zsh-conditional ::= "if" zsh-expression "then" zsh-shell "elif" zsh-expression "then" zsh-shell "else" zsh-shell "fi"

zsh-loop ::= "for" zsh-name "in" zsh-word-list "do" zsh-shell "done" | "while" zsh-expression "do" zsh-shell "done" | "until" zsh-expression "do" zsh-shell "done"

zsh-function ::= "function" zsh-name "{" zsh-shell "}"

zsh-variable ::= zsh-name "=" zsh-word

zsh-alias ::= "alias" zsh-name "=" zsh-word

zsh-history ::= "history" zsh-history-option

zsh-job ::= "bg" zsh-job-id | "fg" zsh-job-id | "jobs" zsh-job-option

zsh-process ::= "ps" zsh-process-option

zsh-expansion ::= zsh-parameter-expansion | zsh-command-substitution | zsh-arithmetic-expansion | zsh-process-substitution | zsh-history-expansion | zsh-filename-expansion | zsh-tilde-expansion

zsh-redirection ::= zsh-redirect | zsh-heredoc

zsh-pipeline ::= zsh-pipeline-element | zsh-pipeline "|" zsh-pipeline-element

zsh-subshell ::= "(" zsh-shell ")"

zsh-arithmetic ::= zsh-arithmetic-expression

zsh-completion ::= zsh-completion-command | zsh-completion-option

zsh-module ::= "zmodload" zsh-module-name | "zmodunload" zsh-module-name

zsh-utility ::= zsh-utility-command | zsh-utility-option

zsh-expression ::= zsh-word | zsh-test | zsh-arithmetic-expression

zsh-word ::= zsh-simple-word | zsh-double-quoted | zsh-single-quoted | zsh-parameter-expansion | zsh-command-substitution | zsh-arithmetic-expansion | zsh-process-substitution | zsh-history-expansion | zsh-filename-expansion | zsh-tilde-expansion

zsh-name ::= zsh-simple-word

zsh-word-list ::= zsh-word | zsh-word-list zsh-word

zsh-history-option ::= zsh-simple-word

zsh-job-id ::= zsh-simple-word

zsh-job-option ::= zsh-simple-word

zsh-process-option ::= zsh-simple-word

zsh-parameter-expansion ::= "${" zsh-name zsh-parameter-expansion-option "}"

zsh-parameter-expansion-option ::= zsh-parameter-length | zsh-parameter-offset | zsh-parameter-substring | zsh-parameter-replace | zsh-parameter-default | zsh-parameter-assign

zsh-parameter-length ::= "#" | "##"

zsh-parameter-offset ::= "%" | "%%"

zsh-parameter-substring ::= ":" zsh-parameter-substring-option

zsh-parameter-substring-option ::= zsh-parameter-substring-length | zsh-parameter-substring-offset-length

zsh-parameter-substring-length ::= zsh-simple-word

zsh-parameter-substring-offset-length ::= zsh-simple-word ":" zsh-simple-word

zsh-parameter-replace ::= "/" zsh-parameter-replace-pattern "/" zsh-parameter-replace-string zsh-parameter-replace-option

zsh-parameter-replace-pattern ::= zsh-simple-word

zsh-parameter-replace-string ::= zsh-simple-word

zsh-parameter-replace-option ::= zsh-parameter-replace-global | zsh-parameter-replace-case

zsh-parameter-replace-global ::= "/" | "//"

zsh-parameter-replace-case ::= "/#" | "/##" | "/%" | "/%%"

zsh-parameter-default ::= ":" zsh-parameter-default-value

zsh-parameter-default-value ::= zsh-simple-word

zsh-parameter-assign ::= "=" zsh-simple-word

zsh-command-substitution ::= "$(" zsh-shell ")"

zsh-arithmetic-expansion ::= "$((" zsh-arithmetic-expression "))"

zsh-process-substitution ::= "<(" zsh-shell ")" | ">(" zsh-shell ")"

zsh-history-expansion ::= "!" zsh-history-option

zsh-filename-expansion ::= zsh-simple-word | zsh-wildcard

zsh-wildcard ::= "*" | "?" | "[" zsh-wildcard-char-class "]"

zsh-wildcard-char-class ::= zsh-wildcard-char | zsh-wildcard-char "-" zsh-wildcard-char

zsh-wildcard-char ::= zsh-simple-word

zsh-tilde-expansion ::= "~" | "~" zsh-simple-word

zsh-test ::= "[" zsh-test-condition "]" | "[[" zsh-test-condition "]]"

zsh-test-condition ::= zsh-test-unary | zsh-test-binary

zsh-test-unary ::= zsh-test-file | zsh-test-string | zsh-test-variable

zsh-test-binary ::= zsh-test-comparison | zsh-test-regex

zsh-test-file ::= "-e" | "-f" | "-d" | "-h" | "-L" | "-p" | "-S" | "-b" | "-c" | "-t" | "-r" | "-w" | "-x" | "-s" | "-g" | "-u" | "-k" | "-O" | "-G" | "-N"

zsh-test-string ::= "-z" | "-n" | "=" | "!="

zsh-test-variable ::= "-v" | "-R"

zsh-test-comparison ::= "-eq" | "-ne" | "-lt" | "-le" | "-gt" | "-ge"

zsh-test-regex ::= "=~"

zsh-arithmetic-expression ::= zsh-arithmetic-term | zsh-arithmetic-expression zsh-arithmetic-operator zsh-arithmetic-term

zsh-arithmetic-term ::= zsh-arithmetic-factor | zsh-arithmetic-term zsh-arithmetic-operator zsh-arithmetic-factor

zsh-arithmetic-factor ::= zsh-arithmetic-atom | zsh-arithmetic-unary zsh-arithmetic-factor

zsh-arithmetic-atom ::= zsh-arithmetic-number | zsh-arithmetic-variable | "(" zsh-arithmetic-expression ")"

zsh-arithmetic-number ::= zsh-simple-word

zsh-arithmetic-variable ::= "$" zsh-name

zsh-arithmetic-unary ::= "+" | "-" | "!" | "~"

zsh-arithmetic-operator ::= "+" | "-" | "*" | "/" | "%" | "<<" | ">>" | "&" | "|" | "^" | "==" | "!=" | "<" | "<=" | ">" | ">="

zsh-completion-command ::= "compctl" | "compadd" | "compset" | "compunset" | "zle" | "bindkey" | "emulate" | "setopt" | "unsetopt" | "add-zsh-hook" | "add-zsh-load-hook" | "add-zsh-compdef"

zsh-completion-option ::= "-a" | "-A" | "-c" | "-C" | "-d" | "-D" | "-e" | "-E" | "-f" | "-F" | "-g" | "-G" | "-h" | "-H" | "-i" | "-I" | "-j" | "-J" | "-k" | "-K" | "-l" | "-L" | "-m" | "-M" | "-n" | "-N" | "-o" | "-O" | "-p" | "-P" | "-q" | "-Q" | "-r" | "-R" | "-s" | "-S" | "-t" | "-T" | "-u" | "-U" | "-v" | "-V" | "-w" | "-W" | "-x" | "-X" | "-y" | "-Y" | "-z" | "-Z"

zsh-module-name ::= zsh-simple-word

zsh-utility-command ::= "zargs" | "zmv" | "zcalc" | "zparseopts" | "zpty" | "ztcp" | "zsocket" | "zselect" | "zmq" | "zprof" | "zdump" | "zformat" | "zftp" | "zrun" | "zcompile" | "ztest" | "zstd" | "zutil" | "zef"

zsh-utility-option ::= zsh-simple-word
"""
)

data = {
    'model': model,
    #'prompt': full_command,
    'prompt': ['[INST] <<SYS>>\nYou are a zsh shell export, please help me complete the command, and only respond with the completed line.\n<</SYS>>\n\n' + full_command + ' [/INST]'],
    'input_prefix': prompt_prefix,
    'input_suffix': prompt_suffix,
    #'max_tokens': 512,
    'max_tokens': 192,
    'temperature': 0.5,
    'n': 1,
    'stop': '\n',
    #'grammar': save_var_grammar,
    #'stream': True,
}

if system_use_local_server:
    response = requests.post(f'{api_url}/completion', headers=headers, data=json.dumps(data))
    #response = requests.post(f'{api_url}/infill', headers=headers, data=json.dumps(data))
else:
    response = requests.post(f'{api_url}/v1/completions', headers=headers, data=json.dumps(data))

#print(response.content)
#print(response.text)

response_data = response.json()
if 'choices' in response_data:
    completed_command = response_data['choices'][0]['text']
else:
    completed_command = response_data['content']

#completed_command=completed_command[39:].replace(prompt_prefix, '')

# Optimistically remove the prompt prefix and incomplete command from the completion response
completed_command=completed_command[39:].replace('#!/bin/zsh\n\n', '')
completed_command=completed_command.replace(prompt_prefix, '')
completed_command=completed_command.replace(prompt_prefix.replace('#!/bin/zsh\n\n', ''), '')

#    print('Error: API response does not contain "choices" key')
#    sys.exit(1)

#sys.stdout.write(f"\n{completed_command.replace(prompt_prefix, '', 1)[36:]}")
sys.stdout.write(f"{completed_command.replace(prompt_prefix, '', 1)}")

#def initialize_openai_api():
#    """
#    Initialize the OpenAI API
#    """
#    # Check if file at API_KEYS_LOCATION exists
#    create_template_ini_file()
#    config = configparser.ConfigParser()
#    config.read(API_KEYS_LOCATION)
#
#    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
#    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")
#
#    if 'model' in config['openai']:
#        model = config['openai']['model'].strip('"').strip("'")
#    else:
#        model = 'gpt-3.5-turbo'
#
#    return model

#
#model = initialize_openai_api()
#
#cursor_position_char = int(sys.argv[1])
#
## Read the input prompt from stdin.
#buffer = sys.stdin.read()
#prompt_prefix = '#!/bin/zsh\n\n' + buffer[:cursor_position_char]
#prompt_suffix = buffer[cursor_position_char:]
#full_command = prompt_prefix + prompt_suffix
#response = openai.ChatCompletion.create(model=model, messages=[
#    {
#        "role":'system',
#        "content": "You are a zsh shell expert, please help me complete the following command, \
#you should only output the completed command, no need to include any other explanation",
#    },
#    {
#        "role":'user',
#        "content": full_command,
#    }
#])
#completed_command = response['choices'][0]['message']['content']
#
#sys.stdout.write(f"\n{completed_command.replace(prompt_prefix, '', 1)}")
