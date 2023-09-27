"""
A Script to download songs from the Newgrounds and save them as MP3, featuring:

    - Downloading from Newgrounds

    - Downloading from YouTube
    
    - And some things to be added soon!
    
"""
from tkinter import messagebox

try:
    import asyncio
    import contextlib
    import linecache
    import os
    import py_compile as pyc
    import re
    import shutil
    import threading
    import webbrowser
    from pathlib import Path
    import diskcache

    import aiofiles
    import aiohttp
    import customtkinter as ctk
    import httpx
    import httpx_cache
    import msgpack
    import pycached
    import ujson
    import wget
    from bs4 import BeautifulSoup
    from customtkinter import CTk as Tk
    from customtkinter import CTkButton, CTkEntry, CTkLabel
    from pytube import YouTube
    import warnings
    from functools import wraps
except ModuleNotFoundError as m:
    messagebox.showerror("Error",
                         f"1 or more modules are missing. Please install them using "
                         f"'pip install <module name>'.\nError: {m}")
except ImportError:
    messagebox.showwarning("Warning", "An Import Error occurred. Please try again.")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

bools = (True, False) # False is 1. and True is 0

debugging = bools[1]

if debugging:
    __import__("tracemalloc").start()
    print("Debugging mode is on.")

client = httpx_cache.Client(cache=httpx_cache.FileCache(cache_dir="./cache"), timeout=30)

file_name = os.path.basename(__file__)
"""
Gets a file name from the current script running.

    Returns: file name
    
"""
file_path = Path("Downloaded/")

URL = "https://www.newgrounds.com/audio/listen/"
DOWNLOAD_URL = "https://www.newgrounds.com/audio/download/"

should_rename = bools[0]  # if False (1), the file will not be renamed, though it is probably recommended to keep it True (0)
"""
Determines if the file should be renamed or not.

    Returns: True if the file should be renamed, False if the file should not be renamed
"""
if file_name != "Newgrounds_Music_Downloader.py" and should_rename:
    os.rename(__file__, "Newgrounds_Music_Downloader.py")
    messagebox.showinfo("Renamed",
                        "The file has been renamed to Newgrounds_Music_Downloader.py to prevent any issues.")
    input(f"Press Enter key to exit.\n")
pyc.compile(__file__, optimize=-1)
pycached.SimpleMemoryCache(serializer=msgpack)
ujson.decoders = [lambda x: ujson.loads(x)]
linecache.cache = {
    "title": "Newgrounds Audio",
    "url": URL,
    "song_id": 0,
    "title_start": 0,
    "title_end": 0,
    "response": None,
    "download_url": DOWNLOAD_URL,
    "complete": bools[1],
    "downloaded": bools[1],
    "CTk": Tk,
    "CTkEntry": CTkEntry,
    "CTkLabel": CTkLabel,
    "CTkButton": CTkButton,
    "ujson": ujson,
    "aiofiles": aiofiles,
    "aiohttp": aiohttp,
    "msgpack": msgpack,
    "contextlib": contextlib,
    "os": os,
    "re": re,
    "webbrowser": webbrowser,
    "beautifulsoup": BeautifulSoup
}
linecache.lazycache(__file__,
                    module_globals=dict(linecache=linecache.cache, pycached=pycached, py_compile=pyc, ujson=ujson,
                                        aiofiles=aiofiles, aiohttp=aiohttp, msgpack=msgpack, contextlib=contextlib,
                                        os=os, re=re, webbrowser=webbrowser,
                                        CTkButton=CTkButton, beautifulsoup=BeautifulSoup,
                                        CTkEntry=CTkEntry, CTkLabel=CTkLabel, CTk=Tk))

cache = diskcache.Cache()


def deprecated(func):
    if isinstance(func, property):
        return deprecated_property(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn("This function is deprecated", category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return wrapper


def deprecated_property(prop):
    @property
    def wrapper(*args, **kwargs):
        warnings.warn("This property is deprecated", category=DeprecationWarning, stacklevel=2)
        return prop.fget(*args, **kwargs)

    return wrapper


def handle_error(e: Exception | str):
    """
    Handle an error by displaying an error message and giving the user the option to report the error.

    Parameters:
        e (Exception): The error that occurred.

    Returns:
        None
    """
    error_message = f"An error occurred:\n\n {e}\n\n Do you want to report this error? (Requires a GitHub token)"
    if messagebox.askyesno("Error", error_message):
        show_token_window(e)


def get_song():
    """
    Retrieves a song from the Newgrounds audio database using the provided song ID.

    Parameters:
        None

    Returns:
        None

    """
    try:
        song_id = song_entry.get()
        print(f"Song ID: {song_id}")
        if song_id == "" or not song_id.isdigit() or not int:
            messagebox.showerror("Error", "Please enter a song ID.")
            song_entry.delete(0, ctk.END)
            print(f"{song_id} is Invalid")
            return
        url = f"{URL}{song_id}"
        response = client.get(url)
        if response.status_code == 200 and not response.text.startswith("<title>"):
            # Extract song details from the response
            get_title(response)
            if debugging:
                print(f"URL: {url}")
                print(f"Download URL: {DOWNLOAD_URL}{song_id}")
                print(f"{song_id} is Valid")
        else:
            messagebox.showerror("Error", f"Invalid song ID: {song_id}")
            song_entry.delete(0, ctk.END)
            print(f"{song_id} is Invalid")
    except Exception as e:
        handle_error(e)


def get_title(response: httpx.Response):
    """
    Retrieves the title of a song from the Newgrounds audio database using the provided song ID.

    Parameters:
        response: The response from the Newgrounds audio database.

    Returns:
        None
    """

    # Extract song details from the response
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract the title
    try:
        if title_tag := soup.find('title'):
            title = title_tag.text.strip()
            show_confirmation_window(title)
    except AttributeError:
        show_confirmation_window("Unknown")


def show_token_window(error: Exception | str):
    token_window = Tk()
    token_window.title("Token")
    token_window.geometry("290x170")
    token_window.eval("tk::PlaceWindow . center")
    token_window.propagate(True)
    token_label = CTkLabel(
        token_window,
        text="Paste your GitHub token here:"
    )
    token_label.pack(pady=2)
    token_entry = CTkEntry(token_window)
    token_entry.pack(pady=3)
    cancel_button = CTkButton(
        token_window,
        text="Cancel",
        command=token_window.destroy
    )
    cancel_button.pack(pady=5)
    submit_button = CTkButton(token_window, text="Submit",
                              command=lambda: generate_error_report("Fesuoy1", "Newgrounds-Music-Downloader", error,
                                                                    token_entry))
    submit_button.pack(pady=5)

    token_window.mainloop()


def did_send_error_report(response: httpx.Response):
    if response.status_code == 201:
        messagebox.showinfo(
            "Success",
            "Your report was successfully sent."
        )


def generate_error_report(repo_owner: str, repo_name: str, error: Exception | str, token: CTkEntry | str):
    """
    Generates an error report for the GitHub repository.

    Parameters:
        repo_owner (str): The owner of the GitHub repository.
        repo_name (str): The name of the GitHub repository.
        error (Exception or str): The error that occurred.
        token (CTkEntry or str): The GitHub token.

    Returns:
        None

    Raises:
        None
    """
    url = generate_url(repo_owner, repo_name)
    headers = generate_headers(token)
    data = generate_data(repo_name, error)

    try:
        if confirm_report(data):
            response = client.post(url, headers=headers, json=data)
            did_send_error_report(response)
            response.raise_for_status()

    except httpx.HTTPStatusError:
        messagebox.showerror(
            "Error",
            "An error occurred while trying to send an error report to the GitHub repository. Did you enter a valid "
            "token?"
        )


def generate_url(repo_owner: str, repo_name: str) -> str:
    return f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"


def generate_headers(token: CTkEntry | str) -> dict:
    if token != str:
        return {
            "Authorization": f"Bearer {token.get()}",
            "Accept": "application/vnd.github.v3+json",
        }

    personal_token = os.getenv(token)
    return {
        "Authorization": f"Bearer {personal_token}",
        "Accept": "application/vnd.github.v3+json",
    }


def generate_data(repo_name: str, error: str) -> dict:
    return {
        "title": f"Error in {repo_name}",
        "body": f"An error occurred in the repository {repo_name}:\n\n{error}"
    }


def confirm_report(data: dict) -> bool:
    return messagebox.askyesno(
        "Confirmation",
        f"Your report will look like this:\n\n{data.get('title')}\n{data.get('body')}\n\nDo you want to send it?",
    )


def show_confirmation_window(title):
    """
    Shows a confirmation window with the title and song ID.

    Parameters:
        title: The title of the song.

    Returns:
        None
    """
    try:
        # Create and configure the preview window
        preview_window = create_preview_window()

        # Add the confirmation label to the preview window
        add_confirm_label(preview_window, title)

        # Add the yes button to the preview window
        add_yes_button(preview_window)

        # Add the no button to the preview window
        add_no_button(preview_window)

        # Add the preview button to the preview window
        add_preview_button(preview_window)

        # Add the test error report button to the preview window
        if debugging:
            add_test_error_report_button(preview_window)

    except Exception as e:
        if messagebox.askyesno("Error",
                               f"Error:\n\n {e}\n\n Do you want to report this error? (Requires a GitHub token)"):
            show_token_window(e)


def create_preview_window():
    """
    Creates and configures the preview window.

    Returns:
        The preview window.
    """
    preview_window = Tk()
    preview_window.title("Confirmation")
    preview_window.geometry("290x160")
    preview_window.eval("tk::PlaceWindow . center")
    preview_window.pack_propagate(False)
    return preview_window


def add_confirm_label(preview_window, title):
    """
    Adds the confirmation label to the preview window.

    Parameters:
        preview_window: The preview window.
        title: The title of the song.

    Returns:
        The confirmation label.
    """
    confirm_label = CTkLabel(preview_window, text=f"Do you want to download:\n{title}")
    confirm_label.pack(pady=5)
    return confirm_label


def add_yes_button(preview_window):
    """
    Adds the yes button to the preview window.

    Parameters:
        preview_window: The preview window.

    Returns:
        The yes button.
    """
    global yes_button

    yes_button = CTkButton(preview_window, text="Yes",
                           command=lambda: on_yes_click())
    yes_button.pack(pady=5)
    return yes_button


def add_no_button(preview_window):
    """
    Adds the no button to the preview window.

    Parameters:
        preview_window: The preview window.

    Returns:
        The no button.
    """
    no_button = CTkButton(preview_window, text="No", command=preview_window.destroy)
    no_button.pack(pady=5)
    return no_button


def add_preview_button(preview_window):
    """
    Adds the preview button to the preview window.

    Parameters:
        preview_window: The preview window.

    Returns:
        The preview button.
    """
    preview_button = CTkButton(preview_window, text="Open in browser",
                               command=open_musicurl)
    preview_button.pack(pady=5)
    return preview_button


def add_test_error_report_button(preview_window):
    """
    Adds the test error report button to the preview window.

    Parameters:
        preview_window: The preview window.

    Returns:
        The test error report button.
    """
    test_error_report = CTkButton(preview_window, text="Test Error Report",
                                  command=lambda: show_token_window("An Example Error"))
    test_error_report.pack(pady=5)
    return test_error_report


def on_yes_click():
    """
    Handles the yes button click.

    Parameters:
        None

    Returns:
        None
    """
    yes_button.configure(state="disabled", text="Downloading...")
    song_id = song_entry.get()
    threading.Thread(target=asyncio.run, args=(download_song(song_id),)).start()


def open_musicurl():
    song_id = f"{URL}{song_entry.get()}"
    webbrowser.open_new(song_id)


async def download_song(song_id):
    song_path = f"Downloaded/{song_id}.mp3"

    cache.set("song_path", song_path)
    url = f"{DOWNLOAD_URL}{song_id}"
    try:
        await asyncio.to_thread(wget.download, url, out=cache.get("song_path"), bar=None)
        if os.path.exists(cache.get("song_path")):
            messagebox.showinfo("Success",
                                "Music downloaded successfully! The file is moved to the Downloaded folder.")
        else:
            messagebox.showerror("Error",
                                 "Failed to download the song. Maybe you do not have administrator privileges?")
    except Exception as e:
        handle_error(e)
        if os.path.exists(cache.get("song_path")):
            os.remove(cache.get("song_path"))


def clear_cache():
    """
    Clears the cache.

    Parameters:
        None

    Returns:
        None

    """
    if messagebox.askyesno(
            "Clear Cache",
            "Are you sure you want to clear the cache? This will also delete the __pycache__ folder.",
    ):
        linecache.clearcache()
        cache.clear()
        shutil.rmtree("__pycache__", ignore_errors=True)
        messagebox.showinfo("Cache Cleared", "Cache has been cleared successfully.")


@deprecated
def yt_window():
    global perc_label, progress, yt_entry
    try:
        yt_root = Tk()
        yt_root.title("YouTube Audio Downloader")
        yt_root.geometry("450x250")
        yt_root.eval("tk::PlaceWindow . center")
        yt_root.propagate(True)

        spaces = CTkLabel(yt_root, text="")
        spaces.pack(pady=3, ipadx=20)

        yt_entry = CTkEntry(yt_root, placeholder_text="Paste YouTube URL")
        yt_entry.pack(pady=5, ipadx=20)

        yt_download = CTkButton(yt_root, text="Download Audio", command=lambda: yt_url_confirm(yt_entry))
        yt_download.pack(pady=3, ipadx=20)

        cancel = CTkButton(yt_root, text="Close", command=yt_root.destroy)
        cancel.pack(pady=3, ipadx=20)

        perc_label = CTkLabel(yt_root, text="0%")
        perc_label.pack(pady=3, ipadx=20)

        progress = ctk.CTkProgressBar(yt_root, width=400)
        progress.set(0)
        progress.pack(pady=3, ipadx=20)

        messagebox.showwarning("Deprecated", "This option is deprecated as of v1.2.0 "
                                             "and will most likely be removed in future versions, "
                                             "you may encounter errors using this. but most unlikely would get fixed.")
    except Exception as e:
        handle_error(e)


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    poc = bytes_downloaded / total_size * 100
    per = str(int(poc))
    perc_label.configure(text=f"{per}%")
    perc_label.update()
    progress.set(float(poc) / 100)


def on_complete(stream, file_path):
    messagebox.showinfo("Success", "Audio Downloaded Successfully! the file is saved at the Downloaded folder.")
    yt_entry.delete(0, ctk.END)


def vid_on_complete(stream, file_path):
    messagebox.showinfo("Success", "Video Downloaded Successfully! the file is saved at the Downloaded folder.")
    yt_entry.delete(0, ctk.END)


def res_return(res: str) -> str:
    vid_obj = YouTube(link, on_progress_callback=on_progress, on_complete_callback=vid_on_complete)
    if video_obj := vid_obj.streams.get_by_resolution(res):
        video_path = "Downloaded/"
        video_obj.download(video_path, max_retries=3)
    return res


def resolution_window() -> None:
    try:
        reswindow = create_resolution_window()
        add_resolution_buttons(reswindow)
        reswindow.mainloop()
    except Exception as e:
        handle_error(e)


def create_resolution_window() -> Tk:
    reswindow = Tk()
    reswindow.title("Resolution")
    reswindow.geometry("200x260")
    reswindow.eval("tk::PlaceWindow . center")
    reswindow.propagate(True)
    return reswindow


def add_resolution_buttons(reswindow: Tk) -> None:
    resolutions = {"144p": res_return, "240p": res_return, "360p": res_return, "480p": res_return, "720p": res_return,
                   "1080p": res_return}
    for resolution, action in resolutions.items():
        button = CTkButton(reswindow, text=resolution,
                           command=lambda res=resolution: threading.Thread(target=action, args=(res,)).start())
        button.pack(pady=3, ipadx=25)


def yt_url_confirm(yt_entry: CTkEntry) -> None:
    try:
        global link
        link = yt_entry.get()
        if link.startswith("https://www.youtube.com/watch?v=") or link.startswith(
                "https://youtu.be/") or link.startswith("https://youtube.com/watch?v="):
            yt_obj = YouTube(link, on_progress_callback=on_progress, on_complete_callback=on_complete)
            if messagebox.askyesno("Confirm", f"You are about to download: {yt_obj.title}"):
                if audio := yt_obj.streams.get_audio_only("mp3"):
                    audio.download("Downloaded/", max_retries=3)
                elif messagebox.askyesno("Warning",
                                         "No audio stream available. Do you want to download the video instead?",
                                         icon="warning"):
                    resolution_window()
                else:
                    messagebox.showerror("Error", "No video stream available")
        else:
            messagebox.showerror("Error", "Invalid YouTube URL")
    except TypeError:
        handle_error("(Technical) Youtube object is None. "
                     "This is Unnecessary to report as there could be a chance i could deprecate this feature.")
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    window = Tk()
    window.title("Newgrounds Music Downloader")
    window.geometry("280x240")
    window.eval("tk::PlaceWindow . center")

    # Create a label and an entry for the song ID
    label = CTkLabel(window, text="")
    label.pack()
    song_entry = CTkEntry(window, placeholder_text="Enter Newgrounds Song ID")
    song_entry.pack(pady=5, ipadx=20)

    # Create a download button
    download_button = CTkButton(window, text="Download", command=get_song)
    download_button.pack(pady=5, ipadx=20)

    # Create a YouTube window button
    yt_button = CTkButton(window, text="Download from YouTube", command=yt_window)
    yt_button.pack(pady=5, ipadx=12)

    # Create a quit button
    quit_button = CTkButton(window, text="Quit", command=exit)
    quit_button.pack(pady=5, ipadx=20)

    # Create a clear cache button
    clear_cache_button = CTkButton(window, text="Clear Cache", command=clear_cache)
    clear_cache_button.pack(pady=5, ipadx=20)

    if not os.path.exists("Downloaded"):
        os.mkdir("Downloaded")
    # Start the main GUI event loop
    window.mainloop()
