## Development

Run a development server

```
uvicorn findthatpostcode:app --reload
```

## Testing

```sh
python -m pytest
```

Using coverage:

```sh
coverage run -m pytest && coverage html
python -m http.server -d htmlcov 8001
```

## Linting/formatting

```sh
ruff .
ruff format --check .
```

```sh
ruff . --fix
ruff format .
```
