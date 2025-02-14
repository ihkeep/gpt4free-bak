
import sys, re
from pathlib import Path
from os import path

sys.path.append(str(Path(__file__).parent.parent))

import g4f

def read_code(text):
    match = re.search(r"```(python|py|)\n(?P<code>[\S\s]+?)\n```", text)
    if match:
        return match.group("code")

def read_result(result):
    lines = []
    for line in result.split("\n"):
        if (line.startswith("```")):
            break
        if (line):
            lines.append(line)
    explanation = "\n".join(lines) if lines else ""
    return explanation, read_code(result)

def input_command():
    print("Enter/Paste the cURL command. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    contents = []
    while True:
        try:
            line = input()
        except:
            break
        contents.append(line)
    return "\n".join(contents)

name = input("Name: ")
provider_path = f"g4f/Provider/{name}.py"

example = """
from __future__ import annotations

from aiohttp import ClientSession

from ..typing       import AsyncGenerator
from .base_provider import AsyncGeneratorProvider
from .helper        import format_prompt


class ChatgptDuo(AsyncGeneratorProvider):
    url                   = "https://chat-gpt.com"
    supports_gpt_35_turbo = True
    working               = True

    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: list[dict[str, str]],
        **kwargs
    ) -> AsyncGenerator:
        headers = {
            "authority": "chat-gpt.com",
            "accept": "application/json",
            "origin": cls.url,
            "referer": f"{cls.url}/chat",
        }
        async with ClientSession(headers=headers) as session:
            prompt = format_prompt(messages),
            data = {
                "prompt": prompt,
                "purpose": "ask",
            }
            async with session.post(cls.url + "/api/chat", json=data) as response:
                response.raise_for_status()
                async for stream in response.content:
                    if stream:
                        yield stream.decode()
"""

if not path.isfile(provider_path):
    command = input_command()

    prompt = f"""
Create a provider from a cURL command. The command is:
```bash
{command}
```
A example for a provider:
```py
{example}
```
The name for the provider class:
{name}
Replace "hello" with `format_prompt(messages)`.
And replace "gpt-3.5-turbo" with `model`.
"""

    print("Create code...")
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_35_long,
        messages=[{"role": "user", "content": prompt}],
        auth=True,
        timeout=120,
    )
    print(response)
    explanation, code = read_result(response)
    if code:
        with open(provider_path, "w") as file:
            file.write(code)
        with open(f"g4f/Provider/__init__.py", "a") as file:
            file.write(f"\nfrom .{name} import {name}")
else:
    with open(provider_path, "r") as file:
        code = file.read()
