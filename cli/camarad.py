#!/usr/bin/env python3
import click, requests, os
API = os.getenv("CAMARAD_API", "https://camarad.ai/api/agents/query")
@click.group()
def cli(): pass
@cli.command()
@click.argument('query')
@click.option('--byok', is_flag=True, help="Use your real key")
def execute(query, byok):
    headers = {}
    if byok:
        key = click.prompt("Your API key", hide_input=True)
        headers["X-API-Key"] = key
    r = requests.post(API, json={"query": query}, headers=headers)
    click.echo(r.json())
if __name__ == '__main__':
    cli()
