import json
from openai import OpenAI
import requests
import os
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from typing import Optional, Dict, Any

class GPTInterface:

    def __init__(self, api_key: str):
        self.open_client = OpenAI(api_key=api_key)
        self.console = Console()

    def from_prompt_to_gpt_json(
            self,
            user_prompt: str,
            assistant_description: str,
            json_format: Optional[str] = None,
            temperature: float = 0,
            gpt_version: str = 'gpt-4-1106-preview'
    ) -> Dict[str, Any]:
        self.console.print(Panel.fit("Préparation de la requête GPT", style="bold magenta"))

        messages = [
            {"role": "system", "content": f"{assistant_description}. {'Tu dois impérativement répondre dans le format JSON suivant: ' + json_format if json_format else 'Tu dois répondre dans un format JSON.'}"},
            {"role": "user", "content": user_prompt}
        ]

        self.console.print(Panel.fit(f"Envoi de la requête à {gpt_version}", style="bold blue"))

        try:
            completions = self.open_client.chat.completions.create(
                model=gpt_version,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=temperature
            )

            completions_json = json.loads(completions.model_dump_json())
            response_content = json.loads(completions_json["choices"][0]['message']['content'])

            self.console.print(Panel.fit("Réponse reçue et parsée avec succès", style="bold green"))

            # Affichage de la réponse dans un tableau
            table = Table(title="Réponse GPT")
            for key, value in response_content.items():
                table.add_row(str(key), str(value))
            self.console.print(table)

            return response_content

        except Exception as e:
            self.console.print(Panel.fit(f"Erreur lors de la requête GPT : {str(e)}", style="bold red"))
            raise

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
            response = self.open_client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            image_url = response.data[0].url
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