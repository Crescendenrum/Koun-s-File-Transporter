import os
import shutil
import unicodedata
import FreeSimpleGUI as sg
import textwrap
import json

def find_json_files(directory, keyword="lang", recursive=False):
    """Search for JSON files in a directory that contain a keyword in their name."""
    matching_files = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".json") and keyword in file.lower():
                    matching_files.append(os.path.join(root, file))
    else:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".json") and keyword in entry.name.lower():
                    matching_files.append(entry.path)

    return matching_files  # Returns a list of matching JSON file paths

# Example usage
folder_path = "./"  # Adjust based on your structure
json_files = find_json_files(folder_path, recursive=True)  # Enable recursive search if needed

if json_files:
    for json_file in json_files:
        print(f"Found JSON file: {json_file}")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("Languages loaded successfully:", data.keys())
        except json.JSONDecodeError:
            print(f"❌ Error decoding {json_file}: Invalid JSON format.")
else:
    print("No matching JSON file found.")


TASKS_FILE = "tasks.json"
TRANSLATIONS_FILE = "translations.json"

def normalize_string(text):
    return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII").casefold()

def move_matching_files(search_terms: list, destination_path: str, search_paths: list):
    search_terms = [normalize_string(term) for term in search_terms]
    files_moved = []

    excluded_folders = ["Windows", "Program Files", "Program Files (x86)", "System32", "AppData", "$Recycle.Bin"]

    destination_path = os.path.expanduser(destination_path)  # Expands ~ to full path
    if not os.path.exists(destination_path):

        os.makedirs(destination_path)

    for search_path in search_paths:
        for root, _, files in os.walk(search_path):
            if any(excluded in root for excluded in excluded_folders):
                continue
            for file in files:
                file_normalized = normalize_string(file)
                for term in search_terms:
                    if term in file_normalized:
                        source_file = os.path.join(root, file)
                        destination_file = os.path.join(destination_path, file)

                        # ✅ Avoid moving files to the same folder
                        if os.path.abspath(source_file) == os.path.abspath(destination_file):
                            continue

                        try:
                            shutil.move(source_file, destination_file)
                            files_moved.append(f"{source_file} -> {destination_file}")
                        except Exception as e:
                            sg.popup_error(f"Error moving {source_file}: {e}")
                        break
    return files_moved

def load_tasks():
    """Load organization rules from JSON."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_tasks(tasks):
    """Save organization rules to JSON."""
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4, ensure_ascii=False)

def load_translations():
    if os.path.exists(TRANSLATIONS_FILE):
        with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as file:
            translations = json.load(file)
            print(f"Translations loaded: {translations}")
            return translations
    return {}

def get_translation(key, lang, translations):
    if key not in translations or lang not in translations[key]:
        print(f"⚠ Missing translation for '{key}' in '{lang}'")
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("en", key))



def main(selected_language="en"):
    sg.theme("DarkBlue")

    search_paths = [
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents")
    ]


    tasks = load_tasks()
    translations = load_translations()

    languages = {
        "English": "en",
        "Türkçe": "tr",
        "Français": "fr",
        "Spanish": "es",
    }

    layout = [
        [sg.Text(get_translation("welcome", selected_language, translations), font=("Helvetica", 14), justification="center")],
        [sg.Text("🌐 Dil Seçimi:")],
        [sg.Combo(list(languages.keys()), default_value=[key for key, val in languages.items() if val == selected_language][0], key="-LANGUAGE-", enable_events=True)],
        [sg.Text(get_translation("manage_folders", selected_language, translations))],
        [sg.Listbox(values=search_paths, size=(50, 5), key="-SEARCH_PATHS-"), sg.Button(get_translation("add_folder", selected_language, translations)), sg.Button(get_translation("remove_folder", selected_language, translations))],
        [sg.Text(get_translation("manage_rules", selected_language, translations))],
        [sg.Column([[sg.Frame(task["destination"], [[sg.Listbox(task["keywords"], size=(40, 4), key=f"TASK-{i}")]])] for i, task in enumerate(tasks)], scrollable=True, size=(500, 200))],
        [sg.Button(get_translation("add_rule", selected_language, translations)), sg.Button(get_translation("remove_rule", selected_language, translations))],
        [sg.Button(get_translation("start_organizing", selected_language, translations), size=(20, 1), button_color=("white", "green"))],
        [sg.Button(get_translation("exit", selected_language, translations), size=(20, 1), button_color=("white", "red"))]
    ]

    window = sg.Window("📂 Akıllı Dosya Düzenleyici", layout, resizable=True)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, get_translation("exit", selected_language, translations)):
            break

        if event == "-LANGUAGE-":
            selected_language = languages[values["-LANGUAGE-"]]
            window.close()
            main(selected_language)  # ✅ Pass selected language to restart UI with updated translations
            return

        if event == get_translation("add_folder", selected_language, translations):
            folder = sg.popup_get_folder(get_translation("select_folder", selected_language, translations))
            if folder and folder not in search_paths:
                search_paths.append(folder)
                window["-SEARCH_PATHS-"].update(search_paths)

        if event == get_translation("remove_folder", selected_language, translations):
            selected = values["-SEARCH_PATHS-"]
            if selected:
                search_paths.remove(selected[0])
                window["-SEARCH_PATHS-"].update(search_paths)

        if event == get_translation("add_rule", selected_language, translations):
            keyword = sg.popup_get_text(get_translation("enter_keywords", selected_language, translations))
            destination = sg.popup_get_folder(get_translation("select_destination", selected_language, translations))
            if keyword and destination:
                keywords_list = [kw.strip() for kw in keyword.split(",")]
                tasks.append({"keywords": keywords_list, "destination": destination})
                save_tasks(tasks)  # ✅ Save immediately
                window.close()
                main()  # Restart UI to reflect changes
                return

        if event == get_translation("remove_rule", selected_language, translations):
            selected_task_index = None

            # Find which task's Listbox has a selection
            for i, task in enumerate(tasks):
                if values.get(f"TASK-{i}"):  # Check if something is selected in this task's Listbox
                    selected_task_index = i
                    break

            if selected_task_index is not None:
                confirm = sg.popup_yes_no(get_translation("confirm_removal", selected_language, translations), title=get_translation("confirmation", selected_language, translations))
                if confirm == "Yes":
                    del tasks[selected_task_index]  # Remove the selected task
                    save_tasks(tasks)  # Save the updated tasks list
                    window.close()
                    main()  # Restart UI to reflect changes
            else:
                sg.popup_error(get_translation("no_rules_selected", selected_language, translations))

        if event == get_translation("start_organizing", selected_language, translations):
            if not search_paths:
                sg.popup_error(get_translation("add_scan_folder", selected_language, translations))
                continue
            if not tasks:
                sg.popup_error(get_translation("add_org_rule", selected_language, translations))
                continue
            
            def shorten_text(text, length=25):
                """Shortens long text while keeping it readable."""
                return textwrap.shorten(text, width=length, placeholder="...")

            moved_files_summary = ""
            for task in tasks:
                moved_files = move_matching_files(task["keywords"], task["destination"], search_paths)
                if moved_files:
                    for move in moved_files:
                        try:
                            src, dest = move.rsplit(" -> ", 1)  # ✅ Ensure only last `->` is split
                            filename = shorten_text(os.path.basename(src), 30)  # Shorten filename
                            short_dest = shorten_text(dest.replace("~\\Downloads", "")
                                                          .replace("~\\Documents\\", "")
                                                          .replace("~\\Desktop\\", ""), 50)  # Shorten folder path
                            
                            moved_files_summary += f'"{filename}" -> "{short_dest}"\n'
                        except ValueError:
                            continue  # Ignore malformed logs

            if moved_files_summary:
                sg.popup(get_translation("files_moved", selected_language, translations), moved_files_summary)
            else:
                sg.popup(get_translation("no_matching_files", selected_language, translations))

    window.close()

if __name__ == "__main__":
    main()
