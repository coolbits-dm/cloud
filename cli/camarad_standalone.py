#!/usr/bin/env python3
import click, requests, os, json
API = os.getenv('CAMARAD_API', 'https://camarad.ai/api/agents/query')
CACHE_DIR = os.path.join(os.path.expanduser('~'), '.camarad', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, 'responses.json')

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

@click.group()
@click.version_option(version='Camarad CLI vΔ-∞ – Empire online')
def cli(): pass

@cli.command()
@click.argument('query')
@click.option('--byok', is_flag=True, help='Use your real key')
def execute(query, byok):
    cache = load_cache()
    if query in cache:
        click.echo(cache[query])
        return
    headers = {}
    if byok:
        key = click.prompt('Your API key', hide_input=True)
        headers['X-API-Key'] = key
    r = requests.post(API, json={'query': query}, headers=headers)
    response = r.json()
    cache[query] = response
    save_cache(cache)
    click.echo(response)

@cli.command()
@click.option('--emperor-mode', is_flag=True, help='Emperor mode')
@click.option('--tone', default='normal', help='Tone of the response')
def exec(emperor_mode, tone):
    if emperor_mode and tone == 'fuckin-go':
        click.echo('Emperor mode activated. Fuckin’ go.')
        click.echo('€ tick. € tick. € tick.')
        click.echo('Done.')
    else:
        click.echo('Camarad Protocol Δ-10')
        click.echo('∞')

if __name__ == '__main__':
    cli()

# Installation:
# pip install click requests
# python camarad.py execute 'status billing'
# python camarad.py exec --emperor-mode --tone=fuckin-go
