# Cutest Picture — make.fun bounty `cutest-picture-01`

A tiny deterministic program that draws one cute picture: a kitten
face with big shiny eyes, pink blush cheeks, a tiny nose, whiskers
and a little bow, on a soft pastel background with polka dots.

## Run it

Requires Python 3.13 (stdlib only, no network, no dependencies):

```sh
python3 main.py
```

It writes the picture to `/output/entry.png` (override with the
`ENTRY_OUTPUT` environment variable). 1024x1024 PNG, about 13 KB.
Run it twice and the output is byte-identical (~1 s per run).

## Files

- `main.py` — the program (stdlib only; own PNG encoder via zlib)
- `LICENSE` — MIT
