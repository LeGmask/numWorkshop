import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class Script: 
    """Class for numworks workshop python script"""
    name: str
    description: str
    content: str
    public: bool

class Workshop:
    def __init__(self, email, password) -> None:
        self.session = requests.Session()
        self.baseUrl = "workshop.numworks.com"
        user = {
            "email": email,
            "password": password
        }
        self.login(user)

    def login(self, user):
        login = self.session.get(self.getUrl("/users/sign_in"))
        soup = BeautifulSoup(login.text, "html.parser")
        authenticity_token = soup.find("input").get("value")

        payload = {
            "authenticity_token": authenticity_token,
            "commit": "Se connecter",
            "user[email]": user["email"],
            "user[password]": user["password"],
        }

        r = self.session.post(self.getUrl("/users/sign_in"), data=payload)
        soup = BeautifulSoup(r.text, "html.parser").find(["ul","li","a"], class_="dropdown-menu animated-dropdown-sm")
        self.python = soup.find_all("a")[1].get("href")
        

    def createScript(self, script: Script):
        # @todo : error if script allready exist...
        r = self.session.get(self.getUrl(f"{self.python}/new"))
        soup = BeautifulSoup(r.text, "html.parser")
        authenticity_token = soup.find("input").get("value")

        payload = {
            "authenticity_token": authenticity_token,
            "commit": "Sauvegarder",
            "script[description]": script.description,
            "script[name]": f"{script.name.lower()}.py",
            "script[public]": 1 if script.public else 0, 
            "script[text_area_content]": script.content,
        }
        
        r = self.session.post(self.getUrl(f"{self.python}"), data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        self.raiseErrors(soup.find(id="error_explanation"))
            
        

    def editScript(self, script: Script, name=None):
        r = self.session.get(self.getUrl(f"{self.python}/{script.name}/edit"))
        soup = BeautifulSoup(r.text, "html.parser")
        authenticity_token = soup.find_all("input")[1].get("value")

        payload = {
            "_method": "patch",
            "authenticity_token": authenticity_token,
            "commit": "Sauvegarder",
            "script[description]": script.description,
            "script[name]": f"{name.lower()}.py" or f"{script.name.lower()}.py",
            "script[public]": 1 if script.public else 0,
            "script[text_area_content]": script.content,
        }

        r = self.session.post(self.getUrl(f"{self.python}/{script.name}"), data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        self.raiseErrors(soup.find(id="error_explanation"))

        script.name = name or script.name
        # print(r.text)

    def deleteScript(self, script: Script):
        r = self.session.get(self.getUrl(f"{self.python}/{script.name}"))

        soup = BeautifulSoup(r.text, "html.parser")
        authenticity_token = soup.find("meta", attrs={"name": "csrf-token"}).get("content")

        payload = {
            "_method": "delete",
            "authenticity_token": authenticity_token,
        }

        r = self.session.post(self.getUrl(f"{self.python}/{script.name}"), data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        self.raiseErrors(soup.find(id="error_explanation"))
    
    def getScript(self, url) -> Script:
        r = self.session.get(f"{url}")
        soup = BeautifulSoup(r.text, "html.parser")
        send_to_calculator = soup.find("send-to-calculator")

        scriptName = send_to_calculator.get("script-name").split(".")[0]
        scriptContent = send_to_calculator.get("script-content")

        scriptDescription = soup.find(class_="text-justify").text.strip("\n")
        if url[37:].split("/")[0] != self.python.split("/")[2]:
            scriptPublic = True
        else:
            scriptPublic = bool(soup.find(class_="text-success"))
            
        return Script(scriptName, scriptDescription, scriptContent, scriptPublic)


    def getUrl(self, url):
        return f"https://{self.baseUrl}{url}"
    
    def raiseErrors(self, errors):
        if errors:
            errors = [error.text for error in errors.find_all("li")]
            for error in errors:
                    raise Exception(error)


