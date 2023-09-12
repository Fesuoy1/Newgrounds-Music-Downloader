"""
A Script to download songs from the Newgrounds and save them as MP3, featuring:

    - Downloading
    
    - Saving
    
    - Confirmation
    
    - And many things to be added!
    
"""

import asyncio
import contextlib
import linecache
import os
import py_compile as pyc
import re
import shutil
import webbrowser

import aiofiles
import aiohttp
import msgpack
import pycached
import requests
import requests_cache
import ujson

from customtkinter import CTk as Tk
from customtkinter import CTkButton, CTkEntry, CTkLabel
from tkinter import messagebox
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from pathlib import Path

file_name = os.path.basename(__file__)
"""
Gets a file name from the current script running.

    Returns: file name
    
"""
should_rename = True  # if False, the file will not be renamed, though it is probably recommended to keep it True
"""
Determines if the file should be renamed or not.

    Returns: True if the file should be renamed, False if the file should not be renamed
"""
if file_name != "Newgrounds_Music_Downloader.py" and should_rename:
    os.rename(__file__, "Newgrounds_Music_Downloader.py")
    messagebox.showinfo("Renamed", "The file has been renamed to Newgrounds_Music_Downloader.py to prevent any issues.")
    input(f"Press Enter key to exit.\n")
pyc.compile(__file__, optimize=-1)
requests_cache.install_cache("downloader_cache", expire_after=3600)  # Cache expires after 1 hour
gui_cache = requests_cache.CachedSession("gui_cache", expire_after=3600)
pycached.SimpleMemoryCache(serializer=msgpack)
ujson.decoders = [lambda x: ujson.loads(x)]
linecache.cache = {
    "title": "Newgrounds Audio",
    "url": "https://www.newgrounds.com/audio/listen/",
    "song_id": 0,
    "title_start": 0,
    "title_end": 0,
    "response": None,
    "download_url": "https://www.newgrounds.com/audio/download/",
    "complete": False,
    "downloaded": False,
    "CTk": Tk,
    "CTkEntry": CTkEntry,
    "CTkLabel": CTkLabel,
    "CTkButton": CTkButton,
    "ujson": ujson,
    "requests": requests,
    "requests_cache": requests_cache,
    "aiofiles": aiofiles,
    "aiohttp": aiohttp,
    "msgpack": msgpack,
    "contextlib": contextlib,
    "os": os,
    "re": re,
    "webbrowser": webbrowser,
    "gui_cache": gui_cache,
    "beautifulsoup": BeautifulSoup
}
linecache.lazycache(__file__,
                    module_globals=dict(linecache=linecache.cache, pycached=pycached, py_compile=pyc, ujson=ujson,
                                        requests=requests, requests_cache=requests_cache,
                                        aiofiles=aiofiles, aiohttp=aiohttp, msgpack=msgpack, contextlib=contextlib,
                                        os=os, re=re, webbrowser=webbrowser, gui_cache=gui_cache, CTkButton=CTkButton,
                                        CTkEntry=CTkEntry, CTkLabel=CTkLabel, CTk=Tk))


def search_song():
    """
    Retrieves a song from the Newgrounds audio database using the provided song ID.
    
    Parameters:
        None
        
    Returns:
        None
        
    """
    song_id = entry.get()
    if song_id == "" or not song_id.isdigit() or not int:
        messagebox.showerror("Error", "Please enter a song ID.")
        return
    url = f"https://www.newgrounds.com/audio/listen/{song_id}"
    response = requests.get(url)
    if response.status_code == 200 and not response.text.startswith("<title>"):
        # Extract song details from the response
        response = gui_cache.get(url)
        get_title(response, song_id)
    else:
        messagebox.showerror("Error", "Invalid song ID")


def get_title(response, song_id):
    """
    Retrieves the title of a song from the Newgrounds audio database using the provided song ID.
    
    Parameters:
        response: The response from the Newgrounds audio database.
        song_id: The ID of the song.
    
    Returns:
        None
        
    Raises:
        None
    """

    # Extract song details from the response
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract the title
    if title_tag := soup.find('title'):
        title = title_tag.text.strip()
        # Show confirmation message box
        show_confirmation_window(song_id, title)


def show_confirmation_window(song_id, title):
    """
    Shows a confirmation window with the title and song ID.
    
    Parameters:
        song_id: The ID of the song.
        title: The title of the song.
        
    Returns:
        None
        
    Raises:
        None 
    """
    try:
        # replace with a messagebox when converting to any programming language, right now it has better visuals
        preview_window = Tk()
        preview_window.title("Confirmation")
        preview_window.geometry("290x170")
        preview_window.eval("tk::PlaceWindow . center")
        preview_window.pack_propagate(False)
        confirm_label = CTkLabel(preview_window, text=f"Do you want to download:\n{title}")
        confirm_label.pack(pady=5)
        yes_button = CTkButton(preview_window, text="Yes",
                               command=lambda: confirm_download(True))
        yes_button.pack(pady=5)

        no_button = CTkButton(preview_window, text="No", command=preview_window.destroy)
        no_button.pack(pady=5)
        preview_button = CTkButton(preview_window, text="Open in browser",
                                   command=open_musicurl)
        preview_button.pack(pady=5)
    except Exception as e:
        messagebox.showerror("Error", f"Error:\n {e}")


def confirm_download(confirm):
    """
    Confirm the download of a song.
    
    Parameters:
        confirm: Whether to confirm the download.
    
    Returns:
        None
        
    Raises:
        None
    """
    song_id = entry.get()
    if confirm:
        asyncio.run(download_song(song_id))


def open_musicurl():
    song_id = f"https://www.newgrounds.com/audio/listen/{entry.get()}"
    webbrowser.open_new(song_id)


async def download_song(song_id):
    """
    Downloads a song asynchronously given a song ID.
    
    Parameters:
        song_id: The ID of the song to be downloaded.
        
    Returns:
        None
        
    Raises:
        aiohttp.ClientError: If there is an error with the HTTP request.
        Aiofiles.AFSError: If there is an error while opening or writing to the file.
        FileNotFoundError: If the file is not found.
    """
    url = f"https://www.newgrounds.com/audio/download/{song_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Save the song
                await save_file(response, song_id)
            else:
                raise RequestException("Failed to download the song.")


async def save_file(response, song_id):
    file_path = Path(f"Downloaded/{song_id}.mp3")
    try:
        content = await response.content.read()

        async with aiofiles.open(file_path, mode='wb') as file:
            await file.write(content)

        if file_path.exists():
            messagebox.showinfo("Success", "Music downloaded successfully! The file is moved to the Downloaded folder.")
        else:
            messagebox.showerror("Error",
                                 "Failed to download the song. Maybe you do not have administrator privileges?")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while trying to save a music:\n {e}")
        file_path.unlink(missing_ok=True)


def clear_cache():
    """
    Clears the cache by calling the `requests_cache.clear()` function.
    Parameters:
        None
        
    Returns:
        None
        
    """
    if confirmation := messagebox.askyesno(
            "Clear Cache",
            "Are you sure you want to clear the cache? This will also delete the __pycache__ folder.",
    ):
        requests_cache.clear()
        linecache.clearcache()
        shutil.rmtree("__pycache__", ignore_errors=True)
        messagebox.showinfo("Cache Cleared", "Cache has been cleared successfully.")

    # Create the main window


window = Tk()
window.title("Newgrounds Music Downloader")
window.geometry("320x280")
window.eval("tk::PlaceWindow . center")

# Create a label and an entry for the song ID
label = CTkLabel(window, text="", font=("Arial", 14))
label.pack(pady=5, ipadx=20)
entry = CTkEntry(window, placeholder_text="Enter Newgrounds Song ID")
entry.pack(pady=5, ipadx=20)

# Create a download button
download_button = CTkButton(window, text="Download", command=search_song)
download_button.pack(pady=5, ipadx=20)

# Create a quit button
quit_button = CTkButton(window, text="Quit", command=quit)
quit_button.pack(pady=5, ipadx=20)

# Create a clear cache button
clear_cache_button = CTkButton(window, text="Clear Cache", command=clear_cache)
clear_cache_button.pack(pady=5, ipadx=20)

with contextlib.suppress(FileExistsError):
    os.mkdir("Downloaded")

window.mainloop()
