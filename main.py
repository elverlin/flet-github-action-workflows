import flet as ft
import requests
import base64
import json

from typing import Any


def main(page: ft.Page):
    page.padding = 0
    page.title = "My animes"
    page.bgcolor = "#050117"
    
    
    
    
    class Section(ft.Container):
        def __init__(self, section_texte, is_multiline, on_submit):
            super().__init__()
            self.is_multiline = is_multiline
            self.on_submit = on_submit
            
            self.margin = ft.margin.symmetric(horizontal=10, vertical=5)
            
            self.section_name: ft.Container = self.create_banner(texte=section_texte)
            self.section_entry: ft.TextField = ft.TextField(**self.section_entry_style())
            
            self.content: ft.Row = ft.Column([self.section_name, self.section_entry])
         
        
        def section_entry_style(self) -> dict[str, Any]:
            return{
                "border_radius" : 5, 
                "border_color" : "white", 
                "on_submit" : self.on_submit,
                "multiline" : self.is_multiline,
                "content_padding" : ft.padding.symmetric(vertical=1, horizontal=7)
            }

        def banner_style(self, texte: str) -> dict[str, Any]:
            return {
                "height": 30,
                "bgcolor": "#c20000",
                "border_radius" : 6,
                "alignment": ft.alignment.center,
                "content": ft.Text(value=texte, size=17, weight=ft.FontWeight.BOLD, color="white")
            }
        
        
        def create_banner(self, texte: str) -> ft.Container:
            return ft.Container(content=ft.Container(**self.banner_style(texte=texte)), margin=ft.margin.only(top=10))

    class Add_Episode(ft.Container):
        def __init__(self, on_click_event):
            super().__init__()
            self.margin = ft.margin.symmetric(horizontal=10, vertical=5)
            
            self.banner = self.create_banner(texte="Ajouter un épisode")
            self.episode_number = ft.TextField(**self.entry_style(hint_text="Épisode N°"))
            self.episode_language = ft.Dropdown(**self.episode_language_style())
            self.episode_link = ft.TextField(**self.entry_style(hint_text="Lien de l'épisode"))
            self.submit_button = ft.FilledButton(text="Envoyer", style=ft.ButtonStyle(bgcolor="blue", color="white"), disabled=True, on_click=on_click_event)
            
            self.content = ft.Column([self.banner, self.episode_number, self.episode_language, self.episode_link, self.submit_button])
        
            
        def entry_style(self, hint_text) -> dict[str, Any]:
            return{
                "border_radius" : 5,
                "hint_text" : hint_text,
                "border_color" : "white", 
                "on_change" : self.check_entry,
                "content_padding" : ft.padding.symmetric(vertical=1, horizontal=7)
            }

        def banner_style(self, texte: str) -> dict[str, Any]:
            return {
                "height": 30,
                "bgcolor": "#c20000",
                "border_radius" : 6,
                "alignment": ft.alignment.center,
                "content": ft.Text(value=texte, size=17, weight=ft.FontWeight.BOLD, color="white")
            }
        
        def episode_language_style(self) -> dict[str, Any]:
            return{
                "value" : "VOSTFR", 
                "bgcolor" : "#c20000", 
                "options" : [ft.dropdown.Option("VOSTFR"), ft.dropdown.Option("VF")],
                "text_style" : ft.TextStyle(color="white", weight=ft.FontWeight.BOLD)
                
            }
        
        
        def create_banner(self, texte: str) -> ft.Container:
            return ft.Container(content=ft.Container(**self.banner_style(texte=texte)), margin=ft.margin.only(top=10))

        def check_entry(self, e):
            if self.episode_number.value != "" and self.episode_link.value != "":
                self.submit_button.style = ft.ButtonStyle(bgcolor="#c20000", color="white")
                self.submit_button.disabled = False
                self.update()
                
            else: 
                self.submit_button.style = ft.ButtonStyle(bgcolor="blue", color="white")
                self.submit_button.disabled = True
                self.update()

        def return_episode(self):
            episode_number = self.episode_number.value
            episode_language = self.episode_language.value
            episode_link = self.episode_link.value
            
            return f"{episode_number}:{episode_language}:{episode_link}"
        
    class Episodes(ft.Container):
        def __init__(self):
            super().__init__()
            self.margin = ft.margin.symmetric(horizontal=10, vertical=5)
            self.episodes_list = ft.ListView(controls=[])
            
            self.content = self.episodes_list
        
    class Controller(ft.Container):
        def __init__(self):
            super().__init__()
            self.expand = True
            
            self.notif = self.create_notif()
            page.overlay.append(self.notif)
            
            self.token_id = Section(section_texte="Token ID", is_multiline=False, on_submit=None)
            self.file_id = Section(section_texte="File ID", is_multiline=False, on_submit=self.get_fie_content)
            self.episodes = Episodes()
            self.add_episode = Add_Episode(on_click_event=self.submit_file_content)
            
            self.content = ft.Column([self.token_id, self.file_id, self.episodes, self.add_episode], scroll=ft.ScrollMode.ADAPTIVE)
        
        
        def notif_style(self) -> dict[str, Any]:
            return{
                "bgcolor" : "#c20000",
                "content" : ft.Text("", color="white", size=15, weight=ft.FontWeight.W_400)
            }
        
        
        def create_notif(self) -> ft.SnackBar:
            return ft.SnackBar(
                bgcolor="#c20000",
                content=ft.Text("", color="white", size=15, weight=ft.FontWeight.W_500)
            )    
            
        def get_fie_content(self, e):
            token = self.token_id.content.controls[1].value
            file_path = self.file_id.content.controls[1].value
            
            api_url = f"https://api.github.com/repos/elverlin/Data/contents/{file_path}.txt?ref=main"
            headers = {}

            if token:
                headers['Authorization'] = f'token {token}'

            try:
                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    file_content_encoded = response.json().get('content', '')
                    file_content = base64.b64decode(file_content_encoded).decode('utf-8')
                    
                    lines = file_content.splitlines()
                    for line_number, line in enumerate(lines, start=1):
                        self.episodes.content.controls.append(ft.Text(f"{line}"))
                        self.episodes.content.controls.append(ft.Divider(height=2))
                        self.update()
                        
                
                elif response.status_code == 404:
                    self.notif.content.value = "Fichier introuvable"
                    self.notif.open = True
                    page.update()
                    
                else:
                    self.notif.content.value = f"Erreur : Statut de la requête {response.status_code}."
                    self.notif.open = True
                    page.update()
                    
            except:
                self.notif.content.value = "Erreur de connexion"
                self.notif.open = True
                page.update()
        
        def get_github_file_content(self):
            token = self.token_id.content.controls[1].value
            file_path = self.file_id.content.controls[1].value
            
            api_url = f"https://api.github.com/repos/elverlin/Data/contents/{file_path}.txt?ref=main"
            headers = {}

            if token:
                headers['Authorization'] = f'token {token}'

            try:
                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    file_data = response.json()
                    file_content_encoded = file_data.get('content', '')
                    file_sha = file_data.get('sha', '')
                    file_content = base64.b64decode(file_content_encoded).decode('utf-8')
                    return file_content, file_sha
                elif response.status_code == 404:
                    return None, None
                else:
                    return f"Erreur : Statut de la requête {response.status_code}.", None
                
            except:
                self.notif.content.value = "Erreur de connexion"
                self.notif.open = True
                page.update()
        
        def submit_file_content(self, e):
            token = self.token_id.content.controls[1].value
            file_path = self.file_id.content.controls[1].value
            content_to_add = self.add_episode.return_episode()
            
            headers = {
                'Authorization': f'token {token}',
                'Content-Type': 'application/json'
            }
            
            current_content, file_sha = self.get_github_file_content()
            
            if current_content is None and file_sha is None:
                new_content = content_to_add
                message = f"Création du fichier {file_path}.txt avec le contenu spécifié."
                
            else:
                new_content = current_content + "\n" + content_to_add
                message = f"Mise à jour du fichier {file_path}.txt avec le nouveau contenu."

            
            encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')

            
            data = {
                "message": message,
                "content": encoded_content,
                "branch": "main"
            }

            if file_sha:
                data["sha"] = file_sha

            api_url = f"https://api.github.com/repos/elverlin/Data/contents/{file_path}.txt"
            response = requests.put(api_url, headers=headers, data=json.dumps(data))

            if response.status_code in [200, 201]:
                self.notif.content.value = "Épisode ajouté"
                self.notif.open = True
                page.update()
                
            else:
                self.notif.content.value = f"Erreur : {response.status_code}, {response.json()}"
                self.notif.open = True
                page.update()
    
    
    
    page.add(Controller())
    
    
    
ft.app(target=main)
