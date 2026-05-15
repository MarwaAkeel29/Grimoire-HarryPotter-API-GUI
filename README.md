# ⚡ **The Marauder's Digital Grimoire**
### A Digital Wizarding World Encyclopedia Built with Python & Tkinter

**Harry Potter Grimoire** is an immersive, interactive desktop application that acts as a portal to the Wizarding World. Built using **Python**, **Tkinter**, and the **PotterDB API**, this app allows users to explore characters, spells, potions, movies, and books in a fully animated, audio-rich environment.

---

## 🔮 **Features**

### 🗺️ **Marauder's Map Navigation**
- Navigate through the application using an interactive **Marauder's Map** interface.
- Pin-based navigation system to jump between archives (Characters, Spells, Potions, Books, Movies).
- Animated transitions and lore-accurate backgrounds.

### 📚 **Extensive Knowledge Base (API Integration)**
Powered by the **PotterDB API**, the Grimoire fetches live data for:
- **🧙 Characters:** Search wizards/witches and **filter by Hogwarts House** (Gryffindor, Slytherin, etc.).
- **✨ Spells:** Browse incantations and effects, **filtered by Category** (Charm, Curse, Hex, etc.).
- **🧪 Potions:** Discover magical brews, **filtered by Difficulty** (Beginner, Advanced, etc.).
- **🎬 Movies:** View cast lists, budgets, box office scores, and posters.
- **📖 Books:** Read summaries and view full **Chapter Lists**.

### 🎨 **Immersive UI/UX**
- **Cinematic Backgrounds:** Custom `AnimatedGIF` engine supporting transparent and full-screen animations.
- **Themed Styling:** distinct color palettes for every section (e.g., Dark Red for Movies, Parchment for Books, Blue-Green for Spells).
- **Responsive Scrolling:** Smooth mousewheel navigation for card lists and details.
- **Asynchronous Loading:** Multi-threaded searching prevents UI freezing while fetching data from the API.

### 🔊 **Audio Atmosphere**
- **Background Music:** loops *John Williams' Harry Potter Theme* for ambiance.
- **Sound Effects:** Interactive click sounds for buttons and navigation.

---

## 🎯 **How to Use**

1. **Launch the App:** You will be greeted by the animated Title Screen.
2. **Enter the World:** Click **"Enter Map"** to view the Marauder's Map.
3. **Select a Destination:** Click a pin location (e.g., *Potion Library* or *Character Archives*).
4. **Search & Filter:**
   - Type a name (e.g., "Harry or Adrian") into the search bar.
   - Use the **Filter Button** to narrow results (e.g., select "Slytherin" to see only Slytherin characters).
5. **View Details:** Click on any card to open a detailed dossier containing images, attributes, and descriptions.
6. **Navigation:** Use the back arrows to return to the previous screen or the map.

---

## ⚙️ **Tech Stack**

- **Python 3.x**
- **Tkinter** – GUI Framework (Widgets, Canvas, Events)
- **Requests** – REST API Handling (Fetching data from PotterDB)
- **Pillow (PIL)** – Image processing (Resizing posters/character images, GIF handling)
- **Pygame** – Audio Engine (Background music & SFX)
- **Threading** – Concurrency (For non-blocking API calls)

---

## 📦 **Dependencies**

To run the **Harry Potter Grimoire**, you need the following Python libraries installed:

- **[Requests](https://pypi.org/project/requests/)** – For making HTTP requests to the PotterDB API.
- **[Pillow (PIL)](https://pypi.org/project/Pillow/)** – For loading, resizing images, and handling animated GIFs.
- **[Pygame](https://pypi.org/project/pygame/)** – For the sound engine (music and click effects).
- **Tkinter** – Standard Python GUI toolkit (usually pre-installed).

### **Installation**

You can install all the required external libraries by running this single command in your terminal or command prompt:

```bash
pip install requests pillow pygame
