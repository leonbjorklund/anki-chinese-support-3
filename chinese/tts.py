# Copyright © 2012 Roland Sieker <ospalh@gmail.com>
# Copyright © 2012 Thomas TEMPÉ <thomas.tempe@alysse.org>
# Copyright © 2017 Pu Anlai <https://github.com/InspectorMustache>
# Copyright © 2019 Oliver Rice <orice@apple.com>
# Copyright © 2017-2021 Joseph Lorimer <joseph@lorimer.me>
# Inspiration: Tymon Warecki
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html

import ssl
from os.path import basename, exists, join
from re import sub
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import requests
from aqt import mw
from gtts import gTTS
from gtts.tts import gTTSError

from .aws import AWS4Signer

requests.packages.urllib3.disable_warnings()


class AudioDownloader:
    def __init__(self, text, source='gcloud|zh-CN'):
        self.text = text
        self.service, self.lang = source.split('|')
        self.path = self.get_path()
        self.func = {
            'google': self.get_google,
            'baidu': self.get_baidu,
            'aws': self.get_aws,
            'gcloud': self.get_gcloud,
        }.get(self.service)

    def get_path(self):
        filename = '{}_{}_{}.mp3'.format(
            self.sanitize(self.text), self.service, self.lang
        )
        return join(mw.col.media.dir(), filename)

    def sanitize(self, s):
        return sub(r'[/:*?"<>|]', '', s)

    def download(self):
        if exists(self.path):
            return basename(self.path)

        if not self.func:
            raise NotImplementedError(self.service)

        self.func()

        return basename(self.path)

    def get_google(self):
        tts = gTTS(self.text, lang=self.lang, tld='com')
        try:
            tts.save(self.path)
        except gTTSError as e:
            print('gTTS Error: {}'.format(e))

    def get_gcloud(self):
        try:
            from google.cloud import texttospeech
            import random
            import os
            
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\lubjse\Desktop\Repos\tts-key.json"
            
            client = texttospeech.TextToSpeechClient()
            
            voices = [
                {"language_code": "cmn-CN", "name": "cmn-CN-Wavenet-A", "gender": texttospeech.SsmlVoiceGender.FEMALE},
                {"language_code": "cmn-CN", "name": "cmn-CN-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
                {"language_code": "cmn-CN", "name": "cmn-CN-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.MALE},
                {"language_code": "cmn-CN", "name": "cmn-CN-Wavenet-D", "gender": texttospeech.SsmlVoiceGender.FEMALE},
                {"language_code": "cmn-TW", "name": "cmn-TW-Wavenet-A", "gender": texttospeech.SsmlVoiceGender.FEMALE},
                {"language_code": "cmn-TW", "name": "cmn-TW-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
                {"language_code": "cmn-TW", "name": "cmn-TW-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.MALE},
            ]
            
            selected_voice = random.choice(voices)
            voice_name = selected_voice["name"]
            language_code = selected_voice["language_code"]
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name
            )
            
            synthesis_input = texttospeech.SynthesisInput(text=self.text)
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                pitch=random.uniform(-2, 2),
                speaking_rate=random.uniform(1.0, 1.10)
            )
            
            response = client.synthesize_speech(
                input=synthesis_input, 
                voice=voice, 
                audio_config=audio_config
            )
            
            with open(self.path, "wb") as out:
                out.write(response.audio_content)
        except Exception as e:
            print('Google Cloud TTS Error: {}'.format(e))

    def get_baidu(self):
        query = {
            'lan': self.lang,
            'ie': 'UTF-8',
            'text': self.text.encode('utf-8'),
            'spd': 2,
            'source': 'web',
        }

        url = 'https://fanyi.baidu.com/gettts?' + urlencode(query)
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')

        # baidu web server seems to behave nondeterministically when the alpn extension is not supplied where it
        # sometimes returns 200 OK but with Content-Length 0
        # when the extension is sent, the audio/mpeg content is returned as expected
        # automatically sending the alpn extension was added in python 3.10, but Anki is currently using 3.9
        context = ssl.create_default_context()
        context.set_alpn_protocols(['http/1.1'])

        with urlopen(request, context=context, timeout=5) as response, open(self.path, 'wb') as audio:
            if response.code != 200:
                raise ValueError('{}: {}'.format(response.code, response.msg))

            bytes_response = response.read()
            audio.write(bytes_response)

    def get_aws(self):
        signer = AWS4Signer(service='polly')
        signer.use_aws_profile('chinese_support_redux')

        url = 'https://polly.%s.amazonaws.com/v1/speech' % (signer.region_name)
        query = {
            'OutputFormat': 'mp3',
            'Text': self.text,
            'VoiceId': self.lang,
        }

        response = requests.post(url, json=query, auth=signer)

        if response.status_code != 200:
            raise ValueError(
                'Polly Request Failed: Error Code {}'.format(
                    response.status_code
                )
            )

        with open(self.path, 'wb') as audio:
            audio.write(response.content)

