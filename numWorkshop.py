
import requests
from typing import Dict, NamedTuple, NoReturn

from bs4 import BeautifulSoup


class WorkshopError(Exception):

    def __init__(self, error: str):
        self.error = error

    def __str__(self) -> str:
        return self.error


class Script(NamedTuple):
    """Encapsulate a numworks workshop python script."""
    name: str
    description: str
    content: str
    public: bool


class Workshop:

    def __init__(self, email: str, password: str):
        self.session = requests.Session()
        self.base_url = "workshop.numworks.com"
        user = {
            "email": email,
            "password": password
        }
        self.login(user)

    def login(self, user: Dict[str, str]) -> NoReturn:
        login = self.session.get(self.get_url("/users/sign_in"))
        soup = BeautifulSoup(login.text, "html.parser")
        authenticity_token = soup.find("input").get("value")

        payload = {
            "authenticity_token": authenticity_token,
            "commit": "Se connecter",
            "user[email]": user["email"],
            "user[password]": user["password"],
        }

        r = self.session.post(self.get_url("/users/sign_in"), data=payload)
        soup = BeautifulSoup(r.text, "html.parser").find(
                                ["ul", "li", "a"],
                                class_="dropdown-menu animated-dropdown-sm")
        self.python = soup.find_all("a")[1].get("href")

    def create_script(self, script: Script) -> NoReturn:
        # @todo : error if script allready exist...
        r = self.session.get(self.get_url(f"{self.python}/new"))
        soup = BeautifulSoup(r.text, "html.parser")
        authenticity_token = soup.find("input").get("value")

        payload = {
            "authenticity_token": authenticity_token,
            "commit": "Sauvegarder",
            "script[description]": script.description,
            "script[name]": f"{script.name.lower()}.py",
            "script[public]": int(script.public),
            "script[text_area_content]": script.content,
        }

        r = self.session.post(self.get_url(f"{self.python}"), data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        self.raise_errors(soup.find(id="error_explanation"))

    def edit_script(self, script: Script, name=None) -> NoReturn:
        r = self.session.get(self.get_url(f"{self.python}/{script.name}/edit"))
        soup = BeautifulSoup(r.text, "html.parser")
        authenticity_token = soup.find_all("input")[1].get("value")

        payload = {
            "_method": "patch",
            "authenticity_token": authenticity_token,
            "commit": "Sauvegarder",
            "script[description]": script.description,
            "script[name]": (f"{name.lower()}.py"
                             or f"{script.name.lower()}.py"),
            "script[public]": int(script.public),
            "script[text_area_content]": script.content,
        }

        r = self.session.post(self.get_url(f"{self.python}/{script.name}"),
                              data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        self.raise_errors(soup.find(id="error_explanation"))

        script.name = name or script.name

    def delete_script(self, script: Script) -> NoReturn:
        r = self.session.get(self.get_url(f"{self.python}/{script.name}"))

        soup = BeautifulSoup(r.text, "html.parser")
        authenticity_token = soup.find("meta",
                                       attrs={"name": "csrf-token"}).get(
                                           "content")

        payload = {
            "_method": "delete",
            "authenticity_token": authenticity_token,
        }

        r = self.session.post(self.get_url(f"{self.python}/{script.name}"),
                              data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        self.raise_errors(soup.find(id="error_explanation"))

    def get_script(self, url: str) -> Script:
        r = self.session.get(f"{url}")
        soup = BeautifulSoup(r.text, "html.parser")
        send_to_calculator = soup.find("send-to-calculator")

        script_name = send_to_calculator.get("script-name").split(".")[0]
        script_content = send_to_calculator.get("script-content")

        script_description = soup.find(class_="text-justify").text.strip("\n")

        if url[37:].split("/")[0] != self.python.split("/")[2]:
            script_public = True
        else:
            script_public = bool(soup.find(class_="text-success"))

        return Script(script_name,
                      script_description,
                      script_content,
                      script_public)

    def get_url(self, url: str) -> str:
        return f"https://{self.base_url}{url}"

    def raise_errors(self, errors: Exception) -> NoReturn:
        if errors:
            errors = (error.text for error in errors.find_all("li"))
            for error in errors:
                raise WorkshopError(error)
