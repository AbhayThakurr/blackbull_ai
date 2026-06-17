import urllib.parse
import webbrowser

from langchain.tools import tool


@tool
def search_web_in_browser(query: str, browser_name: str = None) -> str:
    """
    Searches Google in a browser.
    Use this tool when the user asks to search the web (e.g. 'search for netflix').
    If the user explicitly specifies a browser (e.g. 'firefox', 'chrome', 'brave'), pass it in browser_name.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"

        if browser_name:
            # Map common names to linux browser commands
            b_map = {"firefox": "firefox", "chrome": "google-chrome", "brave": "brave"}
            target = b_map.get(browser_name.lower(), browser_name.lower())
            try:
                webbrowser.get(target).open(url)
                return f"Successfully opened {browser_name} and searched Google for: '{query}'"
            except webbrowser.Error:
                # Fallback to default if specific browser is not found
                webbrowser.open(url)
                return f"Opened default browser (could not find {browser_name}) and searched: '{query}'"
        else:
            webbrowser.open(url)
            return f"Successfully opened default browser and searched Google for: '{query}'"
    except Exception as e:
        return f"Failed to search web in browser: {str(e)}"


@tool
def open_url_in_browser(url: str, browser_name: str = None) -> str:
    """
    Opens a specific website URL in a browser.
    Provide the full URL (e.g. 'https://www.youtube.com').
    If the user just says a site name like 'YouTube', 'Netflix', or 'Google',
    convert it to the full URL (e.g. 'youtube.com') before passing it in.
    If the user explicitly specifies a browser (e.g. 'firefox', 'chrome', 'brave'), pass it in browser_name.
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        if browser_name:
            b_map = {"firefox": "firefox", "chrome": "google-chrome", "brave": "brave"}
            target = b_map.get(browser_name.lower(), browser_name.lower())
            try:
                webbrowser.get(target).open(url)
                return f"Successfully opened {browser_name} and navigated to: {url}"
            except webbrowser.Error:
                webbrowser.open(url)
                return f"Opened default browser (could not find {browser_name}) and navigated to: {url}"
        else:
            webbrowser.open(url)
            return f"Successfully opened default browser and navigated to: {url}"
    except Exception as e:
        return f"Failed to open URL: {str(e)}"


@tool
def search_youtube(query: str, browser_name: str = None) -> str:
    """
    Opens YouTube search results for a query.
    Use this when the user wants to *search* for videos on YouTube
    (e.g. 'search YouTube for funny cats', 'find TMKOC episodes on YouTube').
    If the user wants to *play* the first/most relevant video directly,
    use `play_youtube_video` instead.
    """
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"

        if browser_name:
            b_map = {"firefox": "firefox", "chrome": "google-chrome", "brave": "brave"}
            target = b_map.get(browser_name.lower(), browser_name.lower())
            try:
                webbrowser.get(target).open(url)
                return (
                    f"Opened YouTube in {browser_name}, showing results for: '{query}'"
                )
            except webbrowser.Error:
                webbrowser.open(url)
                return f"Opened YouTube, showing results for: '{query}'"
        else:
            webbrowser.open(url)
            return f"Opened YouTube, showing results for: '{query}'"
    except Exception as e:
        return f"Failed to search YouTube: {str(e)}"


@tool
def play_youtube_video(query: str, browser_name: str = None) -> str:
    """
    Plays the most relevant YouTube video for a search query by opening it directly.
    Use this when the user wants to *play* a specific video, song, show,
    or clip on YouTube (e.g. 'play TMKOC on YouTube', 'play Despacito',
    'play the latest MrBeast video').
    This opens the first/top video result — no need to search and click.
    """
    try:
        # Use Google's "I'm Feeling Lucky" with site:youtube.com to go
        # directly to the top YouTube video for the query.
        encoded = urllib.parse.quote(f"site:youtube.com {query}")
        url = f"https://www.google.com/search?q={encoded}&btnI="

        if browser_name:
            b_map = {"firefox": "firefox", "chrome": "google-chrome", "brave": "brave"}
            target = b_map.get(browser_name.lower(), browser_name.lower())
            try:
                webbrowser.get(target).open(url)
                return f"Playing top YouTube result for '{query}' in {browser_name}"
            except webbrowser.Error:
                webbrowser.open(url)
                return f"Playing top YouTube result for '{query}' in default browser"
        else:
            webbrowser.open(url)
            return f"Playing top YouTube result for '{query}'"
    except Exception as e:
        return f"Failed to play YouTube video: {str(e)}"
