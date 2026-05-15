"""
HARRY POTTER GRIMOIRE APP
"""

# standard GUI toolkit for building all Grimoire interface screens
import tkinter as tk
# themed widgets for modern UI controls (dropdowns, scrollbars)
from tkinter import ttk, messagebox
# file system operations to locate assets in project folders
import os
# library for loading, resizing and converting image formats
from PIL import Image, ImageTk
# HTTP requests to fetch character/spell data from PotterDB API
import requests
# in-memory binary stream for image processing
import io
# concurrent operations to prevent UI freezing during searches
import threading
# sound effects and background music management
import pygame


# API endpoints for different Harry Potter categories
API_URL = "https://api.potterdb.com/v1/characters"
SPELL_API_URL = "https://api.potterdb.com/v1/spells"
POTION_API_URL = "https://api.potterdb.com/v1/potions"
MOVIE_API_URL = "https://api.potterdb.com/v1/movies"
BOOK_API_URL = "https://api.potterdb.com/v1/books"

# global cache to store preloaded GIF frames (reduces memory usage)
GIF_CACHE = {}


class AnimatedGIF:
    """Loads and animates GIF backgrounds with frame caching"""
    
    def __init__(self, parent, gif_path, x, y, default_delay=80):
        # parent widget where GIF will be displayed
        self.parent = parent
        # tracks current animation frame
        self.frame_index = 0
        # controls animation loop state
        self.running = True
        
        # Check cache first to avoid reloading same GIF
        if gif_path not in GIF_CACHE:
            # Load and cache GIF frames
            frames = []
            delays = []
            gif = Image.open(gif_path)
            try:
                while True:
                    # extract individual frame
                    frame = gif.copy().convert("RGBA")
                    frames.append(ImageTk.PhotoImage(frame))
                    # preserve original timing or use default
                    delay = gif.info.get("duration", default_delay)
                    delays.append(delay)
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass  # end of GIF sequence
            # store in global cache for reuse
            GIF_CACHE[gif_path] = (frames, delays)
        
        # retrieve frames from cache
        self.frames, self.delays = GIF_CACHE[gif_path]
        
        # create label to hold animated frames
        self.label = tk.Label(parent, bg="#000000", bd=0)
        # position GIF at specified coordinates
        self.label.place(x=x, y=y)
        
        # start animation loop
        self.animate()

    def animate(self):
        """Continuous animation loop for GIF playback"""
        if not self.running or not self.frames:
            return

        # update label with current frame
        self.label.configure(image=self.frames[self.frame_index])

        # get delay for current frame
        delay = self.delays[self.frame_index]
        # cycle to next frame (loop back to 0 at end)
        self.frame_index = (self.frame_index + 1) % len(self.frames)

        # schedule next frame update
        self.parent.after(delay, self.animate)

    def stop(self):
        """Safely stops animation and cleans up resources"""
        self.running = False
        if self.label.winfo_exists():
            self.label.destroy()

class GrimoireApp:
    """Main controller class for the Harry Potter Grimoire application"""
    
    def __init__(self, root):
        # main application window reference
        self.root = root
        self.root.title("Harry Potter Grimoire")  # window title
        self.root.geometry("1000x650")  # fixed window dimensions for layout stability
        self.root.config(bg="#0B0C10")  # dark theme background color
        self.root.resizable(False, False)  # prevents unwanted window resizing
        self.current_page = None  # tracks active page/screen

        # base directory for asset loading
        self.base_dir = os.path.dirname(__file__)

        # application icon setup
        icon_path = os.path.join(self.base_dir, "Assets", "icons", "app_icon.ico")
        self.root.iconbitmap(icon_path)
        
        # Start with title page on launch
        self.show_title_page()

        # initialize pygame mixer for audio management
        pygame.mixer.init()

        # define paths for audio assets
        self.music_dir = os.path.join(self.base_dir, "assets", "music")
        self.sound_dir = os.path.join(self.base_dir, "assets", "sounds")

        # load and play background music continuously
        pygame.mixer.music.load(
            os.path.join(self.music_dir, "John Williams - Harry Potter.mp3")
        )
        pygame.mixer.music.set_volume(0.25)  # balanced volume level
        pygame.mixer.music.play(-1)  # infinite loop background music

        # load UI click sound effect
        self.click_sound = pygame.mixer.Sound(
            os.path.join(self.sound_dir, "click.mp3")
        )
        self.click_sound.set_volume(0.6)  # adjust click sound volume

    def click(self, action=None):
        """Plays click sound then executes button action with slight delay"""
        self.click_sound.play()  # auditory feedback for user interaction
        if action:
            self.root.after(80, action)  # schedule action after sound plays

    def clear_screen(self):
        """Removes all widgets and stops animations from current page"""
        # Stop current page animations safely
        if self.current_page and hasattr(self.current_page, "destroy"):
            self.current_page.destroy()

        # Destroy all widgets from root window
        for widget in self.root.winfo_children():
            widget.destroy()

    #PAGE NAVIGATION METHODS
    def show_title_page(self):
        """Page 1: Title/Intro screen with heading and explore button"""
        self.clear_screen()
        self.current_page = TitlePage(self.root, self)
    
    def show_map_intro(self):
        """Page 2A: Map description and lore information page"""
        self.clear_screen()
        self.current_page = MapIntroPage(self.root, self)

    def show_map_select(self):
        """Page 2B: Interactive map with location pin navigation buttons"""
        self.clear_screen()
        self.current_page = MapSelectPage(self.root, self)
 
    def show_character_archives(self):
        """Page 3A: Character search interface with card display"""
        self.clear_screen()
        self.current_page = CharacterArchives(self.root, self)

    def show_character_detail(self, char):
        """Page 3B: Detailed character view with image and aligned details"""
        self.clear_screen()
        self.current_page = CharacterDetailPage(self.root, self, char)

    def show_spell_library(self):
        """Page 4A: Spell search and card browsing interface"""
        self.clear_screen()
        self.current_page = SpellArchives(self.root, self)

    def show_spell_detail(self, spell):
        """Page 4B: Detailed spell information view"""
        self.clear_screen()
        self.current_page = SpellDetailPage(self.root, self, spell)

    def show_potion_library(self):
        """Page 5A: Potion search and card browsing interface"""
        self.clear_screen()
        self.current_page = PotionArchives(self.root, self)

    def show_potion_detail(self, potion):
        """Page 5B: Detailed potion information view"""
        self.clear_screen()
        self.current_page = PotionDetailPage(self.root, self, potion)

    def show_movie_archives(self):
        """Page 6A: Movie catalog with scrollable card display"""
        self.clear_screen()
        self.current_page = MovieArchives(self.root, self)

    def show_movie_detail(self, movie):
        """Page 6B: Detailed movie information view"""
        self.clear_screen()
        self.current_page = MovieDetailPage(self.root, self, movie)

    def show_book_archives(self):
        """Page 7A: Book catalog with scrollable card display"""
        self.clear_screen()
        self.current_page = BookArchives(self.root, self)

    def show_book_detail(self, book, mode):
        """Page 7B: Book detail view with toggle between details and chapters"""
        self.clear_screen()
        self.current_page = BookDetailPage(self.root, self, book, mode)


class TitlePage:
    """Page 1: Title screen with animated background and navigation buttons"""
    
    def __init__(self, parent, app_ref):
        # parent window reference for widget placement
        self.parent = parent
        # reference to main app controller for navigation
        self.app = app_ref
        # base directory for asset loading
        self.base_dir = self.app.base_dir

        # GIF BACKGROUND setup with animation
        gif_path = os.path.join(
            self.base_dir, "assets", "backgrounds", "title_bg.gif"
        )

        # initialize animated background GIF
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0,
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,   # full width relative to parent
            relheight=1   # full height relative to parent
        )

        # ASSET PATHS for button images
        enter_btn_path = os.path.join(self.base_dir, "assets", "buttons", "enter_map.png")
        info_btn_path = os.path.join(self.base_dir, "assets", "buttons", "wizarding_world.png")

        # BUTTON IMAGES loaded and resized
        self.enter_img = tk.PhotoImage(file=enter_btn_path).subsample(3, 3)  # 33% original size
        self.info_img = tk.PhotoImage(file=info_btn_path).subsample(2, 2)    # 50% original size

        # ENTER MAP BUTTON (main navigation)
        enter_btn = tk.Button(
            parent,
            image=self.enter_img,
            bd=0,  # no border
            highlightthickness=0,  # no focus highlight
            bg="#000000",  # black background to match theme
            activebackground="#000000",  # same color when clicked
            command=lambda: app.click(app.show_map_intro)  # navigate to map intro
        )
        enter_btn.place(relx=1.0, x=-33, y=39, anchor="ne")  # top-right corner positioning

        # WIZARDING WORLD INFO BUTTON (additional information)
        info_btn = tk.Button(
            parent,
            image=self.info_img,
            bd=0,
            highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: self.app.click(self.show_about_popup)  # open info popup
        )
        info_btn.place(x=19, y=14)  # absolute top-left positioning

    def show_about_popup(self):
        """Opens informational window about the Wizarding World with background"""
        
        # create popup window
        about_win = tk.Toplevel(self.parent)
        about_win.title("Wizarding World")
        about_win.geometry("600x400")  # fixed size popup
        about_win.resizable(False, False)  # prevent resizing
        about_win.transient(self.parent)  # associate with main window
        about_win.grab_set()  # make popup modal (blocks main window)

        # set popup icon
        icon_path = os.path.join(self.base_dir, "Assets", "icons", "app_icon.ico")
        about_win.iconbitmap(icon_path)

        # GIF BACKGROUND PATH for popup
        gif_path = os.path.join(
            self.base_dir, "assets", "backgrounds", "about_bg.gif"
        )

        # Animated GIF Background for popup window
        about_win.bg_gif = AnimatedGIF(
            parent=about_win,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch to fill entire popup window
        about_win.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        # Proper cleanup when popup closes
        def on_close():
            about_win.bg_gif.stop()  # stop animation
            about_win.destroy()  # destroy window

        about_win.protocol("WM_DELETE_WINDOW", on_close)  # set close handler

    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


class MapIntroPage:
    """Page 2A: Map introduction screen with lore description and navigation"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref

        # determine base directory for asset loading
        base_dir = os.path.dirname(__file__)

        # paths for background and navigation button images
        bg_path = os.path.join(base_dir, "assets", "backgrounds", "map_intro_bg.png")
        back_btn_path = os.path.join(base_dir, "assets", "buttons", "back.png")
        cont_btn_path = os.path.join(base_dir, "assets", "buttons", "continue.png")

        # BACKGROUND setup (static PNG image)
        self.bg_img = tk.PhotoImage(file=bg_path)
        self.bg_label = tk.Label(parent, image=self.bg_img)
        self.bg_label.image = self.bg_img  # keep reference to prevent garbage collection        
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # full screen coverage

        # BUTTON IMAGES loaded and resized
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(4, 4)   # 25% original size
        self.cont_img = tk.PhotoImage(file=cont_btn_path).subsample(4, 4)  # 25% original size

        # BACK BUTTON (return to title screen)
        self.back_btn = tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            highlightthickness=0,  # no focus highlight
            bg="#000000",  # black background
            activebackground="#e9cca0",  # parchment color when active
            command=lambda: app.click(app.show_title_page)  # navigate back
        )
        self.back_btn.image = self.back_img  # maintain image reference        
        self.back_btn.place(x=30, y=596)  # positioned near bottom-left

        # CONTINUE BUTTON (proceed to interactive map)
        self.cont_btn = tk.Button(
            parent,
            image=self.cont_img,
            bd=0,
            highlightthickness=0,
            bg="#000000",
            activebackground="#e9cca0",  # parchment color when active
            command=lambda: app.click(app.show_map_select)  # navigate forward
        )
        self.cont_btn.image = self.cont_img  # maintain image reference        
        self.cont_btn.place(relx=1.0, x=-30, y=620, anchor="se")  # bottom-right corner


class MapSelectPage:
    """Page 2B: Interactive Marauder's Map with category selection pins"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref

        # determine base directory for asset loading
        base_dir = os.path.dirname(__file__)

        # paths for map background and pin button images
        bg_path = os.path.join(base_dir, "assets", "backgrounds", "map_select_bg.png")
        pin_char = os.path.join(base_dir, "assets", "buttons", "pin_characters.png")
        pin_spell = os.path.join(base_dir, "assets", "buttons", "pin_spells.png")
        pin_potion = os.path.join(base_dir, "assets", "buttons", "pin_potions.png")
        pin_books = os.path.join(base_dir, "assets", "buttons", "pin_books.png")
        pin_movies = os.path.join(base_dir, "assets", "buttons", "pin_movies.png")
        back_map = os.path.join(base_dir, "assets", "buttons", "back_btn.png")

        # Background setup (static map image)
        self.bg_img = tk.PhotoImage(file=bg_path)
        bg_label = tk.Label(parent, image=self.bg_img)
        bg_label.image = self.bg_img  # keep reference to prevent garbage collection
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # full screen coverage

        # Pin images loaded and resized for map markers
        self.pin_char_img = tk.PhotoImage(file=pin_char).subsample(3, 3)    # 33% original size
        self.pin_spell_img = tk.PhotoImage(file=pin_spell).subsample(3, 3)  # 33% original size
        self.pin_potion_img = tk.PhotoImage(file=pin_potion).subsample(3, 3)# 33% original size
        self.pin_books_img = tk.PhotoImage(file=pin_books).subsample(3, 3)  # 33% original size
        self.pin_movies_img = tk.PhotoImage(file=pin_movies).subsample(3, 3)# 33% original size

        # PIN BUTTONS placed at specific map coordinates
        # Spell Library pin button
        self.btn_spell = tk.Button(
            parent,
            image=self.pin_spell_img,
            bd=0, highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: app.click(app.show_spell_library)  # navigate to spells
        )
        self.btn_spell.image = self.pin_spell_img  # maintain image reference
        self.btn_spell.place(x=300, y=142)  # map coordinate for spells

        # Character Archives pin button
        self.btn_char = tk.Button(
            parent,
            image=self.pin_char_img,
            bd=0, highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: app.click(app.show_character_archives)  # navigate to characters
        )
        self.btn_char.image = self.pin_char_img  # maintain image reference
        self.btn_char.place(x=659, y=130)  # map coordinate for characters

        # Book Archives pin button
        self.btn_books = tk.Button(
            parent,
            image=self.pin_books_img,
            bd=0, highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: app.click(app.show_book_archives)  # navigate to books
        )
        self.btn_books.image = self.pin_books_img  # maintain image reference
        self.btn_books.place(x=388, y=378)  # map coordinate for books

        # Potion Library pin button
        self.btn_potion = tk.Button(
            parent,
            image=self.pin_potion_img,
            bd=0, highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: app.click(app.show_potion_library)  # navigate to potions
        )
        self.btn_potion.image = self.pin_potion_img  # maintain image reference
        self.btn_potion.place(x=535, y=476)  # map coordinate for potions

        # Movie Archives pin button
        self.btn_movies = tk.Button(
            parent,
            image=self.pin_movies_img,
            bd=0, highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: app.click(app.show_movie_archives)  # navigate to movies
        )
        self.btn_movies.image = self.pin_movies_img  # maintain image reference
        self.btn_movies.place(x=680, y=420)  # map coordinate for movies

        # Back button (return to map intro)
        self.back_img = tk.PhotoImage(file=back_map).subsample(3, 3)  # 33% original size
        self.btn_back = tk.Button(
            parent,
            image=self.back_img,
            bd=0,
            highlightthickness=0,
            bg="#000000",
            activebackground="#000000",
            command=lambda: app.click(app.show_map_intro)  # navigate back
        )
        self.btn_back.image = self.back_img  # maintain image reference
        self.btn_back.place(x=22, y=23)  # top-left corner positioning


class CharacterArchives:
    """Page 3A: Character search interface with scrollable card display"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref
        # base directory for asset loading
        self.base_dir = self.app.base_dir

        # BACKGROUND GIF setup with animation
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "character_list_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to map)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_char.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(3, 3)  # 33% original size
        back_btn = tk.Button(
            parent, 
            image=self.back_img, 
            bd=0,  # no border
            bg="#000000", 
            activebackground="#000000",
            command=lambda: app.click(app.show_map_select))  # navigate back to map
        back_btn.place(x=8, y=8)  # top-left positioning

        # SEARCH BAR for character name queries
        self.search_var = tk.StringVar()  # variable to track search text
        self.search_entry = ttk.Entry(
            parent, 
            textvariable=self.search_var, 
            font=("Consolas", 14),  # monospace font for consistency
            width=40)  # character width
        self.search_entry.place(x=200, y=130)  # positioned near top center

        # SEARCH BUTTON to trigger character search
        search_btn_path = os.path.join(self.base_dir, "Assets/buttons/search_btn.png")
        self.search_img = tk.PhotoImage(file=search_btn_path).subsample(3, 3)  # 33% original size
        tk.Button(
            parent, 
            image=self.search_img, 
            bd=0, 
            bg="#FFFFFF",  # white background for contrast
            activebackground="#FFFFFF",
            command=lambda: self.app.click(self.search_characters)  # trigger search
        ).place(x=694, y=129)  # positioned right of search bar

        # FILTER BUTTON (House) - AFTER search button
        filter_btn_path = os.path.join(self.base_dir, "Assets/buttons/filter_btn.png")
        self.filter_img = tk.PhotoImage(file=filter_btn_path).subsample(3, 3)

        self.filter_button = tk.Button(
            parent,
            image=self.filter_img,
            bd=0,
            bg="#FFFFFF",
            activebackground="#FFFFFF",
            command=self.open_filter_menu  # open house filter dropdown
        )
        self.filter_button.place(x=615, y=126)  # positioned left of search button

        # Current filter state for house selection
        self.current_filter = "All"  # Default: show characters from all houses

        # OUTER FRAME for scrollable card container
        outer_frame = tk.Frame(
            parent,
            bg="#200503",  # dark red-brown theme color
            bd=2,  # border width
            relief="ridge"  # 3D border style
        )
        outer_frame.place(
            relx=0.5,  # center horizontally
            y=412,  # vertical position
            anchor="center",  # center alignment
            width=661,  # fixed width
            height=412  # fixed height
        )

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            outer_frame,
            bg="#200503",  # match outer frame background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds character cards)
        self.card_frame = tk.Frame(self.canvas, bg="#200503")
        self.canvas.create_window((0, 0), window=self.card_frame, anchor="nw")  # top-left anchor

        # Update scroll region automatically when content changes
        self.card_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mousewheel handling for scroll navigation
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # Show initial placeholder message
        self.show_placeholder("Search for a wizard or witch ✨")
  
    def show_placeholder(self, text):
        """Display centered placeholder message in card area"""
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create a container frame to center the label
        container = tk.Frame(self.card_frame, bg="#200503", height=412, width=661)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Center the label with thematic styling
        tk.Label(
            container,
            text=text,
            bg="#200503",  # match background
            fg="#e6cfa7",  # parchment text color
            font=("Consolas", 15, "italic")  # styled font
        ).place(relx=0.5, rely=0.5, anchor="center")  # perfect center

    def show_loading(self):
        """Display loading animation while fetching data"""
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create loading container with fixed dimensions
        container = tk.Frame(self.card_frame, bg="#200503", height=412, width=661)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Loading text with dots animation
        self.loading_label = tk.Label(
            container,
            text="Searching...",
            bg="#200503",
            fg="#e6cfa7",  # parchment color
            font=("Consolas", 15, "italic")
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")  # center position
        
        # Start simple dots animation
        self.loading_dots = 0  # animation counter
        self.animate_loading()  # begin animation loop

    def animate_loading(self):
        """Simple dots animation for loading indication"""
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            try:
                if self.loading_label.winfo_exists():  # check if widget still exists
                    dots = ["Searching", "Searching.", "Searching..", "Searching..."]
                    self.loading_label.config(text=dots[self.loading_dots % 4])  # cycle dots
                    self.loading_dots += 1  # increment counter
                    self.parent.after(300, self.animate_loading)  # schedule next frame
            except (tk.TclError, AttributeError):
                pass  # widget destroyed, stop animation

    # Mousewheel helper methods for scroll navigation
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

# Logic adapted from:
# Stack Overflow (2021) – "Tkinter Mousewheel action for scrolling on canvas"
# https://stackoverflow.com/questions/51568717/tkinter-mousewheel-action-for-scrolling-on-canvas
    def _on_mousewheel(self, event):  
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def open_filter_menu(self):
        """Display dropdown menu for house filtering"""
        menu = tk.Menu(
            self.parent, 
            tearoff=0,  # prevent tear-off menu
            bg="#200503",  # theme background
            fg="#e6cfa7",  # parchment text
            activebackground="#38100d",  # card color for hover
            activeforeground="#e6cfa7",  # active text color
            font=("Consolas", 11),  # consistent font
            borderwidth=0  # no border
        )

        # Add filter options with house emojis
        menu.add_command(
            label="All Houses",
            command=lambda: self.apply_house_filter("All")  # show all houses
        )
        menu.add_separator()  # visual separation
        
        menu.add_command(
            label="Gryffindor 🦁",
            command=lambda: self.apply_house_filter("Gryffindor")
        )
        menu.add_command(
            label="Slytherin 🐍",
            command=lambda: self.apply_house_filter("Slytherin")
        )
        menu.add_command(
            label="Ravenclaw 🦅",
            command=lambda: self.apply_house_filter("Ravenclaw")
        )
        menu.add_command(
            label="Hufflepuff 🦡",
            command=lambda: self.apply_house_filter("Hufflepuff")
        )

        # Popup under the filter button
        menu.tk_popup(
            self.filter_button.winfo_rootx(),  # button x position
            self.filter_button.winfo_rooty() + 35  # button y + offset
        )

    def apply_house_filter(self, house):
        """Apply house filter to current search results"""
        self.current_filter = house  # update filter state
        
        # Get current search query from entry field
        query = self.search_var.get().strip()
        
        # Show loading indicator
        self.show_loading()
        
        # Apply filter in background thread to prevent UI freezing
        threading.Thread(
            target=self._perform_filtered_search,
            args=(query, house),
            daemon=True  # daemon thread (terminates with app)
        ).start()

    def search_characters(self):
        """Fetch characters from API with loading indicator"""
        # Clear the frame and show loading
        for w in self.card_frame.winfo_children():
            w.destroy()

        query = self.search_var.get().strip()  # get search text
        if not query:  # empty search check
            self.show_placeholder("Search for a wizard or witch ✨")
            return

        # Show loading animation
        self.show_loading()
        
        # Start search in background thread (with current filter)
        threading.Thread(
            target=self._perform_filtered_search,
            args=(query, self.current_filter),
            daemon=True
        ).start()

    def _perform_filtered_search(self, query, house):
        """Perform filtered search in background thread"""
        try:
            # Fetch character data from PotterDB API
            response = requests.get(
                API_URL,
                params={"page[size]": 100},  # limit to 100 results
                timeout=8  # 8-second timeout
            )
            data = response.json().get("data", [])  # extract character data

            # Apply name filter client-side (case-insensitive)
            if query:
                data = [
                    c for c in data
                    if query.lower() in c["attributes"]["name"].lower()
                ]

            # Apply house filter client-side
            if house != "All":
                data = [
                    c for c in data
                    if c["attributes"].get("house") == house  # exact match
                ]

            # Limit to 20 results for display performance
            data = data[:20]

            # Update UI in main thread (thread-safe)
            self.parent.after(0, lambda: self._display_filtered_results(data, query, house))

        except requests.exceptions.ConnectionError:
            # Network connection failure
            self.parent.after(
                0,
                lambda: self._display_error("🔌 No internet connection")
            )
        except requests.exceptions.Timeout:
            # API request timeout
            self.parent.after(
                0,
                lambda: self._display_error("⏳ Request timed out")
            )
        except Exception as e:
            # General error with truncated message
            self.parent.after(
                0,
                lambda: self._display_error(f"Error: {str(e)[:50]}")
            )

    def _display_filtered_results(self, data, query, house):
        """Display filtered search results in card format"""
        # Clear loading animation
        self.loading_label = None
            
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content

        if not data:  # no results found
            container = tk.Frame(self.card_frame, bg="#200503", height=412, width=661)
            container.pack_propagate(False)
            container.pack()
            
            filter_text = ""
            if house != "All":
                filter_text = f" with house: {house}"  # include filter info
            
            tk.Label(
                container,
                text=f"No characters found{filter_text}",
                bg="#200503",
                fg="white",  # neutral color for empty state
                font=("Consolas", 14)
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # Show filter status if active
        if house != "All":
            filter_label = tk.Label(
                self.card_frame,
                text=f"Filter: {house}",
                bg="#200503",
                fg="#e6cfa7",
                font=("Consolas", 12, "italic")
            )
            filter_label.pack(pady=(10, 5))  # spacing above cards

        # Create cards for each character
        for char in data:
            self.create_card(char)

    def create_card(self, char):
        """Create individual character card with image and details"""
        attr = char["attributes"]  # character attributes

        # Card frame with fixed dimensions
        card = tk.Frame(
            self.card_frame,
            bg="#38100d",  # card background color
            height=130,
            width=620  # consistent card width
        )
        card.pack(padx=10, pady=3)  # spacing between cards  
        card.pack_propagate(False)  # maintain fixed size

        # CHARACTER IMAGE (left side)
        img = self.load_image(attr.get("image"))
        tk.Label(
            card,
            image=img,
            bg="#38100d"  # match card background
        ).place(x=10, y=10)
        card.image = img  # keep reference to prevent garbage collection

        # CHARACTER NAME (top-right)
        tk.Label(
            card,
            text=attr.get("name", "Unknown"),
            font=("Courier New", 13, "bold"),  # distinctive font
            fg="#EFF1F1",  # light text color
            bg="#38100d",
            wraplength=480,  # prevent text overflow
            justify="left"  # left alignment
        ).place(x=110, y=10)

        # HOUSE INFORMATION (middle-right)
        tk.Label(
            card,
            text=f"House: {attr.get('house') or 'Unknown'}",
            font=("Consolas", 11),
            fg="white",  # standard white
            bg="#38100d"
        ).place(x=110, y=50)

        # VIEW BUTTON (bottom-right)
        tk.Button(
            card,
            text="View Character",
            font=("Consolas", 12, "bold"),
            bg="#410602",  # button background
            fg="white",  # button text
            activebackground="#662D29",  # hover color
            bd=0,  # no border
            command=lambda c=char: self.app.click(lambda: self.app.show_character_detail(c))
        ).place(x=110, y=80)

    def _display_error(self, message):
        """Display error message in card area"""
        self.loading_label = None  # Stop loading animation
            
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
            
        container = tk.Frame(self.card_frame, bg="#200503", height=412, width=661)
        container.pack_propagate(False)
        container.pack()
        
        # Error message with red text for visibility
        tk.Label(
            container,
            text=message,
            bg="#200503",
            fg="#ff6b6b",  # red error color
            font=("Consolas", 14)
        ).place(relx=0.5, rely=0.5, anchor="center")

    def load_image(self, url):
        """Load character image from URL or fallback to default"""
        try:
            if not url:
                raise ValueError  # no image URL provided
            img_data = requests.get(url, timeout=5).content  # fetch image data
            img = Image.open(io.BytesIO(img_data)).resize((90, 110))  # standard size
        except:
            # fallback to default "no image" placeholder
            img = Image.open(
                os.path.join(self.base_dir, "Assets", "no_image.png")
            ).resize((90, 110))

        return ImageTk.PhotoImage(img)  # convert to Tkinter format
    
    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation
    
class CharacterDetailPage:
    """Page 3B: Detailed character information display with image and attributes"""
    
    def __init__(self, parent, app, char):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app
        # base directory for asset loading
        self.base_dir = app.base_dir
        # extract character attributes from API data
        attr = char["attributes"]

        # BACKGROUND GIF setup for detail page
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "character_detail_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0,
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to character archives)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_arrow.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(4, 4)  # 25% original size
        back_btn = tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_character_archives)  # navigate back
        )
        back_btn.place(x=9, y=9)  # top-left positioning
        back_btn.image = self.back_img  # maintain image reference

        # CHARACTER IMAGE display (left side of screen)
        self.char_img = self.load_image(attr.get("image"))  # load from URL or fallback
        char_label = tk.Label(parent, image=self.char_img, bg="#000000")
        char_label.place(x=125, y=258)  # centered vertically
        char_label.image = self.char_img  # maintain image reference

        # DETAILS FRAME container for character attributes
        info_frame = tk.Frame(
            parent,
            bg="#4e0c00",  # dark red-brown theme
            bd=2,  # border width
            relief="ridge",  # 3D border style
            padx=20,  # internal horizontal padding
            pady=20   # internal vertical padding
        )
        info_frame.place(x=450, y=224, width=461, height=318)  # right side position

        # DETAILS CONTENT organized in two-column grid
        details = [
            ("Name", attr.get("name")),
            ("Gender", attr.get("gender")),
            ("House", attr.get("house")),
            ("Blood Status", attr.get("blood_status")),
            ("Species", attr.get("species")),
            ("Eye Color", attr.get("eye_color")),
            ("Hair Color", attr.get("hair_color")),
            ("Boggart", attr.get("boggart")),
        ]

        # Populate grid with labels and values
        for i, (label_text, value) in enumerate(details):
            col = i % 2  # column 0 or 1 (two-column layout)
            row = i // 2  # row index (0-3)

            # Attribute label (bold, left-aligned)
            tk.Label(
                info_frame,
                text=f"{label_text}:",
                font=("Consolas", 15, "bold"),  # bold for labels
                fg="#EFF1F1",  # light text color
                bg="#4e0c00",  # match frame background
                anchor="w"  # left alignment
            ).grid(row=row * 2, column=col, sticky="w", padx=10, pady=(4, 0))

            # Attribute value (regular weight, with wrapping)
            tk.Label(
                info_frame,
                text=value or "Unknown",  # use "Unknown" for missing values
                font=("Consolas", 13),  # slightly smaller than labels
                fg="#F17B72",  # pinkish highlight color
                bg="#4e0c00",  # match background
                wraplength=220,  # prevent text overflow
                justify="left"  # left alignment
            ).grid(row=row * 2 + 1, column=col, sticky="w", padx=10, pady=(0, 8))

        # Configure columns to stretch evenly for balanced layout
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

    def load_image(self, url):
        """Load character image from URL or fallback to default placeholder"""
        try:
            if not url:
                raise ValueError  # no URL provided
            img_data = requests.get(url, timeout=5).content  # fetch image data
            img = Image.open(io.BytesIO(img_data)).resize((195, 268))  # detail size
        except:
            # fallback to default "no image" placeholder
            img = Image.open(
                os.path.join(self.base_dir, "Assets", "no_image.png")
            ).resize((195, 268))

        return ImageTk.PhotoImage(img)  # convert to Tkinter format

    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


class SpellArchives:
    """Page 4A: Spell search interface with scrollable card display"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref
        # base directory for asset loading
        self.base_dir = self.app.base_dir

        # BACKGROUND GIF setup with animation
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "spell_list_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to map)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_spell.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(3, 3)  # 33% original size
        tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#022936",  # dark blue-green background
            activebackground="#000000",  # black when active
            command=lambda: app.click(app.show_map_select)  # navigate back to map
        ).place(x=9, y=16)  # top-left positioning

        # SEARCH BAR for spell name queries
        self.search_var = tk.StringVar()  # variable to track search text
        ttk.Entry(
            parent,
            textvariable=self.search_var,
            font=("Consolas", 14),  # monospace font for consistency
            width=40  # character width
        ).place(x=200, y=130)  # positioned near top center

        # SEARCH BUTTON to trigger spell search
        search_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "search_btn1.png")
        self.search_img = tk.PhotoImage(file=search_btn_path).subsample(3, 3)  # 33% original size
        tk.Button(
            parent,
            image=self.search_img,
            bd=0,
            bg="#FFFFFF",  # white background for contrast
            activebackground="#FFFFFF",
            command=lambda: self.app.click(self.search_spells)  # trigger search
        ).place(x=694, y=129)  # positioned right of search bar

        # FILTER BUTTON (Category) - AFTER search button
        filter_btn_path = os.path.join(self.base_dir, "Assets/buttons/filter_btn1.png")
        self.filter_img = tk.PhotoImage(file=filter_btn_path).subsample(3, 3)

        self.filter_button = tk.Button(
            parent,
            image=self.filter_img,
            bd=0,
            bg="#FFFFFF",
            activebackground="#FFFFFF",
            command=self.open_filter_menu  # open category filter dropdown
        )
        self.filter_button.place(x=617, y=126)  # positioned left of search button

        # Current filter state for category selection
        self.current_filter = "All"  # Default: show spells from all categories

        # OUTER FRAME for scrollable card container
        outer_frame = tk.Frame(
            parent,
            bg="#090b16",  # dark blue theme color
            bd=2,  # border width
            relief="ridge"  # 3D border style
        )
        outer_frame.place(
            relx=0.5,  # center horizontally
            y=412,  # vertical position
            anchor="center",  # center alignment
            width=661,  # fixed width
            height=412  # fixed height
        )

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            outer_frame,
            bg="#090b16",  # match outer frame background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds spell cards)
        self.card_frame = tk.Frame(self.canvas, bg="#090b16")
        self.canvas.create_window((0, 0), window=self.card_frame, anchor="nw")  # top-left anchor

        # Update scroll region automatically when content changes
        self.card_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mousewheel handling for scroll navigation
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # Show initial placeholder message
        self.show_placeholder("Search your magical spell ✨")

    def show_placeholder(self, text):
        """Display centered placeholder message in card area"""
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create a container frame to center the label
        container = tk.Frame(self.card_frame, bg="#090b16", height=412, width=661)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Center the label with thematic styling
        tk.Label(
            container,
            text=text,
            bg="#090b16",  # match background
            fg="#9fdcff",  # light blue spell text color
            font=("Consolas", 15, "italic")  # styled font
        ).place(relx=0.5, rely=0.5, anchor="center")  # perfect center

    def show_loading(self):
        """Display loading animation while fetching data"""
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create loading container with fixed dimensions
        container = tk.Frame(self.card_frame, bg="#090b16", height=412, width=661)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Loading text with dots animation
        self.loading_label = tk.Label(
            container,
            text="Searching...",
            bg="#090b16",
            fg="#9fdcff",  # light blue color
            font=("Consolas", 15, "italic")
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")  # center position
        
        # Start simple dots animation
        self.loading_dots = 0  # animation counter
        self.animate_loading()  # begin animation loop

    def animate_loading(self):
        """Simple dots animation for loading indication"""
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            try:
                if self.loading_label.winfo_exists():  # check if widget still exists
                    dots = ["Searching", "Searching.", "Searching..", "Searching..."]
                    self.loading_label.config(text=dots[self.loading_dots % 4])  # cycle dots
                    self.loading_dots += 1  # increment counter
                    self.parent.after(300, self.animate_loading)  # schedule next frame
            except (tk.TclError, AttributeError):
                pass  # widget destroyed, stop animation

    # Mousewheel helper methods for scroll navigation
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def open_filter_menu(self):
        """Display dropdown menu for spell category filtering"""
        menu = tk.Menu(
            self.parent, 
            tearoff=0,  # prevent tear-off menu
            bg="#090b16",  # spell theme background
            fg="#9fdcff",  # spell theme text color
            activebackground="#171D2E",  # spell card color for hover
            activeforeground="#9fdcff",  # active text color
            font=("Consolas", 11),  # consistent font
            borderwidth=0  # no border
        )

        # Add filter options with category emojis
        menu.add_command(
            label="All Categories",
            command=lambda: self.apply_category_filter("All")  # show all categories
        )
        menu.add_separator()  # visual separation
        
        # Spell category options with thematic emojis
        menu.add_command(
            label="Charm ✨",
            command=lambda: self.apply_category_filter("Charm")
        )
        menu.add_command(
            label="Transfiguration 🔄",
            command=lambda: self.apply_category_filter("Transfiguration")
        )
        menu.add_command(
            label="Curse ☠️",
            command=lambda: self.apply_category_filter("Curse")
        )
        menu.add_command(
            label="Hex 🔮",
            command=lambda: self.apply_category_filter("Hex")
        )
        menu.add_command(
            label="Jinx ⚡",
            command=lambda: self.apply_category_filter("Jinx")
        )
        menu.add_command(
            label="Healing spell 💚",
            command=lambda: self.apply_category_filter("Healing spell")
        )
        menu.add_command(
            label="Unknown ❓",
            command=lambda: self.apply_category_filter("Unknown")
        )

        # Popup under the filter button
        menu.tk_popup(
            self.filter_button.winfo_rootx(),  # button x position
            self.filter_button.winfo_rooty() + 35  # button y + offset
        )

    def apply_category_filter(self, category):
        """Apply category filter to current search results"""
        self.current_filter = category  # update filter state
        
        # Get current search query from entry field
        query = self.search_var.get().strip()
        
        # Show loading indicator
        self.show_loading()
        
        # Apply filter in background thread to prevent UI freezing
        threading.Thread(
            target=self._perform_filtered_search,
            args=(query, category),
            daemon=True  # daemon thread (terminates with app)
        ).start()

    def search_spells(self):
        """Fetch spells from API with loading indicator"""
        # Clear the frame and show loading
        for w in self.card_frame.winfo_children():
            w.destroy()

        query = self.search_var.get().strip()  # get search text
        if not query:  # empty search check
            self.show_placeholder("Search your magical spell ✨")
            return

        # Show loading animation
        self.show_loading()
        
        # Start search in background thread (with current filter)
        threading.Thread(
            target=self._perform_filtered_search,
            args=(query, self.current_filter),
            daemon=True
        ).start()

    def _perform_filtered_search(self, query, category):
        """Perform filtered search in background thread"""

# HTTP request timeout handling Adapted from: Stack Overflow
# T. (2014). "Timeout for Python requests.get() entire response"
# https://stackoverflow.com/questions/21965484/timeout-for-python-requests-get-entire-response 
       
        try:
            # Fetch spell data from PotterDB API
            response = requests.get(
                SPELL_API_URL,
                params={"page[size]": 100},  # limit to 100 results
                timeout=15  # 15-second timeout for spell data
            )
            data = response.json().get("data", [])  # extract spell data

            # Apply name filter client-side (case-insensitive)
            if query:
                data = [
                    s for s in data
                    if query.lower() in s["attributes"]["name"].lower()
                ]

            # Apply category filter client-side
            if category != "All":
                if category == "Unknown":
                    # Handle spells with null/empty category
                    data = [
                        s for s in data
                        if not s["attributes"].get("category") or 
                        s["attributes"].get("category") is None
                    ]
                else:
                    # Filter by specific category
                    data = [
                        s for s in data
                        if s["attributes"].get("category") == category
                    ]

            # Limit to 20 results for display performance
            data = data[:20]

            # Update UI in main thread (thread-safe)
            self.parent.after(0, lambda: self._display_filtered_results(data, query, category))

        except Exception as e:
            # General error handling
            self.parent.after(0, lambda: self._display_error(f"Error: {str(e)}"))

    def _display_filtered_results(self, data, query, category):
        """Display filtered search results in card format"""
        # Clear loading animation
        self.loading_label = None
            
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content

        if not data:  # no results found
            container = tk.Frame(self.card_frame, bg="#090b16", height=412, width=661)
            container.pack_propagate(False)
            container.pack()
            
            filter_text = ""
            if category != "All":
                filter_text = f" with category: {category}"  # include filter info
            
            tk.Label(
                container,
                text=f"No spells found{filter_text}",
                bg="#090b16",
                fg="#9fdcff",  # theme color for empty state
                font=("Consolas", 14)
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # Show filter status if active
        if category != "All":
            filter_label = tk.Label(
                self.card_frame,
                text=f"Filter: {category}",
                bg="#090b16",
                fg="#9fdcff",
                font=("Consolas", 12, "italic")
            )
            filter_label.pack(pady=(10, 5))  # spacing above cards

        # Create cards for each spell
        for spell in data:
            self.create_card(spell)

    def create_card(self, spell):
        """Create individual spell card with image and details"""
        attr = spell["attributes"]  # spell attributes

        # Card frame with fixed dimensions
        card = tk.Frame(
            self.card_frame,
            bg="#171D2E",  # dark blue card background
            height=130,
            width=620  # consistent card width
        )
        card.pack(padx=10, pady=3)  # spacing between cards
        card.pack_propagate(False)  # maintain fixed size

        # SPELL IMAGE (left side)
        img = self.load_image(attr.get("image"))
        tk.Label(
            card,
            image=img,
            bg="#171D2E"  # match card background
        ).place(x=10, y=10)
        card.image = img  # keep reference to prevent garbage collection

        # SPELL NAME (top-right)
        tk.Label(
            card,
            text=attr.get("name", "Unknown Spell"),
            font=("Courier New", 13, "bold"),  # distinctive font
            fg="#F5E9FF",  # light purple text color
            bg="#171D2E",
            wraplength=480,  # prevent text overflow
            justify="left"  # left alignment
        ).place(x=110, y=10)

        # CATEGORY INFORMATION (middle-right)
        tk.Label(
            card,
            text=f"Category: {attr.get('category') or 'Unknown'}",
            font=("Consolas", 11),
            fg="white",  # standard white
            bg="#171D2E"
        ).place(x=110, y=50)

        # VIEW BUTTON (bottom-right)
        tk.Button(
            card,
            text="View Spell",
            font=("Consolas", 12, "bold"),
            bg="#090b16",  # button background
            fg="white",  # button text
            activebackground="#171D2E",  # hover color
            bd=0,  # no border
            command=lambda s=spell: self.app.click(lambda: self.app.show_spell_detail(s))
        ).place(x=110, y=80)

    def _display_error(self, message):
        """Display error message in card area"""
        self.loading_label = None  # Stop loading animation
            
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
            
        container = tk.Frame(self.card_frame, bg="#090b16", height=412, width=661)
        container.pack_propagate(False)
        container.pack()
        
        # Error message with red text for visibility
        tk.Label(
            container,
            text=message,
            bg="#090b16",
            fg="#ff6b6b",  # red error color
            font=("Consolas", 14)
        ).place(relx=0.5, rely=0.5, anchor="center")

    def load_image(self, url):
        """Load spell image from URL or fallback to default"""
        try:
            if not url:
                raise ValueError  # no image URL provided
            img_data = requests.get(url, timeout=5).content  # fetch image data
            img = Image.open(io.BytesIO(img_data)).resize((90, 110))  # standard size
        except:
            # fallback to default "no image" placeholder for spells
            img = Image.open(
                os.path.join(self.base_dir, "Assets", "no_image1.png")
            ).resize((90, 110), Image.NEAREST)  # use nearest neighbor for pixel art

        return ImageTk.PhotoImage(img)  # convert to Tkinter format

    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation

class SpellDetailPage:
    """Page 4B: Detailed spell information display with image and magical attributes"""
    
    def __init__(self, parent, app, spell):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app
        # base directory for asset loading
        self.base_dir = app.base_dir
        # extract spell attributes from API data
        attr = spell["attributes"]

        # BACKGROUND GIF setup for detail page
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "spell_detail_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to spell archives)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_arrow1.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(4, 4)  # 25% original size
        back_btn = tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_spell_library)  # navigate back
        )
        back_btn.place(x=4, y=4)  # top-left positioning
        back_btn.image = self.back_img  # maintain image reference

        # SPELL IMAGE display (left side of screen)
        self.spell_img = self.load_image(attr.get("image"))  # load from URL or fallback
        spell_img_label = tk.Label(parent, image=self.spell_img, bg="#183447")  # blue-gray background
        spell_img_label.place(x=115, y=255)  # centered vertically
        spell_img_label.image = self.spell_img  # maintain image reference

        # DETAILS FRAME container for spell attributes
        info_frame = tk.Frame(
            parent,
            bg="#183447",  # dark blue-gray theme
            bd=2,  # border width
            padx=10,  # internal horizontal padding
            pady=10   # internal vertical padding
        )
        info_frame.place(x=525, y=228, width=390, height=290)  # right side position

        # DETAILS CONTENT organized in two-column grid
        details = [
            ("Name", attr.get("name")),
            ("Category", attr.get("category")),
            ("Effect", attr.get("effect")),
            ("Incantation", attr.get("incantation")),
            ("Light", attr.get("light")),
            ("Hand", attr.get("hand")),
            ("Creator", attr.get("creator")),
            ("Pronunciation", attr.get("pronunciation")),
        ]

        # Populate grid with labels and values
        for i, (label, value) in enumerate(details):
            col = i % 2  # column 0 or 1 (two-column layout)
            row = i // 2  # row index (0-3)

            # Attribute label (bold, left-aligned)
            tk.Label(
                info_frame,
                text=f"{label}:",
                font=("Consolas", 12, "bold"),  # bold for labels
                fg="#F5E9FF",  # light purple text color
                bg="#183447",  # match frame background
            ).grid(row=row * 2, column=col, sticky="w", padx=10, pady=(4, 0))

            # Attribute value (regular weight, with wrapping)
            tk.Label(
                info_frame,
                text=value or "Unknown",  # use "Unknown" for missing values
                font=("Consolas", 11),  # slightly smaller than labels
                fg="#14ADE0",  # bright blue highlight color
                bg="#183447",  # match background
                wraplength=195,  # prevent text overflow in narrow columns
                justify="left"  # left alignment
            ).grid(row=row * 2 + 1, column=col, sticky="w", padx=10, pady=(0, 8))

        # Configure columns to stretch evenly for balanced layout
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

    def load_image(self, url):
        """Load spell image from URL or fallback to default placeholder"""
        try:
            if not url:
                raise ValueError  # no URL provided
            img_data = requests.get(url, timeout=5).content  # fetch image data
            img = Image.open(io.BytesIO(img_data)).resize((210, 255))  # detail size for spells
        except:
            # fallback to default "no image" placeholder for spells
            img = Image.open(
                os.path.join(self.base_dir, "Assets", "no_image1.png")
            ).resize((210, 255), Image.LANCZOS)  # high-quality resampling for spells

        return ImageTk.PhotoImage(img)  # convert to Tkinter format
    
    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


class PotionArchives:
    """Page 5A: Potion search interface with scrollable card display"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref
        # base directory for asset loading
        self.base_dir = self.app.base_dir

        # BACKGROUND GIF setup with animation
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "potion_list_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to map)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_potion.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(3, 3)  # 33% original size
        back_btn = tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_map_select)  # navigate back to map
        )
        back_btn.place(x=5, y=5)  # top-left positioning
        back_btn.image = self.back_img  # maintain image reference

        # SEARCH BAR for potion name queries
        self.search_var = tk.StringVar()  # variable to track search text
        ttk.Entry(
            parent,
            textvariable=self.search_var,
            font=("Consolas", 14),  # monospace font for consistency
            width=40  # character width
        ).place(x=200, y=130)  # positioned near top center

        # SEARCH BUTTON to trigger potion search
        search_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "search_btn2.png")
        self.search_img = tk.PhotoImage(file=search_btn_path).subsample(3, 3)  # 33% original size
        tk.Button(
            parent,
            image=self.search_img,
            bd=0,
            bg="#FFFFFF",  # white background for contrast
            activebackground="#FFFFFF",
            command=lambda: self.app.click(self.search_potions)  # trigger search
        ).place(x=694, y=129)  # positioned right of search bar

        # FILTER BUTTON (Difficulty) - AFTER search button
        filter_btn_path = os.path.join(self.base_dir, "Assets/buttons/filter_btn.png")
        self.filter_img = tk.PhotoImage(file=filter_btn_path).subsample(3, 3)

        self.filter_button = tk.Button(
            parent,
            image=self.filter_img,
            bd=0,
            bg="#FFFFFF",
            activebackground="#FFFFFF",
            command=self.open_filter_menu  # open difficulty filter dropdown
        )
        self.filter_button.place(x=615, y=126)  # positioned left of search button

        # Current filter state for difficulty selection
        self.current_filter = "All"  # Default: show potions of all difficulties

        # OUTER FRAME for scrollable card container
        outer_frame = tk.Frame(
            parent,
            bg="#49241f",  # dark red-brown theme color
            bd=2,  # border width
            relief="ridge"  # 3D border style
        )
        outer_frame.place(
            relx=0.5,  # center horizontally
            y=412,  # vertical position
            anchor="center",  # center alignment
            width=661,  # fixed width
            height=412  # fixed height
        )

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            outer_frame,
            bg="#49241f",  # match outer frame background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds potion cards)
        self.card_frame = tk.Frame(self.canvas, bg="#49241f")
        self.canvas.create_window((0, 0), window=self.card_frame, anchor="nw")  # top-left anchor

        # Update scroll region automatically when content changes
        self.card_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mousewheel handling for scroll navigation
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # Show initial placeholder message
        self.show_placeholder("Search for a magical potion 🧪")

    def show_placeholder(self, text):
        """Display centered placeholder message in card area"""
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create a container frame to center the label
        container = tk.Frame(self.card_frame, bg="#49241f", height=412, width=661)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Center the label with thematic styling
        tk.Label(
            container,
            text=text,
            bg="#49241f",  # match background
            fg="#ffc4bb",  # light pink potion text color
            font=("Consolas", 15, "italic")  # styled font
        ).place(relx=0.5, rely=0.5, anchor="center")  # perfect center

    def show_loading(self):
        """Display loading animation while fetching data"""
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create loading container with fixed dimensions
        container = tk.Frame(self.card_frame, bg="#49241f", height=412, width=661)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Loading text with dots animation
        self.loading_label = tk.Label(
            container,
            text="Searching...",
            bg="#49241f",
            fg="#ffc4bb",  # light pink color
            font=("Consolas", 15, "italic")
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")  # center position
        
        # Start simple dots animation
        self.loading_dots = 0  # animation counter
        self.animate_loading()  # begin animation loop

    def animate_loading(self):
        """Simple dots animation for loading indication"""
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            try:
                if self.loading_label.winfo_exists():  # check if widget still exists
                    dots = ["Searching", "Searching.", "Searching..", "Searching..."]
                    self.loading_label.config(text=dots[self.loading_dots % 4])  # cycle dots
                    self.loading_dots += 1  # increment counter
                    self.parent.after(300, self.animate_loading)  # schedule next frame
            except (tk.TclError, AttributeError):
                pass  # widget destroyed, stop animation

    # Mousewheel helper methods for scroll navigation
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def open_filter_menu(self):
        """Display dropdown menu for potion difficulty filtering"""
        menu = tk.Menu(
            self.parent, 
            tearoff=0,  # prevent tear-off menu
            bg="#49241f",  # potion theme background
            fg="#ffc4bb",  # potion theme text color
            activebackground="#6d332a",  # potion card color for hover
            activeforeground="#ffc4bb",  # active text color
            font=("Consolas", 11),  # consistent font
            borderwidth=0  # no border
        )

        # Add filter options with potion emojis
        menu.add_command(
            label="All Difficulties",
            command=lambda: self.apply_difficulty_filter("All")  # show all difficulties
        )
        menu.add_separator()  # visual separation
        
        # Potion difficulty options with thematic emojis
        menu.add_command(
            label="Beginner 🧪",
            command=lambda: self.apply_difficulty_filter("Beginner")
        )
        menu.add_command(
            label="Moderate 🧪🧪",
            command=lambda: self.apply_difficulty_filter("Moderate")
        )
        menu.add_command(
            label="Advanced 🧪🧪🧪",
            command=lambda: self.apply_difficulty_filter("Advanced")
        )
        menu.add_command(
            label="Unknown ❓",
            command=lambda: self.apply_difficulty_filter("Unknown")
        )

        # Popup under the filter button
        menu.tk_popup(
            self.filter_button.winfo_rootx(),  # button x position
            self.filter_button.winfo_rooty() + 35  # button y + offset
        )

    def apply_difficulty_filter(self, difficulty):
        """Apply difficulty filter to current search results"""
        self.current_filter = difficulty  # update filter state
        
        # Get current search query from entry field
        query = self.search_var.get().strip()
        
        # Show loading indicator
        self.show_loading()
        
        # Apply filter in background thread to prevent UI freezing
        threading.Thread(
            target=self._perform_filtered_search,
            args=(query, difficulty),
            daemon=True  # daemon thread (terminates with app)
        ).start()

    def search_potions(self):
        """Fetch potions from API with loading indicator"""
        # Clear the frame and show loading
        for w in self.card_frame.winfo_children():
            w.destroy()

        query = self.search_var.get().strip()  # get search text
        if not query:  # empty search check
            self.show_placeholder("Search for a magical potion 🧪")
            return

        # Show loading animation
        self.show_loading()
        
        # Start search in background thread (with current filter)
        threading.Thread(
            target=self._perform_filtered_search,
            args=(query, self.current_filter),
            daemon=True
        ).start()

    def _perform_filtered_search(self, query, difficulty):
        """Perform filtered search in background thread"""
        try:
            # Fetch potion data from PotterDB API
            response = requests.get(
                POTION_API_URL,
                params={"page[size]": 100},  # limit to 100 results
                timeout=15  # 15-second timeout for potion data
            )
            data = response.json().get("data", [])  # extract potion data

            # Apply name filter client-side (case-insensitive)
            if query:
                data = [
                    p for p in data
                    if query.lower() in p["attributes"]["name"].lower()
                ]

            # Apply difficulty filter client-side
            if difficulty != "All":
                if difficulty == "Unknown":
                    # Handle potions with null/empty difficulty
                    data = [
                        p for p in data
                        if not p["attributes"].get("difficulty") or 
                        p["attributes"].get("difficulty") is None
                    ]
                else:
                    # Filter by specific difficulty
                    data = [
                        p for p in data
                        if p["attributes"].get("difficulty") == difficulty
                    ]

            # Limit to 20 results for display performance
            data = data[:20]

            # Update UI in main thread (thread-safe)
            self.parent.after(0, lambda: self._display_filtered_results(data, query, difficulty))

        except Exception as e:
            # General error handling
            self.parent.after(0, lambda: self._display_error(f"Error: {str(e)}"))

    def _display_filtered_results(self, data, query, difficulty):
        """Display filtered search results in card format"""
        # Clear loading animation
        self.loading_label = None
            
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content

        if not data:  # no results found
            container = tk.Frame(self.card_frame, bg="#49241f", height=412, width=661)
            container.pack_propagate(False)
            container.pack()
            
            filter_text = ""
            if difficulty != "All":
                filter_text = f" with difficulty: {difficulty}"  # include filter info
            
            tk.Label(
                container,
                text=f"No potions found{filter_text}",
                bg="#49241f",
                fg="#ffc4bb",  # theme color for empty state
                font=("Consolas", 14)
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # Show filter status if active
        if difficulty != "All":
            filter_label = tk.Label(
                self.card_frame,
                text=f"Filter: {difficulty}",
                bg="#49241f",
                fg="#ffc4bb",
                font=("Consolas", 12, "italic")
            )
            filter_label.pack(pady=(10, 5))  # spacing above cards

        # Create cards for each potion
        for potion in data:
            self.create_card(potion)

    def create_card(self, potion):
        """Create individual potion card with image and details"""
        attr = potion["attributes"]  # potion attributes

        # Card frame with fixed dimensions
        card = tk.Frame(
            self.card_frame,
            bg="#6d332a",  # medium brown card background
            height=130,
            width=620  # consistent card width
        )
        card.pack(padx=10, pady=3)  # spacing between cards
        card.pack_propagate(False)  # maintain fixed size

        # POTION IMAGE (left side)
        img = self.load_image(attr.get("image"))
        tk.Label(
            card,
            image=img,
            bg="#6d332a"  # match card background
        ).place(x=10, y=10)
        card.image = img  # keep reference to prevent garbage collection

        # POTION NAME (top-right)
        tk.Label(
            card,
            text=attr.get("name", "Unknown Potion"),
            font=("Courier New", 13, "bold"),  # distinctive font
            fg="#E8F5E9",  # light green text color
            bg="#6d332a",
            wraplength=480,  # prevent text overflow
            justify="left"  # left alignment
        ).place(x=110, y=10)

        # DIFFICULTY INFORMATION (middle-right)
        tk.Label(
            card,
            text=f"Difficulty: {attr.get('difficulty') or 'Unknown'}",
            font=("Consolas", 11),
            fg="white",  # standard white
            bg="#6d332a"
        ).place(x=110, y=50)

        # VIEW BUTTON (bottom-right)
        tk.Button(
            card,
            text="View Potion",
            font=("Consolas", 12, "bold"),
            bg="#5b352f",  # dark brown button background
            fg="white",  # button text
            activebackground="#49241f",  # hover color (lighter brown)
            bd=0,  # no border
            command=lambda p=potion: self.app.click(lambda: self.app.show_potion_detail(p))
        ).place(x=110, y=80)

    def _display_error(self, message):
        """Display error message in card area"""
        self.loading_label = None  # Stop loading animation
            
        for w in self.card_frame.winfo_children():
            w.destroy()  # clear existing content
            
        container = tk.Frame(self.card_frame, bg="#49241f", height=412, width=661)
        container.pack_propagate(False)
        container.pack()
        
        # Error message with red text for visibility
        tk.Label(
            container,
            text=message,
            bg="#49241f",
            fg="#ff6b6b",  # red error color
            font=("Consolas", 14)
        ).place(relx=0.5, rely=0.5, anchor="center")

    def load_image(self, url):
        """Load potion image from URL or fallback to default"""
        try:
            if not url:
                raise ValueError  # no image URL provided
            img_data = requests.get(url, timeout=5).content  # fetch image data
            img = Image.open(io.BytesIO(img_data)).resize((90, 110))  # standard size
        except:
            # fallback to default "no image" placeholder for potions
            img = Image.open(
                os.path.join(self.base_dir, "Assets", "no_image2.png")
            ).resize((90, 110))

        return ImageTk.PhotoImage(img)  # convert to Tkinter format
    
    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


class PotionDetailPage:
    """Page 5B: Detailed potion information display with image and brewing attributes"""
    
    def __init__(self, parent, app, potion):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app
        # base directory for asset loading
        self.base_dir = app.base_dir
        # extract potion attributes from API data
        attr = potion["attributes"]

        # BACKGROUND GIF setup for detail page
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "potion_detail_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to potion archives)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_arrow2.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(4, 4)  # 25% original size
        back_btn = tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_potion_library)  # navigate back
        )
        back_btn.place(x=4, y=4)  # top-left positioning
        back_btn.image = self.back_img  # maintain image reference

        # POTION IMAGE display (left side of screen)
        self.potion_img = self.load_image(attr.get("image"))  # load from URL or fallback
        potion_img_label = tk.Label(
            parent,
            image=self.potion_img,
            bg="#5b352f"  # dark brown background for potion theme
        )
        potion_img_label.place(x=106, y=236)  # centered vertically
        potion_img_label.image = self.potion_img  # maintain image reference

        # DETAILS FRAME container for potion attributes
        info_frame = tk.Frame(
            parent,
            bg="#5b352f",  # medium brown theme color
            bd=2,  # border width
            padx=10,  # internal horizontal padding
            pady=10   # internal vertical padding
        )
        info_frame.place(x=476, y=219, width=435, height=325)  # right side position

        # DETAILS CONTENT organized in two-column grid
        details = [
            ("Name", attr.get("name")),
            ("Difficulty", attr.get("difficulty")),
            ("Effect", attr.get("effect")),
            ("Characteristics", attr.get("characteristics")),
            ("Ingredients", attr.get("ingredients")),
            ("Inventors", attr.get("inventors")),
            ("Side Effects", attr.get("side_effects")),
            ("Time", attr.get("time")),
        ]

        # Populate grid with labels and values
        for i, (label, value) in enumerate(details):
            col = i % 2  # column 0 or 1 (two-column layout)
            row = i // 2  # row index (0-3)

            # Attribute label (bold, left-aligned)
            tk.Label(
                info_frame,
                text=f"{label}:",
                font=("Consolas", 13, "bold"),  # bold for labels
                fg="#E8F5E9",  # light green text color (potion theme)
                bg="#5b352f",  # match frame background
            ).grid(row=row * 2, column=col, sticky="w", padx=5, pady=(2, 0))

            # Attribute value (regular weight, with wrapping)
            tk.Label(
                info_frame,
                text=value or "Unknown",  # use "Unknown" for missing values
                font=("Consolas", 11),  # slightly smaller than labels
                fg="#ffc4bb",  # light pink highlight color
                bg="#5b352f",  # match background
                wraplength=195,  # prevent text overflow in narrow columns
                justify="left"  # left alignment
            ).grid(row=row * 2 + 1, column=col, sticky="w", padx=5, pady=(0, 4))

        # Configure columns to stretch evenly for balanced layout
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

    def load_image(self, url):
        """Load potion image from URL or fallback to default placeholder"""
        try:
            if not url:
                raise ValueError  # no URL provided
            img_data = requests.get(url, timeout=5).content  # fetch image data
            img = Image.open(io.BytesIO(img_data)).resize((210, 280))  # detail size for potions
        except:
            # fallback to default "no image" placeholder for potions
            img = Image.open(
                os.path.join(self.base_dir, "Assets", "no_image2.png")
            ).resize((210, 280))

        return ImageTk.PhotoImage(img)  # convert to Tkinter format
    
    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


class MovieArchives:
    """Page 6A: Movie catalog with scrollable card display and poster images"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref
        # base directory for asset loading
        self.base_dir = self.app.base_dir

        # BACKGROUND GIF setup with animation
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "movie_list_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to map)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_movie.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(3, 3)  # 33% original size
        tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_map_select)  # navigate back to map
        ).place(x=17, y=14)  # top-left positioning

        # OUTER FRAME for scrollable card container (movie theater style)
        outer_frame = tk.Frame(
            parent,
            bg="#3A0F0A",  # dark red cinema theme
            highlightthickness=2,  # border thickness
            highlightbackground="white"  # white border for contrast
        )
        outer_frame.place(x=498, y=365, anchor="center", width=765, height=395)  # center screen

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            outer_frame,
            bg="#3A0F0A",  # match outer frame background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds movie cards)
        self.scroll_frame = tk.Frame(self.canvas, bg="#3A0F0A")
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")  # top-left anchor

        # Update scroll region automatically when content changes
        self.scroll_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mousewheel handling for scroll navigation (thread-safe)
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # Show loading indicator while fetching movies
        self.show_loading("Loading movies...")
        
        # LOAD MOVIES in background thread to prevent UI freezing
        threading.Thread(target=self.load_movies, daemon=True).start()

    def show_loading(self, text="Loading..."):
        """Display loading indicator while movie data loads"""
        for w in self.scroll_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create loading container with fixed dimensions
        container = tk.Frame(self.scroll_frame, bg="#3A0F0A", height=395, width=765)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Loading text with dots animation
        self.loading_label = tk.Label(
            container,
            text=text,
            bg="#3A0F0A",  # match background
            fg="#F5D7C6",  # light cream text color (cinema theme)
            font=("Consolas", 15, "italic")  # styled font
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")  # perfect center
        
        # Start simple dots animation
        self.loading_dots = 0  # animation counter
        self.animate_loading()  # begin animation loop

    def animate_loading(self):
        """Simple dots animation for loading indication"""
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            try:
                if self.loading_label.winfo_exists():  # check if widget still exists
                    dots = ["Loading movies", "Loading movies.", "Loading movies..", "Loading movies..."]
                    self.loading_label.config(text=dots[self.loading_dots % 4])  # cycle dots
                    self.loading_dots += 1  # increment counter
                    self.parent.after(300, self.animate_loading)  # schedule next frame
            except (tk.TclError, AttributeError):
                pass  # widget destroyed, stop animation

    # Mousewheel helper methods for scroll navigation
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_movies(self):
        """Load movie data from API in background thread"""
        try:
            response = requests.get(MOVIE_API_URL, timeout=10)  # 10-second timeout
            movies = response.json().get("data", [])  # extract movie data
            
            # Update UI in main thread (thread-safe)
            self.parent.after(0, lambda: self._display_movies(movies))
            
        except Exception as e:
            # Error handling in main thread
            self.parent.after(0, lambda: self._display_error(f"Error loading movies: {str(e)}"))

    def _display_movies(self, movies):
        """Display loaded movies in card format"""
        # Clear loading indicator
        self.loading_label = None
        
        for w in self.scroll_frame.winfo_children():
            w.destroy()  # clear existing content

        if not movies:  # no movies available
            container = tk.Frame(self.scroll_frame, bg="#3A0F0A", height=395, width=765)
            container.pack_propagate(False)
            container.pack()
            tk.Label(
                container,
                text="No movies available",
                bg="#3A0F0A",
                fg="#F5D7C6",  # theme color
                font=("Consolas", 14)
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # Arrange movies in 2-column grid layout
        col = 0
        row = 0
        for movie in movies:
            self.create_card(movie, row, col)  # create movie card
            col += 1
            if col == 2:  # Two cards per row
                col = 0
                row += 1

    def _display_error(self, message):
        """Display error message in scroll area"""
        self.loading_label = None  # clear loading animation
        
        for w in self.scroll_frame.winfo_children():
            w.destroy()  # clear existing content
            
        container = tk.Frame(self.scroll_frame, bg="#3A0F0A", height=395, width=765)
        container.pack_propagate(False)
        container.pack()
        
        # Error message with red text for visibility
        tk.Label(
            container,
            text=message,
            bg="#3A0F0A",
            fg="#ff6b6b",  # red error color
            font=("Consolas", 14)
        ).place(relx=0.5, rely=0.5, anchor="center")

    def create_card(self, movie, row, col):
        """Create individual movie card with poster and details"""
        attr = movie["attributes"]  # movie attributes

        # Card frame with fixed dimensions (cinema ticket style)
        card = tk.Frame(
            self.scroll_frame,
            bg="#7A1E16",  # medium red card background
            width=350,
            height=160
        )
        card.grid(row=row, column=col, padx=10, pady=10)  # grid positioning
        card.grid_propagate(False)  # maintain fixed size

        # Placeholder label while poster image loads
        poster_label = tk.Label(card, text="Loading...", bg="#7A1E16", fg="white", font=("Consolas", 12))
        poster_label.place(x=7, y=8, width=100, height=140)  # left side position

        # MOVIE TITLE (show immediately while poster loads)
        tk.Label(
            card,
            text=attr.get("title", "Unknown Movie"),
            font=("Consolas", 12, "bold"),
            fg="white",  # white text
            bg="#7A1E16",
            wraplength=230,  # prevent text overflow
            justify="left"  # left alignment
        ).place(x=120, y=10)

        # RELEASE DATE (show immediately)
        tk.Label(
            card,
            text=f"Release: {attr.get('release_date', 'Unknown')}",
            font=("Consolas", 10),
            fg="#F5D7C6",  # light cream color
            bg="#7A1E16"
        ).place(x=120, y=60)

        # RATING (show immediately)
        tk.Label(
            card,
            text=f"Rating: {attr.get('rating', 'N/A')}",
            font=("Consolas", 10),
            fg="#F5D7C6",
            bg="#7A1E16"
        ).place(x=120, y=80)

        # VIEW BUTTON (show immediately)
        tk.Button(
            card,
            text="View Movie",
            font=("Consolas", 11, "bold"),
            bg="#3A0F0A",  # dark red background
            fg="white",  # white text
            bd=0,  # no border
            command=lambda m=movie: self.app.click(lambda: self.app.show_movie_detail(m))
        ).place(x=120, y=110)

        # Load poster image in separate thread (prevents UI freezing)
        def load_image_thread():
            try:
                img_data = requests.get(attr.get("poster"), timeout=5).content  # fetch poster
                img = Image.open(io.BytesIO(img_data)).resize((100, 140))  # standard poster size
            except:
                # fallback to default movie placeholder
                img = Image.open(os.path.join(self.base_dir, "Assets", "no_image_movie.png")).resize((100, 140))
            
            # Pass PIL Image to main thread for Tkinter conversion
            poster_label.after(0, lambda i=img: update_label(i))

        def update_label(pil_image):
            """Update label with loaded image (called in main thread)"""
            # Create ImageTk.PhotoImage in main thread (Tkinter requirement)
            poster_img = ImageTk.PhotoImage(pil_image)
            if poster_label.winfo_exists():
                poster_label.configure(image=poster_img, text="")  # replace text with image
                poster_label.image = poster_img  # keep reference to prevent garbage collection

        # Start image loading in background thread
        threading.Thread(target=load_image_thread, daemon=True).start()

    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation       


class MovieDetailPage:
    """Page 6B: Detailed movie information display with poster and production details"""
    
    def __init__(self, parent, app, movie):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app
        # base directory for asset loading
        self.base_dir = app.base_dir
        # extract movie attributes from API data
        attr = movie["attributes"]

        # BACKGROUND GIF setup for detail page
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "movie_detail_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to movie archives)
        back_btn_path = os.path.join(
            self.base_dir, "Assets", "buttons", "back_arrow3.png"
        )
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(4, 4)  # 25% original size
        tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_movie_archives)  # navigate back
        ).place(x=10, y=10)  # top-left positioning

        # MOVIE POSTER display (left side of screen)
        self.poster_img = self.load_poster(attr.get("poster"))  # load poster from URL
        tk.Label(
            parent,
            image=self.poster_img,
            bg="#000000",  # black background
            relief="flat",  # no border relief
            bd=0  # no border
        ).place(x=60, y=172)  # centered vertically

        # CONTAINER for scrollable movie details
        container = tk.Frame(
            parent,
            bg="#000000",  # black background for cinema theme
            bd=2  # thin border
        )
        container.place(x=385, y=180, width=565, height=370)  # right side position

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            container,
            bg="#000000",  # match container background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds movie details)
        self.scroll_frame = tk.Frame(
            self.canvas,
            bg="#000000",  # black background
            padx=15,  # internal horizontal padding
            pady=15   # internal vertical padding
        )
        self.canvas.create_window(
            (0, 0),
            window=self.scroll_frame,
            anchor="nw"  # top-left anchor
        )

        # Auto-update scroll region when content changes
        self.scroll_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")  # update scrollable area
            )
        )

        # Mousewheel handling for scroll navigation
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # MOVIE DETAILS organized in vertical list format
        details = [
            ("Title", attr.get("title")),
            ("Release Date", attr.get("release_date")),
            ("Rating", attr.get("rating")),
            ("Running Time", attr.get("running_time")),
            ("Director", ", ".join(attr.get("directors", []))),  # join list with commas
            ("Producers", ", ".join(attr.get("producers", []))),
            ("Screenwriters", ", ".join(attr.get("screenwriters", []))),
            ("Editors", ", ".join(attr.get("editors", []))),
            ("Cinematography", ", ".join(attr.get("cinematographers", []))),
            ("Music Composers", ", ".join(attr.get("music_composers", []))),
            ("Distributors", ", ".join(attr.get("distributors", []))),
            ("Budget", attr.get("budget")),
            ("Box Office", attr.get("box_office")),
            ("Summary", attr.get("summary")),  # LAST (longest text)
        ]

        # Populate scroll frame with labels and values
        for label, value in details:
            # Attribute label (bold, left-aligned)
            tk.Label(
                self.scroll_frame,
                text=f"{label}:",
                font=("Consolas", 13, "bold"),  # bold for labels
                fg="#f2e6d8",  # light cream text color (cinema theme)
                bg="#000000",  # match background
                anchor="w"  # left alignment
            ).pack(anchor="w", pady=(8, 0))  # left-aligned, top padding

            # Attribute value (regular weight, with wrapping)
            tk.Label(
                self.scroll_frame,
                text=value or "Unknown",  # use "Unknown" for missing values
                font=("Consolas", 11),  # slightly smaller than labels
                fg="#e6b8a2",  # light brown highlight color
                bg="#000000",  # match background
                wraplength=500,  # prevent text overflow
                justify="left"  # left alignment
            ).pack(anchor="w", pady=(0, 6))  # left-aligned, bottom padding

    # Mousewheel helper methods for scroll navigation
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(
                int(-1 * (event.delta / 120)),  # scroll direction adjustment
                "units"
            )

    def load_poster(self, url):
        """Load movie poster from URL and resize for display"""
        img_data = requests.get(url, timeout=5).content  # fetch poster image
        img = Image.open(io.BytesIO(img_data)).resize((240, 365))  # standard poster size
        return ImageTk.PhotoImage(img)  # convert to Tkinter format
    
    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


class BookArchives:
    """Page 7A: Book catalog with scrollable card display and dual-view navigation"""
    
    def __init__(self, parent, app_ref):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app_ref
        # base directory for asset loading
        self.base_dir = self.app.base_dir

        # BACKGROUND GIF setup with animation
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "books_archive_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to map)
        back_btn_path = os.path.join(
            self.base_dir, "Assets", "buttons", "back_books.png"
        )
        self.back_books_img = tk.PhotoImage(file=back_btn_path).subsample(3, 3)  # 33% original size
        tk.Button(
            parent,
            image=self.back_books_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_map_select)  # navigate back to map
        ).place(x=10, y=10)  # top-left positioning

        # OUTER FRAME for scrollable card container (library shelf style)
        outer_frame = tk.Frame(
            parent,
            bg="#482d07",  # dark brown leather book theme
            highlightthickness=2,  # border thickness
            highlightbackground="#482d07"  # matching border color
        )
        outer_frame.place(
            x=500,  # horizontal center
            y=367,  # vertical center
            anchor="center",  # center alignment
            width=760,  # fixed width
            height=418   # fixed height
        )

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            outer_frame,
            bg="#482d07",  # match outer frame background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds book cards)
        self.scroll_frame = tk.Frame(self.canvas, bg="#482d07")
        self.canvas.create_window(
            (0, 0),
            window=self.scroll_frame,
            anchor="nw"  # top-left anchor
        )

        # AUTO SCROLL REGION configuration
        self.scroll_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")  # update scrollable area
            )
        )

        # MOUSEWHEEL handling for scroll navigation
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # Show loading indicator while fetching books
        self.show_loading("Loading books...")
        
        # LOAD BOOKS in background thread to prevent UI freezing
        threading.Thread(target=self.load_books, daemon=True).start()

    def show_loading(self, text="Loading..."):
        """Display loading indicator while book data loads"""
        for w in self.scroll_frame.winfo_children():
            w.destroy()  # clear existing content
        
        # Create loading container with fixed dimensions
        container = tk.Frame(self.scroll_frame, bg="#482d07", height=418, width=760)
        container.pack_propagate(False)  # maintain fixed size
        container.pack()
        
        # Loading text with dots animation
        self.loading_label = tk.Label(
            container,
            text=text,
            bg="#482d07",  # match background
            fg="#FFFFFF",  # white text for contrast
            font=("Consolas", 15, "italic")  # styled font
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")  # perfect center
        
        # Start simple dots animation
        self.loading_dots = 0  # animation counter
        self.animate_loading()  # begin animation loop

    def animate_loading(self):
        """Simple dots animation for loading indication"""
        if hasattr(self, 'loading_label') and self.loading_label is not None:
            try:
                if self.loading_label.winfo_exists():  # check if widget still exists
                    dots = ["Loading books", "Loading books.", "Loading books..", "Loading books..."]
                    self.loading_label.config(text=dots[self.loading_dots % 4])  # cycle dots
                    self.loading_dots += 1  # increment counter
                    self.parent.after(300, self.animate_loading)  # schedule next frame
            except (tk.TclError, AttributeError):
                pass  # widget destroyed, stop animation

    # MOUSEWHEEL helper methods for scroll navigation
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(
                int(-1 * (event.delta / 120)),  # scroll direction adjustment
                "units"
            )

    def load_books(self):
        """Load book data from API in background thread"""
        try:
            response = requests.get(BOOK_API_URL, timeout=10)  # 10-second timeout
            books = response.json().get("data", [])  # extract book data
            
            # Update UI in main thread (thread-safe)
            self.parent.after(0, lambda: self._display_books(books))
            
        except Exception as e:
            # Error handling in main thread
            self.parent.after(0, lambda: self._display_error(f"Error loading books: {str(e)}"))

    def _display_books(self, books):
        """Display loaded books in card format"""
        # Clear loading indicator
        self.loading_label = None
        
        for w in self.scroll_frame.winfo_children():
            w.destroy()  # clear existing content

        if not books:  # no books available
            container = tk.Frame(self.scroll_frame, bg="#482d07", height=418, width=760)
            container.pack_propagate(False)
            container.pack()
            tk.Label(
                container,
                text="No books available",
                bg="#482d07",
                fg="#FFFFFF",  # white text
                font=("Consolas", 14)
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # Arrange books in 2-column grid layout
        row = 0
        col = 0
        for book in books:
            self.create_card(book, row, col)  # create book card
            col += 1
            if col == 2:  # Two cards per row
                col = 0
                row += 1

    def _display_error(self, message):
        """Display error message in scroll area"""
        self.loading_label = None  # clear loading animation
        
        for w in self.scroll_frame.winfo_children():
            w.destroy()  # clear existing content
            
        container = tk.Frame(self.scroll_frame, bg="#482d07", height=418, width=760)
        container.pack_propagate(False)
        container.pack()
        
        # Error message with red text for visibility
        tk.Label(
            container,
            text=message,
            bg="#482d07",
            fg="#ff6b6b",  # red error color
            font=("Consolas", 14)
        ).place(relx=0.5, rely=0.5, anchor="center")

    def create_card(self, book, row, col):
        """Create individual book card with cover and dual-navigation buttons"""
        attr = book["attributes"]  # book attributes

        # Card frame with fixed dimensions (library book style)
        card = tk.Frame(
            self.scroll_frame,
            bg="#7d5319",  # medium brown card background
            width=350,
            height=160
        )
        card.grid(row=row, column=col, padx=10, pady=10)  # grid positioning
        card.grid_propagate(False)  # maintain fixed size

        # Placeholder label while cover image loads
        cover_label = tk.Label(card, text="Loading...", bg="#7d5319", fg="white", font=("Consolas", 12))
        cover_label.place(x=7, y=8, width=100, height=140)  # left side position

        # BOOK TITLE (show immediately while cover loads)
        tk.Label(
            card,
            text=attr.get("title", "Unknown Book"),
            font=("Consolas", 12, "bold"),
            fg="#FFFFFF",  # white text
            bg="#7d5319",
            wraplength=230,  # prevent text overflow
            justify="left"  # left alignment
        ).place(x=120, y=10)

        # AUTHOR (show immediately)
        tk.Label(
            card,
            text=f"Author: {attr.get('author', 'Unknown')}",
            font=("Consolas", 10),
            fg="#FFFFFF",  # white text
            bg="#7d5319"
        ).place(x=120, y=55)

        # RELEASE DATE (show immediately)
        tk.Label(
            card,
            text=f"Released: {attr.get('release_date', 'N/A')}",
            font=("Consolas", 10),
            fg="#FFFFFF",
            bg="#7d5319"
        ).place(x=120, y=75)

        # VIEW BOOK button (show details view)
        tk.Button(
            card,
            text="View Book",
            font=("Consolas", 10, "bold"),
            bg="#482d07",  # dark brown background
            fg="white",  # white text
            bd=0,  # no border
            activebackground="#7d5319",  # lighter brown when active
            command=lambda b=book: self.app.click(
                lambda: self.app.show_book_detail(b, "details"))  # details mode
        ).place(x=130, y=110)

        # VIEW CHAPTERS button (show chapters list)
        tk.Button(
            card,
            text="View Chapters",
            font=("Consolas", 10, "bold"),
            bg="#482d07",  # dark brown background
            fg="white",  # white text
            bd=0,  # no border
            activebackground="#7d5319",  # lighter brown when active
            command=lambda b=book: self.app.click(
                lambda: self.app.show_book_detail(b, "chapters"))  # chapters mode
        ).place(x=220, y=110)

        # Load cover image in separate thread (prevents UI freezing)
        def load_cover_thread():
            try:
                img_data = requests.get(attr.get("cover"), timeout=5).content  # fetch cover
                pil_image = Image.open(io.BytesIO(img_data)).resize((100, 140))  # standard book size
            except:
                # fallback to default book placeholder
                pil_image = Image.open(
                    os.path.join(self.base_dir, "Assets", "no_image_book.png")
                ).resize((100, 140))

            # Pass PIL Image to main thread for Tkinter conversion
            if cover_label.winfo_exists():
                cover_label.after(
                    0,
                    lambda img=pil_image: update_cover(img)
                )

        def update_cover(pil_image):
            """Update label with loaded cover (called in main thread)"""
            # Create ImageTk.PhotoImage in main thread (Tkinter requirement)
            cover_img = ImageTk.PhotoImage(pil_image)
            cover_label.configure(image=cover_img, text="")  # replace text with image
            cover_label.image = cover_img  # keep reference to prevent garbage collection

        # Start cover loading in background thread
        threading.Thread(target=load_cover_thread, daemon=True).start()

    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation
    
class BookDetailPage:
    """Page 7B: Book information display with toggle between details and chapters views"""
    
    def __init__(self, parent, app, book, mode):
        # parent window reference
        self.parent = parent
        # main application controller reference
        self.app = app
        # base directory for asset loading
        self.base_dir = app.base_dir
        # store book data for both views
        self.book = book
        # extract book attributes from API data
        self.attr = book["attributes"]
        # view mode: "details" or "chapters"
        self.mode = mode

        # BACKGROUND GIF setup for detail page
        gif_path = os.path.join(
            self.base_dir, "Assets", "backgrounds", "book_detail_bg.gif"
        )

        # initialize animated background
        self.bg_gif = AnimatedGIF(
            parent=self.parent,
            gif_path=gif_path,
            x=0,
            y=0
        )

        # Stretch GIF to full screen coverage
        self.bg_gif.label.place(
            x=0,
            y=0,
            relwidth=1,    # full width relative to parent
            relheight=1    # full height relative to parent
        )

        # BACK BUTTON setup (return to book archives)
        back_btn_path = os.path.join(self.base_dir, "Assets", "buttons", "back_arrow4.png")
        self.back_img = tk.PhotoImage(file=back_btn_path).subsample(4, 4)  # 25% original size
        tk.Button(
            parent,
            image=self.back_img,
            bd=0,  # no border
            bg="#000000",  # black background
            activebackground="#000000",  # same when active
            command=lambda: app.click(app.show_book_archives)  # navigate back
        ).place(x=10, y=10)  # top-left positioning

        # BOOK COVER display (left side of screen)
        self.cover_img = self.load_cover(self.attr.get("cover"))  # load cover from URL
        tk.Label(parent, image=self.cover_img, bg="#000000").place(x=93, y=200)  # centered vertically

        # CONTAINER for scrollable book information
        container = tk.Frame(
            parent,
            bg="#c5b499",  # parchment/paper color for book theme
            bd=2  # thin border
        )
        container.place(x=455, y=205, width=510, height=390)  # right side position

        # CANVAS widget for scrollable content area
        self.canvas = tk.Canvas(
            container,
            bg="#c5b499",  # match container background
            highlightthickness=0  # remove highlight border
        )
        self.canvas.pack(side="left", fill="both", expand=True)  # fill available space

        # SCROLLBAR for vertical navigation
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",  # vertical scrolling
            command=self.canvas.yview  # connect to canvas
        )
        scrollbar.pack(side="right", fill="y")  # right side, fill vertical space
        self.canvas.configure(yscrollcommand=scrollbar.set)  # two-way connection

        # SCROLLABLE FRAME inside canvas (holds book information)
        self.scroll_frame = tk.Frame(
            self.canvas,
            bg="#c5b499",  # parchment background
            padx=15,  # internal horizontal padding
            pady=15   # internal vertical padding
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")  # top-left anchor

        # Auto-update scroll region when content changes
        self.scroll_frame.bind(
            "<Configure>",  # triggered when frame size changes
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Mousewheel handling for scroll navigation
        self.canvas.bind("<Enter>", self._bind_mousewheel)  # enable when mouse enters
        self.canvas.bind("<Leave>", self._unbind_mousewheel)  # disable when mouse leaves

        # Show default content based on mode parameter
        if self.mode == "chapters":
            self.show_chapters()  # display chapter list
        else:
            self.show_details()   # display book details (default)

    # --- HELPER METHODS ---
    def clear_content(self):
        """Remove all widgets from scrollable frame"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll events"""
        if self.canvas and self.canvas.winfo_exists():
            # convert mouse delta to scroll units (Windows/Linux difference)
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_cover(self, url):
        """Load book cover from URL and resize for display"""
        img_data = requests.get(url, timeout=5).content  # fetch cover image
        img = Image.open(io.BytesIO(img_data)).resize((275, 396))  # standard book cover size
        return ImageTk.PhotoImage(img)  # convert to Tkinter format

    # --- VIEW METHODS ---
    def show_details(self):
        """Display detailed book information (publication details, summary)"""
        self.clear_content()  # clear previous content
        
        # Book details organized in vertical list
        details = [
            ("Title", self.attr.get("title")),
            ("Author", ", ".join(self.attr.get("authors", []))),  # join multiple authors
            ("Published", self.attr.get("release_date")),
            ("Genre", ", ".join(self.attr.get("genres", []))),  # join multiple genres
            ("Publisher", self.attr.get("publisher")),
            ("Language", self.attr.get("language")),
            ("Pages", self.attr.get("pages")),
            ("Summary", self.attr.get("summary")),  # longest text, placed last
        ]
        
        # Populate scroll frame with labels and values
        for label, value in details:
            # Attribute label (bold, left-aligned)
            tk.Label(
                self.scroll_frame, 
                text=f"{label}:", 
                font=("Consolas", 13, "bold"),
                fg="#000000",  # black text on parchment
                bg="#c5b499", 
                anchor="w"  # left alignment
            ).pack(anchor="w", pady=(8, 0))  # left-aligned, top padding

            # Attribute value (regular weight, with wrapping)
            tk.Label(
                self.scroll_frame, 
                text=value or "Unknown",  # use "Unknown" for missing values
                font=("Consolas", 11, "bold"),  # bold for readability
                fg="#000000",  # black text
                bg="#c5b499", 
                wraplength=455,  # prevent text overflow
                justify="left"  # left alignment
            ).pack(anchor="w", pady=(0, 6))  # left-aligned, bottom padding

    def show_chapters(self):
        """Display book chapters list with numbering"""
        self.clear_content()  # clear previous content

        # Chapter list header
        tk.Label(
            self.scroll_frame, 
            text="Chapters", 
            font=("Consolas", 15, "bold"),
            fg="#000000", 
            bg="#c5b499"
        ).pack(anchor="w", pady=(0, 10))  # left-aligned, bottom margin

        chapters = []
        try:
            # Fetch chapters for this specific book
            book_id = self.book["id"]
            response = requests.get(
                f"https://api.potterdb.com/v1/books/{book_id}/chapters", 
                timeout=5
            )
            chapters_data = response.json().get("data", [])
            
            # Extract chapter names or use default numbering
            chapters = [
                ch.get("attributes", {}).get("title", f"Chapter {i+1}") 
                for i, ch in enumerate(chapters_data)
            ]
        except:
            chapters = []  # empty list on error

        if not chapters:  # no chapters available
            tk.Label(
                self.scroll_frame, 
                text="No chapters available.", 
                font=("Consolas", 11, "bold"),
                fg="#000000", 
                bg="#c5b499"
            ).pack(anchor="w")
            return

        # Display numbered chapter list
        for i, chapter in enumerate(chapters, start=1):
            tk.Label(
                self.scroll_frame, 
                text=f"{i}. {chapter}",  # numbered list format
                font=("Consolas", 11, "bold"),
                fg="#000000", 
                bg="#c5b499", 
                wraplength=500,  # prevent text overflow
                justify="left"  # left alignment
            ).pack(anchor="w", pady=4)  # left-aligned, vertical spacing

    def destroy(self):
        """Cleanup method to stop animations when leaving page"""
        if hasattr(self, "bg_gif"):
            self.bg_gif.stop()  # stop background animation


# LAUNCH APPLICATION
if __name__ == "__main__":
    # Create main application window
    root = tk.Tk()  # initialize Tkinter root window
    
    # Instantiate main application controller
    app = GrimoireApp(root)  # create Grimoire application instance
    
    # Start main event loop (blocks until window closes)
    root.mainloop()  # begin GUI event processing