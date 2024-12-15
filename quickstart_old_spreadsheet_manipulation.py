import json
import os
import random
import re
import time
import webbrowser
from sys import platform

import gspread
import numpy as np
import openai
import pyautogui
import pyperclip
import screeninfo
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import Translator

load_dotenv()
openai.api_key  = os.getenv('OPENAI_API_KEY')

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive"
]
TOKEN_PATH = "token.json"
VALS = [
        pyautogui.easeOutQuad,
        pyautogui.easeInQuad,
        pyautogui.easeInOutQuad,
        pyautogui.easeInBounce,
        pyautogui.easeInElastic
    ]
PROBS = [0.5, 0.25, 0.15, 0.05, 0.05]

MONTH_LABELS = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'september': 9, 
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

if platform == "linux" or platform == "linux2":
    CMD = "ctrl"
elif platform == "darwin":
    CMD = "command"
elif platform == "win32":
    CMD = "ctrl"

def get_credentials():
    creds = None
    credentials_dict_str = os.environ["GOOGLE_CREDENTIALS"]
    credentials_dict = json.loads(credentials_dict_str)

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when authorization flow completes for the 1. time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH)

        # authorization for gsheet
        with open(TOKEN_PATH, encoding='utf-8') as token_f:
            authorized_user = json.load(token_f)
            gc, _ = gspread.oauth_from_dict(credentials_dict, authorized_user)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(credentials_dict, SCOPES)

            # Turns on web browser to sign in with Google account
            input("A web browser will open for you to log in with your teaching Gmail account. After that, it will ask you to grant permission to access all necessary data. Come back when its done.\nPress Enter to start.")
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_PATH, "w", encoding='utf-8') as token_f:
            authorized_user_str = creds.to_json()  # to_string*
            token_f.write(authorized_user_str)

            authorized_user_json = json.loads(authorized_user_str)
            gc, _ = gspread.oauth_from_dict(credentials_dict, authorized_user_json)

    return creds, gc

def get_document(creds):
    service = build("docs", "v1", credentials=creds)
    prefix = "https://docs.google.com/document/d/"

    while True:
        try:
            # Retrieve the document contents from the Docs service.
            url_input = input("Please input the Google Docs URL from which you'd like to generate flashcards (make sure the URL has public access): ")
            # url_input = "https://docs.google.com/document/d/1F58bmSHdSPgbf2rHA1-l-RpXKUgdEzC9vqB7vkODQVo/edit"

            if url_input.startswith(prefix):
                document_id = url_input[len(prefix):].split("/", maxsplit=1)[0]
                document = service.documents().get(documentId=document_id).execute()
                return document
            else:
                print(f"Invalid URL. Please provide a valid Google Docs URL that starts with '{prefix}'.")
        except HttpError:
            print(f"Invalid URL ID ({document_id}). Please provide URL with a valid Google Docs ID.")

def get_lessons(document):
    separator_pattern = r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2}"

    text = ""
    lessons = []
    for line_dict in document["body"]["content"]:
        elements = line_dict.get("paragraph")
        if elements:
            bullet = elements.get("bullet")
            for ele in elements["elements"]:
                text_run = ele.get("textRun")
                if not text_run:
                    continue
                line = text_run["content"]
                match = re.match(separator_pattern, line)
                if match:
                    if text:
                        lessons.append(text)
                    text = line
                if bullet:
                    text += line

    if text:
        lessons.append(text)

    return lessons

# THIS GOT CHANGED IN ODOO VER
def get_expressions(lesson_str):
    lesson = lesson_str.splitlines()
    lesson_date = lesson[0]

    lesson_expressions = lesson[1:]
    star_expr = []
    norm_expr = []
    for i, expr in enumerate(lesson_expressions):
        # expr = re.sub(r"[가-힣]+", "", expr)
        expr = re.sub(r"\{\s*\}|\[\s*\]|\(\s*\)", "", expr)
        expr = expr.strip(" -/")
        if expr.endswith("*"):
            expr = expr[:-1:].strip(" -/")
            star_expr.append((expr, i))
        else:
            norm_expr.append((expr, i))

    # star_expr = sorted(star_expr, key=len)[::-1]
    return lesson_date, star_expr, norm_expr

# THIS GOT CHANGED IN ODOO VER
def select_expressions(star_expr, norm_expr, amount):

    # find longest normal expressions
    if amount > len(star_expr):
        # sorted_norm_expr = sorted(norm_expr, key=len)[::-1] (back when we had no index/tuples)
        sorted_norm_expr = sorted(norm_expr, key=lambda x: len(x[0]))[::-1]
        norm_expr_amount = amount - len(star_expr)
        norm_expr_select = sorted_norm_expr[:norm_expr_amount]
        expr_select_merged = star_expr + norm_expr_select
        expr_select = sorted(expr_select_merged, key=lambda x: x[1])
    else:
        expr_select = star_expr[:amount]

    expressions = [expr[0] for expr in expr_select]
    return expressions

def get_amount_input(lesson_date, star_expr_amount, norm_expr_amount):
    total_expressions = star_expr_amount + norm_expr_amount
    print(f"\nThe last lesson ({lesson_date}) contains {total_expressions} expressions:\n - {star_expr_amount} star expressions\n - {norm_expr_amount} normal expressions\nSpecify the number of expressions you'd like to use: ", end="")

    while True:
        try:
            amount_str = input()
            # amount_str = "8"
            amount = int(amount_str)
            if 2 < amount <= total_expressions:
                return amount
            else:
                print(f"Please enter a valid number between 3 and {total_expressions}: ")
        except ValueError:
            print("Invalid input. Please enter a valid number: ")

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message["content"]


def get_translation(selected_expr):
    print("\nWhich translator would you like to use?\n - 1 for Google translate\n - 2 for ChatGPT")
    while True:
        try:
            inp = input()
            # inp = "8"
            inp = int(inp)
            if 0 < inp < 3:
                if inp == 1:
                    print("Generating translation with Google translate... ")
                elif inp == 2:
                    print("Generating translation with ChatGPT 4... (it should take 1-2 minutes)")
                break
            else:
                print("Please enter a valid number: ")
        except ValueError:
            print("Invalid input. Please enter a valid number: ")

    to_translate = "\n".join(expr for expr in selected_expr)
    if inp == 1:
        translator = Translator()
        translation = translator.translate(to_translate, src="en", dest="ko")
        translated_exprs = translation.text.splitlines()

    # ? Make sure there is no korean text in English translation
    # ? 1. instruction - Use the following translation to enhance it further: {korean_text}
# Translate the English text into casual adult Korean tone while following these steps:
# 1. instruction - Ensure that there is no English text in the Korean translation
# 2. instruction - Avoid labeling the translation with phrases like "Korean" or "English"
# 3. instruction - Ensure incorporating the Korean words inside the brackets
# 4. instruction - Present the translations in a bullet list format, similar to the provided examples
# English text: {english_text}

# Create an improved version of the translation with higher quality and a more natural sounding tone.
# Utilize the following two different versions of translations:
# GPT translation: {gpt_translation}
# Google translation: {google_translation}

    else:
        prompt = (
            "Translate English text into casual adult Korean tone while following these instructions:"
            " - Ensure that there is no English text in Korean translation"
            " - Avoid labeling translation with phrases like 'Korean' or 'English'"
            " - In the English translation, ensure incorporating Korean words that are inside the brackets"
            " - Each translation must match the respective expression separated by a newline character, avoid adding extra information from the next expression."
            f"English text: {to_translate}"
        )
        response = get_completion(prompt)
        splitted_resp = response.splitlines()
        translated_exprs = [x for x in splitted_resp if x]

    print("Done! Preparing Spreadsheets now...")
    return translated_exprs

def get_rows_for_sheet(lesson_title, selected_expr, translated_expr):
    rows = []
    for eng_expr, kor_expr in zip(selected_expr, translated_expr):
        rows.append((lesson_title, eng_expr, kor_expr))

    return rows

def get_spreadsheet_id(creds, lesson_title, folder_name):
    service = build("drive", "v3", credentials=creds)

    folder_id, gsheet_id = search_spreadsheet(service, folder_name, lesson_title)

    # Create folder
    if not folder_id:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        folder = service.files().create(body=file_metadata).execute()
        folder_id = folder["id"]

    # Create gsheet
    if not gsheet_id:
        file_metadata = {
            'name': lesson_title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [folder_id]
        }
        gsheet = service.files().create(body=file_metadata).execute()
        gsheet_id = gsheet["id"]

    return gsheet_id

def search_spreadsheet(service, folder_name, lesson_title):
    folder_id = None
    gsheet_id = None
    folder_list = service.files().list(
        pageSize=1000,
        q="mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false",
        fields="nextPageToken, files(id, name)"
    ).execute()

    folders = folder_list.get('files', [])
    for folder in folders:
        if folder['name'] == folder_name:
            folder_id = folder['id']

            gsheet_list = service.files().list(
                pageSize=1000,
                q=f"mimeType='application/vnd.google-apps.spreadsheet' and '{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name)"
            ).execute()

            gsheets = gsheet_list.get('files', [])
            for gsheet in gsheets:
                if gsheet["name"] == lesson_title:
                    gsheet_id = gsheet['id']
                    break
            break

    return folder_id, gsheet_id

def fill_gsheet(gc, gsheet_id, sheet_rows):
    sh = gc.open_by_key(gsheet_id)
    worksheets = sh.worksheets()
    ws_name = worksheets[0].title
    ws = sh.worksheet(ws_name)
    if ws.column_count >= 11:
        ws.resize(rows=ws.row_count, cols=10)

    ws.append_rows(sheet_rows)

def trigger_web_browser(gsheet_id):
    input("\nYou may now review and make updates in the Spreadsheet. Please ensure not to do delete any rows. You can edit your cards on the Spreadsheet.\nPress Enter to open the Spreadsheet and come back here when you're done.")
    url = f"https://docs.google.com/spreadsheets/d/{gsheet_id}"
    webbrowser.open_new_tab(url)
    input("\nBefore creating Flashcards with Quizlet, please ensure:\n - You're logged in to Kakao Business website\n - You're logged in to Quizlet website\n - There are no flashcard drafts in Quizlet\n - Quizlet is in Dark Mode\n - Your web browser is in fullscreen mode\nPress Enter when you're ready to begin the process.")
    print("Preparing for quizlet generation...")

def get_quizlet_vocab(gc, gsheet_id, row_amount):
    sh = gc.open_by_key(gsheet_id)
    worksheets = sh.worksheets()
    ws_name = worksheets[0].title
    ws = sh.worksheet(ws_name)

    row_amount += 1  # list slicing opposite direction - exclusive
    quizlet_vocab_text = ""
    for row in ws.get_all_values()[:-row_amount:-1][::-1]:
        eng_expr, kor_expr = row[1], row[2]
        quizlet_vocab_text += f"{eng_expr}\t{kor_expr}\n"

    return quizlet_vocab_text

def get_random_move():
    random_movement = random.choices(VALS, weights=PROBS, k=1)[0]
    return random_movement

def get_random_speed(duration):
    random_speed = np.random.triangular(duration, duration + duration/8, duration * 1.7)
    return random_speed

def find_img_coors(image_name, scale, center=True, mandatory=True):
    confidence_var = 0.97
    while confidence_var > 0.8:
        try:
            if center:
                rec = pyautogui.locateOnScreen(f"images/{scale}/{image_name}", confidence=confidence_var)
                mid_coors = pyautogui.center(rec)
            else:
                rec = pyautogui.locateOnScreen(f"images/{scale}/{image_name}", confidence=confidence_var)
                left_mid_x, left_mid_y = rec.left, rec.top + round(rec.height/2)
                left_bot_x, left_bot_y = rec.left, rec.top + rec.height
            print(f"Confidence: {confidence_var}, ({image_name})")
            break
        except pyautogui.ImageNotFoundException:
            confidence_var -= 0.05
            print(f"Reducing confidence to {confidence_var}..")
    if confidence_var <= 0.8:
        if mandatory:
            raise Exception(f"Mandatory image (in images/{scale}/{image_name}) was not found on your screen! If it was on your screen, but it wasnt found, try to create your own image of it and put it into images/{scale}/{image_name}.")
        else:
            return 0, 0

    if center:
        return mid_coors.x, mid_coors.y
    else:
        return left_mid_x, left_mid_y, left_bot_x, left_bot_y

def get_quizlet_title(student_name, lesson_date):
    name = student_name.split()[0]
    date = lesson_date.split()
    month, day = MONTH_LABELS[date[0].lower()], date[1]
    day = ''.join(c for c in day if c.isdigit())
    title = f"{name} {month}월 {day}일"

    return title

def create_quizlet(title, vocab, cards_amount):
    while True:
        try:
            url = "https://quizlet.com"

            for m in screeninfo.get_monitors():
                if m.is_primary:
                    primary_screen = m

            resolution = f"{primary_screen.width}x{primary_screen.height}"
            print(f"Using resolution: {resolution}")

            webbrowser.open_new(url)
            time.sleep(get_random_speed(4))

            displays = os.listdir("images")
            displays = [scale for scale in os.listdir("images") if scale.startswith(resolution) or scale.startswith("your_images")]
            max_val = 0
            max_index = 0
            for i, scale in enumerate(displays):
                print(f"Trying out {scale} scale now...")
                confidence_var = 1
                while confidence_var > 0.9:
                    try:
                        pyautogui.locateOnScreen(f"images/{scale}/1plus.png", confidence=confidence_var)
                        print(f"Confidence: {confidence_var}")
                        if confidence_var > max_val:
                            max_index = i
                            max_val = confidence_var
                        break
                    except pyautogui.ImageNotFoundException:
                        confidence_var -= 0.01
                        print(f"Reducing confidence to {confidence_var}..")
                    except OSError as e:
                        print(f"The 1plus.png image wasn't found for your resolution. (folder {scale}!) ({e}).")
                        break

            scale = displays[max_index]
            print(f"Best found scale is: {scale}")

            x, y = find_img_coors("1plus.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(1), get_random_move())
            pyautogui.click()                                       # +

            x, y = find_img_coors("2set.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.2), get_random_move())
            pyautogui.click()                                       # Study set
            time.sleep(get_random_speed(2.5))                       # Text field
            pyperclip.copy(title)
            pyautogui.hotkey(CMD, 'v')
            time.sleep(get_random_speed(0.2))

            # LANGUAGES START
            pyautogui.click()                                       # Nowhere (out of text field)
            time.sleep(get_random_speed(0.3))
            left_mid_x, left_mid_y, left_bot_x, left_bot_y = find_img_coors("3wordclick.png", scale, center=False)
            pyautogui.moveTo(left_mid_x, left_mid_y, get_random_speed(0.3), get_random_move())
            pyautogui.click()                                       # Text field

            pyautogui.moveTo(left_bot_x, left_bot_y, get_random_speed(0.2), get_random_move())
            pyautogui.click()                                       # Lang Button

            pyperclip.copy("한국어")
            pyautogui.hotkey(CMD, 'v')
            time.sleep(get_random_speed(0.1))
            pyautogui.press('enter')

            time.sleep(get_random_speed(0.2))
            x, y = find_img_coors("4langselect2.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.2), get_random_move())
            pyautogui.click()                                       # Lang Button

            pyperclip.copy("영어")
            pyautogui.hotkey(CMD, 'v')
            time.sleep(get_random_speed(0.1))
            pyautogui.press('enter')
            # LANGUAGES END
            
            # START PW SETTINGS
            # wheel
            time.sleep(get_random_speed(0.5))
            x, y = find_img_coors("11wheel.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.3), get_random_move())
            pyautogui.click()

            # select
            time.sleep(get_random_speed(0.4))
            x, y = find_img_coors("22select.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.3), get_random_move())
            pyautogui.click()
            time.sleep(get_random_speed(0.2))
            pyautogui.press("down")
            time.sleep(get_random_speed(0.1))
            pyautogui.press("enter")

            # pw field
            time.sleep(get_random_speed(0.2))
            x, y = find_img_coors("33password.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.3), get_random_move())
            pyautogui.click()
            pw = 123456  # LOAD PW HERE
            time.sleep(get_random_speed(0.1))
            pyperclip.copy(pw)
            pyautogui.hotkey(CMD, 'v')
            time.sleep(get_random_speed(0.2))
            pyautogui.press("enter")

            # END PW
            time.sleep(get_random_speed(0.5))
            x, y = find_img_coors("5import.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.3), get_random_move())
            pyautogui.click()                                       # Text field
            pyperclip.copy(vocab)
            time.sleep(get_random_speed(0.3))
            pyautogui.hotkey(CMD, 'v')

            x, y = find_img_coors("6import.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(1.5), get_random_move())
            pyautogui.click()                                       # Import
            time.sleep(get_random_speed(1 + (cards_amount/30)))

            x, y = find_img_coors("7create.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.5), get_random_move())
            pyautogui.click()                                       # Create

            time.sleep(get_random_speed(3 + (cards_amount/20)))

            x, y = find_img_coors("8getlink.png", scale, mandatory=False)
            if not x:
                pyautogui.press('pagedown')
                time.sleep(get_random_speed(0.5))
                x, y = find_img_coors("8getlink.png", scale, mandatory=False)
            pyautogui.moveTo(x, y, get_random_speed(0.3), get_random_move())
            pyautogui.click()                                       # Share button

            time.sleep(get_random_speed(0.3))
            x, y = find_img_coors("9copylink.png", scale)
            pyautogui.moveTo(x, y, get_random_speed(0.2), get_random_move())
            pyautogui.click()                                       # Link copy

            time.sleep(get_random_speed(0.3))

            clipboard_content = pyperclip.paste()
            break
        except Exception as err:
            input(f"{err}.\nTo try one more time, press Enter!")
    return clipboard_content, scale

def save_msg(quizlet_vocab_text, quizlet_url_link, title):
    message_vocab_text = quizlet_vocab_text.replace("\t", " - ")
    message_text = quizlet_url_link + "\n\n" + message_vocab_text

    file_path = f"Messages/{title}.txt"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(message_text)

    print("\nMessage for students has been saved to a file in Messages directory!")

def kakao_msg_prep(title, scale):
    while True:
        try:
            url = "https://center-pf.kakao.com/_ndxoZG/chats"
            webbrowser.open_new(url)

            time.sleep(get_random_speed(3.5))
            x, y = find_img_coors("10kakaosearch.png", scale)
            pyperclip.copy(title[:2])
            pyautogui.moveTo(x, y, get_random_speed(0.7), get_random_move())
            pyautogui.click()
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')

            pyautogui.moveTo(x, y+150, get_random_speed(0.5), get_random_move())
            pyautogui.click()                                       # Text field
            time.sleep(get_random_speed(2))

            file_path = f"Messages/{title}.txt"
            with open(file_path, encoding="utf-8") as file:
                message_text = file.read()
            pyperclip.copy(message_text)

            pyautogui.hotkey('ctrl', 'v')

            time.sleep(get_random_speed(1))
            break
        except Exception as err:
            input(f"{err}.\nTo try one more time, press Enter!")


def main():
    creds, gc = get_credentials()  # web browser input prompt (email with credentials)

    document = get_document(creds)  # input prompt (gdoc URL)

    lessons = get_lessons(document)
    lesson_date, star_expr, norm_expr = get_expressions(lessons[-1])
    expression_amount = get_amount_input(lesson_date, len(star_expr), len(norm_expr))  # input prompt (amount)
    selected_expr = select_expressions(star_expr, norm_expr, expression_amount)

    translated_expr = get_translation(selected_expr)
    sheet_rows = get_rows_for_sheet(lesson_date, selected_expr, translated_expr)

    gsheet_id = get_spreadsheet_id(creds, document["title"], "English School")
    fill_gsheet(gc, gsheet_id, sheet_rows)
    trigger_web_browser(gsheet_id)  # input prompt (enter to continue)

    quizlet_vocab_text = get_quizlet_vocab(gc, gsheet_id, len(selected_expr))
    title = get_quizlet_title(document["title"], lesson_date)

    quizlet_url_link, scale = create_quizlet(title, quizlet_vocab_text, len(selected_expr))  ########
    save_msg(quizlet_vocab_text, quizlet_url_link, title)  ###########
    kakao_msg_prep(title, scale)  ###############

if __name__ == "__main__":
    main()
