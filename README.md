# python_crypto

Based entirely off of [Cryptocurrency-cli](https://www.npmjs.com/package/cryptocurrency-cli)

Dependencies:

```bash
pip install click requests ascii_graph terminaltables pyinstaller python-dateutil
```

Then either:

`python main.py`

or:

`pyinstaller -F main.py`

Be sure to add a `portfolio.json` file to `dist/` before running the exe or ziping it.

Run `dist/main.exe` like normal. Pyinstaller will make an exe for the env you are currently working in (ex Windows).

Changing values in `portfolio.json` will reflect on the next cycle (6 second interval). For a complete list of coin and token ids, `Ctrl+f` your search [here](https://api.coinmarketcap.com/v1/ticker/?limit=0) (note: some tokens have unexpected ids [ex Golem <- golem-network-tokens])
