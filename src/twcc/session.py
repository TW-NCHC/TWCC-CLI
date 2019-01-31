# -*- coding: utf-8 -*-
import copy
import errno
import os
import re
from twcc.util import *
from PyInquirer import Validator, ValidationError, prompt
from PyInquirer import style_from_dict, Token

class TwccApiValidator(Validator):
    def validate(self, document):
        ok = re.match('^([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a TWCC API key',
                cursor_position=len(document.text))  # Move cursor to end
custom_style_2 = style_from_dict({
    Token.Separator: '#6C6C6C',
    Token.QuestionMark: '#FF9D00 bold',
    #Token.Selected: '',  # default
    Token.Selected: '#5F819D',
    Token.Pointer: '#FF9D00 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#5F819D bold',
    Token.Question: '',
})

quest_api = [
    {
        'type': 'input',
        'name': 'TWCC_API_KEY',
        'message': "Your API Key from www.TWCC.ai",
        'validate': TwccApiValidator
    },
    {
        'type': 'input',
        'name': 'TWCC_KEY_NAME',
        'message': "Enter Key Name for this key",
    },
]

class Session(object):

    def __init__(self,
                 twcc_yaml_path=None,
                 twcc_session=None):

        self.files = {}
        self.twcc_yaml_path = twcc_yaml_path

        self.files["credential"] = os.path.join(
            os.environ['TWCC_DATA_PATH'], "credential")
        self.files["resources"] = os.path.join(
            os.environ['TWCC_DATA_PATH'], "resources")

        if self.is_files_exist():
            self.load_session()
        else:
            self.create_session()


    def is_files_exist(self):
        for fn in self.files.keys():
            if not os.path.isfile(self.files[fn]):
                return False
        return True

    def create_session(self):
        answers = prompt(quest_api)
        API_KEY = answers['TWCC_API_KEY']
        KEY_NAME = answers['TWCC_KEY_NAME']
        self.convertYaml(API_KEY, KEY_NAME)
        self._getProjects()
        self.load_session()

    def _getProjects(self):
        from twcc.services.base import acls, projects
        import json
        a = projects()
        a._csite_ = 'k8s-taichung-default' # TWCC allow k8s only
        cluster = a.getSites()[0]
        avl_proj = a.list()
        table_layout ("Proj for {0}".format(cluster), avl_proj, ['id', 'name'])
        quest_api = [
            { 'type': 'rawlist',
              'name': 'default_project',
              'message': "Default *PROJECT_ID* when using TWCC-Cli:",
              'choices': [ "{} - {}".format(x['id'], x['name']) for x in avl_proj ],
            }]
        answers = prompt(quest_api, style=custom_style_2)
        proj_id = answers['default_project'].split(" - ")[0]
        # @todo here!
        fn_cred = self.files['credential']
        open(fn_cred, 'a+').write("twcc_proj_id={}\n".format(proj_id))



    def load_session(self):
        self.yaml = self.files['resources']

        self.credentials = {}
        cnt = open(self.files['credential'], 'r').readlines()
        for li in cnt:
            li = li.strip()
            if not re.search("^\[default]", li):
                key, val = li.split("=")

                if key == "twcc_host":
                    self.host = val
                elif key == "twcc_api_key":
                    (key_u, key_v) = val.split(":")
                    self.credentials[key_u] = key_v
                elif key == "twcc_ssh_key":
                    self.ssh_key = val
                elif key == "twcc_proj_id":
                    self.def_proj = val

        if len(self.credentials.keys())>=1:
            #print(type(self.credentials.keys()))
            self.default_key = self.credentials.keys()[0]
            #self.default_key = self.credentials.keys()

        self.clusters = {}
        import yaml
        config = yaml.load(open(self.yaml, 'r').read())
        self.clusters = config[ os.environ['_STAGE_'] ]['clusters']
        del config

    def convertYaml(self, api_key, key_name):
        """
        Todo:
           * need to change
        """
        if not os.path.exists(os.environ['TWCC_DATA_PATH']):
            mkdir_p(os.environ['TWCC_DATA_PATH'])

        if not os.path.exists(self.files['resources']):
            from shutil import copyfile
            copyfile(self.twcc_yaml_path, self.files['resources'])

        if not os.path.exists(self.files['credential']):
            import yaml
            config = yaml.load(open(self.twcc_yaml_path, 'r').read())
            t_config = config[os.environ['_STAGE_']]

            mbuf = ""
            if 'host' in t_config:
                mbuf += "[default]\n"
                mbuf += "twcc_host={0}\n".format(t_config['host'])
            mbuf += "twcc_api_key={0}:{1}\n".format(key_name, api_key)
            #mbuf += "twcc_ssh_key={}\n".format(ssh_key_name)
            open(self.files['credential'], 'w').write(mbuf)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def session_start():
    if not '_TWCC_SESSION_' == globals():
        TWCC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return Session( twcc_yaml_path="{}/yaml/NCHC_API-Test_env.yaml".format(TWCC_PATH) )
    else:
        global _TWCC_SESSION_
        return _TWCC_SESSION_

