# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
import json
import base64
import websockets
import asyncio

from websockets.sync.client import connect
from websockets.client import connect as async_connect

from .core.api_error import ApiError
from .core.jsonable_encoder import jsonable_encoder
from .core.remove_none_from_dict import remove_none_from_dict
from .core.request_options import RequestOptions
from .types.voice_settings import VoiceSettings
from .text_to_speech.client import TextToSpeechClient, AsyncTextToSpeechClient
from .types import OutputFormat
from .text_to_speech.types.text_to_speech_stream_with_timestamps_response import TextToSpeechStreamWithTimestampsResponse

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


def text_chunker(chunks: typing.Iterator[str]) -> typing.Iterator[str]:
    """Used during input streaming to chunk text blocks and set last char to space"""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""
    for text in chunks:
        if buffer.endswith(splitters):
            yield buffer if buffer.endswith(" ") else buffer + " "
            buffer = text
        elif text.startswith(splitters):
            output = buffer + text[0]
            yield output if output.endswith(" ") else output + " "
            buffer = text[1:]
        else:
            buffer += text
    if buffer != "":
        yield buffer + " "

async def async_text_chunker(chunks: typing.AsyncIterator[str]) -> typing.AsyncIterator[str]:
    """Used during input streaming to chunk text blocks and set last char to space"""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""
    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer if buffer.endswith(" ") else buffer + " "
            buffer = text
        elif text.startswith(splitters):
            output = buffer + text[0]
            yield output if output.endswith(" ") else output + " "
            buffer = text[1:]
        else:
            buffer += text
    if buffer != "":
        yield buffer + " "

class RealtimeTextToSpeechClient(TextToSpeechClient):

    def convert_realtime(
        self,
        voice_id: str,
        *,
        text: typing.Iterator[str],
        model_id: typing.Optional[str] = OMIT,
        output_format: typing.Optional[OutputFormat] = "mp3_44100_128",
        voice_settings: typing.Optional[VoiceSettings] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[bytes]:
        """
        Converts text into speech using a voice of your choice and returns audio.

        Parameters:
            - voice_id: str. Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.
            
            - text: typing.Iterator[str]. The text that will get converted into speech.

            - model_id: typing.Optional[str]. Identifier of the model that will be used, you can query them using GET /v1/models. The model needs to have support for text to speech, you can check this using the can_do_text_to_speech property.

            - voice_settings: typing.Optional[VoiceSettings]. Voice settings overriding stored setttings for the given voice. They are applied only on the given request.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from elevenlabs import PronunciationDictionaryVersionLocator, VoiceSettings
        from elevenlabs.client import ElevenLabs

        def get_text() -> typing.Iterator[str]:
            yield "Hello, how are you?"
            yield "I am fine, thank you."

        client = ElevenLabs(
            api_key="YOUR_API_KEY",
        )
        client.text_to_speech.convert_realtime(
            voice_id="string",
            text=get_text(),
            model_id="string",
            voice_settings=VoiceSettings(
                stability=1.1,
                similarity_boost=1.1,
                style=1.1,
                use_speaker_boost=True,
            ),
        )
        """
        with connect(
            urllib.parse.urljoin(
              "wss://api.elevenlabs.io/", 
              f"v1/text-to-speech/{jsonable_encoder(voice_id)}/stream-input?model_id={model_id}&output_format={output_format}"
            ),
            additional_headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            )
        ) as socket:
            try:
                socket.send(json.dumps(
                    dict(
                        text=" ",
                        try_trigger_generation=True,
                        voice_settings=voice_settings.dict() if voice_settings else None,
                        generation_config=dict(
                            chunk_length_schedule=[50],
                        ),
                    )
                ))
            except websockets.exceptions.ConnectionClosedError as ce:
                raise ApiError(body=ce.reason, status_code=ce.code)

            try:
                for text_chunk in text_chunker(text):
                    data = dict(text=text_chunk, try_trigger_generation=True)
                    socket.send(json.dumps(data))
                    try:
                        data = json.loads(socket.recv(1e-4))
                        if "audio" in data and data["audio"]:
                            yield base64.b64decode(data["audio"])  # type: ignore
                    except TimeoutError:
                        pass

                socket.send(json.dumps(dict(text="")))

                while True:

                    data = json.loads(socket.recv())
                    if "audio" in data and data["audio"]:
                        yield base64.b64decode(data["audio"])  # type: ignore
            except websockets.exceptions.ConnectionClosed as ce:
                if "message" in data:
                    raise ApiError(body=data, status_code=ce.code)
                elif ce.code != 1000:
                    raise ApiError(body=ce.reason, status_code=ce.code)


    def convert_realtime_full(
        self,
        voice_id: str,
        *,
        text: typing.Iterator[str],
        model_id: typing.Optional[str] = OMIT,
        output_format: typing.Optional[OutputFormat] = "mp3_44100_128",
        voice_settings: typing.Optional[VoiceSettings] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[TextToSpeechStreamWithTimestampsResponse]:
        """
        Converts text into speech using a voice of your choice and returns audio.

        Parameters:
            - voice_id: str. Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.

            - text: typing.Iterator[str]. The text that will get converted into speech.

            - model_id: typing.Optional[str]. Identifier of the model that will be used, you can query them using GET /v1/models. The model needs to have support for text to speech, you can check this using the can_do_text_to_speech property.

            - voice_settings: typing.Optional[VoiceSettings]. Voice settings overriding stored setttings for the given voice. They are applied only on the given request.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from elevenlabs import PronunciationDictionaryVersionLocator, VoiceSettings
        from elevenlabs.client import ElevenLabs

        def get_text() -> typing.Iterator[str]:
            yield "Hello, how are you?"
            yield "I am fine, thank you."

        client = ElevenLabs(
            api_key="YOUR_API_KEY",
        )
        client.text_to_speech.convert_realtime(
            voice_id="string",
            text=get_text(),
            model_id="string",
            voice_settings=VoiceSettings(
                stability=1.1,
                similarity_boost=1.1,
                style=1.1,
                use_speaker_boost=True,
            ),
        )
        """
        with connect(
            urllib.parse.urljoin(
                "wss://api.elevenlabs.io/",
                f"v1/text-to-speech/{jsonable_encoder(voice_id)}/stream-input?model_id={model_id}&output_format={output_format}"
            ),
            additional_headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            )
        ) as socket:
            try:
                socket.send(json.dumps(
                    dict(
                        text=" ",
                        try_trigger_generation=True,
                        voice_settings=voice_settings.dict() if voice_settings else None,
                        generation_config=dict(
                            chunk_length_schedule=[50],
                        ),
                    )
                ))
            except websockets.exceptions.ConnectionClosedError as ce:
                raise ApiError(body=ce.reason, status_code=ce.code)

            try:
                for text_chunk in text_chunker(text):
                    data = dict(text=text_chunk, try_trigger_generation=True)
                    socket.send(json.dumps(data))
                    try:
                        data = json.loads(socket.recv(1e-4))
                        yield data
                    except TimeoutError:
                        pass

                socket.send(json.dumps(dict(text="")))

                while True:

                    data = json.loads(socket.recv())
                    yield data
            except websockets.exceptions.ConnectionClosed as ce:
                if "message" in data:
                    raise ApiError(body=data, status_code=ce.code)
                elif ce.code != 1000:
                    raise ApiError(body=ce.reason, status_code=ce.code)


class AsyncRealtimeTextToSpeechClient(AsyncTextToSpeechClient):

    async def convert_realtime(
        self,
        voice_id: str,
        *,
        text: typing.AsyncIterator[str],
        model_id: typing.Optional[str] = OMIT,
        output_format: typing.Optional[OutputFormat] = "mp3_44100_128",
        voice_settings: typing.Optional[VoiceSettings] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[bytes]:
        """
        Converts text into speech using a voice of your choice and returns audio.

        Parameters:
            - voice_id: str. Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.
            
            - text: typing.Iterator[str]. The text that will get converted into speech.

            - model_id: typing.Optional[str]. Identifier of the model that will be used, you can query them using GET /v1/models. The model needs to have support for text to speech, you can check this using the can_do_text_to_speech property.

            - voice_settings: typing.Optional[VoiceSettings]. Voice settings overriding stored setttings for the given voice. They are applied only on the given request.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from elevenlabs import PronunciationDictionaryVersionLocator, VoiceSettings
        from elevenlabs.client import ElevenLabs

        def get_text() -> typing.Iterator[str]:
            yield "Hello, how are you?"
            yield "I am fine, thank you."

        client = ElevenLabs(
            api_key="YOUR_API_KEY",
        )
        client.text_to_speech.convert_realtime(
            voice_id="string",
            text=get_text(),
            model_id="string",
            voice_settings=VoiceSettings(
                stability=1.1,
                similarity_boost=1.1,
                style=1.1,
                use_speaker_boost=True,
            ),
        )
        """
        async with async_connect(
            urllib.parse.urljoin(
              "wss://api.elevenlabs.io/", 
              f"v1/text-to-speech/{jsonable_encoder(voice_id)}/stream-input?model_id={model_id}&output_format={output_format}"
            ),
            extra_headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            )
        ) as socket:
            try:
                await socket.send(json.dumps(
                    dict(
                        text=" ",
                        try_trigger_generation=True,
                        voice_settings=voice_settings.dict() if voice_settings else None,
                        generation_config=dict(
                            chunk_length_schedule=[50],
                        ),
                    )
                ))
            except websockets.exceptions.ConnectionClosedError as ce:
                raise ApiError(body=ce.reason, status_code=ce.code)

            try:
                async for text_chunk in async_text_chunker(text):
                    data = dict(text=text_chunk, try_trigger_generation=True)
                    await socket.send(json.dumps(data))
                    try:
                        async with asyncio.timeout(1e-4):
                            data = json.loads(await socket.recv())
                        if "audio" in data and data["audio"]:
                            yield base64.b64decode(data["audio"])  # type: ignore
                    except TimeoutError:
                        pass

                await socket.send(json.dumps(dict(text="")))

                while True:

                    data = json.loads(await socket.recv())
                    if "audio" in data and data["audio"]:
                        yield base64.b64decode(data["audio"])  # type: ignore
            except websockets.exceptions.ConnectionClosed as ce:
                if "message" in data:
                    raise ApiError(body=data, status_code=ce.code)
                elif ce.code != 1000:
                    raise ApiError(body=ce.reason, status_code=ce.code)

    async def convert_realtime_full(
        self,
        voice_id: str,
        *,
        text: typing.AsyncIterator[str],
        model_id: typing.Optional[str] = OMIT,
        output_format: typing.Optional[OutputFormat] = "mp3_44100_128",
        voice_settings: typing.Optional[VoiceSettings] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[TextToSpeechStreamWithTimestampsResponse]:
        """
        Converts text into speech using a voice of your choice and returns audio.

        Parameters:
            - voice_id: str. Voice ID to be used, you can use https://api.elevenlabs.io/v1/voices to list all the available voices.

            - text: typing.Iterator[str]. The text that will get converted into speech.

            - model_id: typing.Optional[str]. Identifier of the model that will be used, you can query them using GET /v1/models. The model needs to have support for text to speech, you can check this using the can_do_text_to_speech property.

            - voice_settings: typing.Optional[VoiceSettings]. Voice settings overriding stored setttings for the given voice. They are applied only on the given request.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        ---
        from elevenlabs import PronunciationDictionaryVersionLocator, VoiceSettings
        from elevenlabs.client import ElevenLabs

        def get_text() -> typing.Iterator[str]:
            yield "Hello, how are you?"
            yield "I am fine, thank you."

        client = ElevenLabs(
            api_key="YOUR_API_KEY",
        )
        client.text_to_speech.convert_realtime(
            voice_id="string",
            text=get_text(),
            model_id="string",
            voice_settings=VoiceSettings(
                stability=1.1,
                similarity_boost=1.1,
                style=1.1,
                use_speaker_boost=True,
            ),
        )
        """
        async with async_connect(
            urllib.parse.urljoin(
                "wss://api.elevenlabs.io/",
                f"v1/text-to-speech/{jsonable_encoder(voice_id)}/stream-input?model_id={model_id}&output_format={output_format}"
            ),
            extra_headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            )
        ) as socket:
            try:
                await socket.send(json.dumps(
                    dict(
                        text=" ",
                        try_trigger_generation=True,
                        voice_settings=voice_settings.dict() if voice_settings else None,
                        generation_config=dict(
                            chunk_length_schedule=[50],
                        ),
                    )
                ))
            except websockets.exceptions.ConnectionClosedError as ce:
                raise ApiError(body=ce.reason, status_code=ce.code)

            try:
                async for text_chunk in async_text_chunker(text):
                    data = dict(text=text_chunk, try_trigger_generation=True)
                    await socket.send(json.dumps(data))
                    try:
                        async with asyncio.timeout(1e-4):
                            data = json.loads(await socket.recv())
                        yield data
                    except TimeoutError:
                        pass

                await socket.send(json.dumps(dict(text="")))

                while True:

                    data = json.loads(await socket.recv())
                    yield data
            except websockets.exceptions.ConnectionClosed as ce:
                if "message" in data:
                    raise ApiError(body=data, status_code=ce.code)
                elif ce.code != 1000:
                    raise ApiError(body=ce.reason, status_code=ce.code)
