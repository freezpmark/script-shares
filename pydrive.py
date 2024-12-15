

def document_template(content: dict):
    text = f"""# My Google Doc!

## Abstract

This is some introductory text.
We could have lorem ipsum'd it,
but that would be too generic for my tastes.
So instead, I have chosen to write freely from my mind.

## Section 1

- First bullet point
- Second bullet point

<hr class="pb">

## Section 2

{content["lorem ipsum"]}

| hello | world |
|:-----:|:-----:|
|  1  |  a  |
|  2  |  b  |

<hr class="pb">

"""
    return text

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from markdown import markdown

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
drive = GoogleDrive(gauth)

content = {"lorem ipsum": "Lorem ipsum dolor sit amet."}
text = document_template(content)
htmldoc = markdown(text)
gdoc = drive.CreateFile(
    {
        "title": "My Shiny New Google Doc from Python!",
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
)
gdoc.SetContentString(htmldoc)
gdoc.Upload()

a = 2


