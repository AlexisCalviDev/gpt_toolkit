import json
import openai
import requests
import os
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from typing import Optional, Dict, Any

from json_schema_builder import JSONSchemaBuilder

class GPTInterface:

    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.console = Console()

    def from_prompt_to_gpt_json(
            self,
            user_prompt: str,
            assistant_description: str,
            json_format: Optional[Dict[str, Any]] = None,
            temperature: float = 0,
            gpt_version: str = 'gpt-4-1106-preview'
    ) -> Dict[str, Any]:
        self.console.print(Panel.fit("Préparation de la requête GPT", style="bold magenta"))

        if json_format:
            json_schema = JSONSchemaBuilder.create_schema(json_format)
            system_content = f"{assistant_description}. Tu dois impérativement répondre dans le format JSON suivant: {json.dumps(json_schema, indent=2)}"
        else:
            system_content = f"{assistant_description}. Tu dois répondre dans un format JSON."

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ]

        self.console.print(Panel.fit(f"Envoi de la requête à {gpt_version}", style="bold blue"))

        try:
            completions = openai.ChatCompletion.create(
                model=gpt_version,
                messages=messages,
                temperature=temperature
            )

            response_content = json.loads(completions.choices[0].message['content'])

            self.console.print(Panel.fit("Réponse reçue et parsée avec succès", style="bold green"))

            # Affichage de la réponse dans un tableau
            table = Table(title="Réponse GPT")
            self._add_to_table(table, response_content)
            self.console.print(table)

            return response_content

        except Exception as e:
            self.console.print(Panel.fit(f"Erreur lors de la requête GPT : {str(e)}", style="bold red"))
            raise

    def _add_to_table(self, table: Table, data: Dict[str, Any], prefix: str = ""):
        for key, value in data.items():
            if isinstance(value, dict):
                self._add_to_table(table, value, f"{prefix}{key}.")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._add_to_table(table, item, f"{prefix}{key}[{i}].")
                    else:
                        table.add_row(f"{prefix}{key}[{i}]", str(item))
            else:
                table.add_row(f"{prefix}{key}", str(value))

    def from_prompt_to_dalle_url(
            self,
            prompt: str,
            output_path: Optional[str] = None,
            model: str = 'dall-e-3',
            size: str = '1024x1792',
            quality: str = 'standard'
    ) -> str:
        self.console.print(Panel.fit("Préparation de la requête DALL-E", style="bold magenta"))

        try:
            response = openai.Image.create(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            image_url = response['data'][0]['url']
            self.console.print(Panel.fit("Image générée avec succès", style="bold green"))
            self.console.print(f"URL de l'image : [link={image_url}]{image_url}[/link]")

            if output_path:
                self.save_image(image_url, output_path)

            return image_url

        except Exception as e:
            self.console.print(Panel.fit(f"Erreur lors de la génération d'image : {str(e)}", style="bold red"))
            raise

    def save_image(self, image_url: str, output_path: str):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(output_path, 'wb') as file:
                file.write(response.content)
            self.console.print(Panel.fit(f"Image sauvegardée avec succès : {output_path}", style="bold green"))
        except Exception as e:
            self.console.print(Panel.fit(f"Erreur lors de la sauvegarde de l'image : {str(e)}", style="bold red"))
            raise