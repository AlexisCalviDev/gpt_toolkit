import json
import openai
import requests
import os
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from typing import Optional, Dict, Any
from rich.syntax import Syntax
import re


class GPTInterface:

    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.console = Console()

    def clean_json_response(self, response: str) -> str:
        # Supprimer les balises de code Markdown
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'\s*```', '', response)

        # Supprimer les sauts de ligne supplémentaires et les espaces en début/fin
        response = response.strip()

        return response

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
            json_example = json.dumps(json_format, indent=2)
            system_content = f"{assistant_description}. Tu dois impérativement répondre avec un JSON qui suit exactement" \
                             f" cette structure, en remplaçant les valeurs par le contenu approprié. Voici un exemple " \
                             f"de la structure attendue:\n\n{json_example}\n\nAssure-toi de respecter exactement cette " \
                             f"structure, en remplaçant uniquement les valeurs par le contenu généré."
        else:
            system_content = f"{assistant_description}. Tu dois répondre dans un format JSON."

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ]

        self.console.print(Panel.fit(f"Envoi de la requête", style="bold blue"))
        self.console.print(Panel.fit(f"system_content:{system_content}", style="bold blue"))
        self.console.print(Panel.fit(f"user_prompt:{user_prompt}", style="bold blue"))

        try:
            completions = openai.ChatCompletion.create(
                model=gpt_version,
                messages=messages,
                temperature=temperature
            )
            response_content = completions.choices[0].message['content']
            cleaned_content = self.clean_json_response(response_content)
            self.console.print(Panel.fit(f"Réponse reçue: {cleaned_content}", style="bold green"))

        except Exception as e:
            self.console.print(Panel.fit(f"Erreur lors de la requête GPT : {str(e)}", style="bold red"))
            raise

        try:
            response_json = json.loads(cleaned_content)

            print(f"Réponse reçue: {response_json}")
            return response_json

        except Exception as e:
            self.console.print(Panel.fit(f"Erreur lors de la transformation en JSON : {str(e)}", style="bold red"))
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


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    # Charger les variables d'environnement depuis un fichier .env
    load_dotenv()

    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv('OPENAI_API_KEY')

    # Créer une instance de GPTInterface
    gpt_interface = GPTInterface(api_key)

    # Exemple d'utilisation de from_prompt_to_gpt_json
    json_format = {
        "titre": "Titre de l'article",
        "contenu": "Contenu de l'article",
        "mots_cles": ["mot1", "mot2", "mot3"]
    }

    result = gpt_interface.from_prompt_to_gpt_json(
        user_prompt="Génère un court article sur l'intelligence artificielle",
        assistant_description="Tu es un assistant spécialisé en rédaction d'articles sur l'IA",
        json_format=json_format
    )

    print("Résultat de from_prompt_to_gpt_json:")
    print(json.dumps(result, indent=2))

    # Exemple d'utilisation de from_prompt_to_dalle_url
    image_url = gpt_interface.from_prompt_to_dalle_url(
        prompt="Un robot futuriste dans un laboratoire high-tech",
        output_path="robot_ia.jpg"
    )

    print(f"URL de l'image générée : {image_url}")