# aiocertstream

An async client to connect to certstream in Python.

## Installation

- Windows: `pip install aiocertstream` or `py -3 -m pip install aiocertstream`
- *Nix: `pip3 install aiocertstream`

## Example usage

For this example we'll just print out the cert index:

```py
from aiocertstream import Client


client = Client()

@client.listen
async def my_handler(event: dict) -> None:
    print(event["data"]["cert_index"])

client.run()
```
