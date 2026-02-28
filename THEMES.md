# GridShift Visual Themes

GridShift supports four distinct visual themes, each offering a unique aesthetic experience while maintaining full gameplay functionality.

## Available Themes

### 1. Default Theme (Classic)
The standard ASCII theme with clean, readable characters and colorful elements.

**Appearance:**
- Walls: `#` (white/bold)
- Player: `@` (yellow/bold)
- Boxes: `$` (cyan/bold)
- Goals: `.` (green)
- Box on goal: `*` (green/bold)
- Player on goal: `+` (yellow/bold)
- Borders: Single-line box drawing (`┌─┐│└─┘`)

**Usage:**
```bash
python -m gridshift.main --theme default
# or just
python -m gridshift.main
```

**Best for:** Maximum compatibility, clear readability

---

### 2. Neon Theme (Cyberpunk)
A vibrant cyberpunk aesthetic with bold colors and double-line borders.

**Appearance:**
- Walls: `█` (magenta/bold) - solid blocks
- Player: `@` (green/bold)
- Boxes: `[█]` (cyan/bold) - bracketed blocks
- Goals: `◆` (yellow) - diamond shapes
- Box on goal: `〚█〛` (cyan/bold)
- Player on goal: `⊕` (green/bold)
- Borders: Double-line box drawing (`╔═╗║╚═╝`)

**Usage:**
```bash
python -m gridshift.main --theme neon
```

**Best for:** Modern terminals, dark backgrounds, visual flair

**Color scheme:**
- Dark background
- Magenta walls (bold)
- Cyan boxes with brackets
- Yellow diamond goals
- Green player (bold)

---

### 3. Retro Theme (Matrix/Classic Terminal)
Everything rendered in green-on-black, reminiscent of old terminals and The Matrix.

**Appearance:**
- Walls: `▓` (green/bold) - dense hatch pattern
- Player: `@` (green/bold)
- Boxes: `□` (green/bold) - hollow squares
- Goals: `·` (green/bold) - small dots
- Box on goal: `■` (green/bold) - filled squares
- Player on goal: `⊕` (green/bold)
- Borders: Simple ASCII (`+-+|+-+`)

**Usage:**
```bash
python -m gridshift.main --theme retro
```

**Best for:** Nostalgia, monochrome displays, minimalist aesthetics

**Color scheme:**
- All elements in green on black background
- Everything rendered in bold for maximum visibility
- Matrix rain style aesthetic

---

### 4. Emoji Theme (Fun & Colorful)
Uses emoji characters for a playful, modern look. Note: Emojis are 2 characters wide in most terminals.

**Appearance:**
- Walls: 🧱 (brick)
- Player: 🏃 (runner)
- Boxes: 📦 (package)
- Goals: ⭐ (star)
- Box on goal: ✅ (check mark)
- Player on goal: 🎯 (target)
- Empty: `  ` (two spaces for proper alignment)
- Borders: Single-line box drawing (`┌─┐│└─┘`)

**Special tiles (for future expansion):**
- Ice: 🧊
- Teleporter: 🌀

**Usage:**
```bash
python -m gridshift.main --theme emoji
```

**Best for:** Modern terminals with good emoji support, casual play, screenshots

**Technical notes:**
- Uses double-width cells (2 characters per grid cell)
- Requires terminal with emoji support
- Grid rendering is automatically adjusted for 2-char width

---

## Implementation Details

### Architecture

The theme system is implemented through:

1. **`themes.py`**: Base `Theme` class and theme-specific subclasses
2. **`renderer.py`**: Uses theme objects for all visual rendering
3. **`main.py`**: Command-line argument for theme selection

### Adding Custom Themes

To create a new theme:

```python
from gridshift.themes import Theme, ThemeType

class MyCustomTheme(Theme):
    def __init__(self):
        super().__init__()
        # Override character mappings
        self.wall = '▓'
        self.player = '☺'
        self.box = '■'
        # etc.
        
        # Override cell width if needed (default is 1)
        self.cell_width = 1  # or 2 for wide characters
    
    def init_colors(self):
        """Override to define custom color scheme."""
        # Initialize curses color pairs
        # See existing themes for examples
        pass
```

Then register it in the `THEMES` dictionary:

```python
THEMES[ThemeType.CUSTOM] = MyCustomTheme
```

### Cell Width Handling

The renderer automatically adjusts grid layout based on `theme.cell_width`:
- `cell_width = 1`: Standard ASCII characters (1 terminal column per cell)
- `cell_width = 2`: Wide characters like emoji (2 terminal columns per cell)

Grid borders, centering, and spacing are all automatically calculated based on cell width.

---

## Testing

All themes have comprehensive test coverage:

```bash
# Test the theme system
python -m pytest tests/test_themes.py -v

# Test a specific theme
python -m pytest tests/test_themes.py::TestNeonTheme -v
```

---

## Terminal Compatibility

**Default, Neon, Retro:**
- Work on any terminal with basic Unicode support
- Tested on: macOS Terminal, iTerm2, GNOME Terminal, Windows Terminal

**Emoji:**
- Requires terminal with emoji rendering support
- Best results on: iTerm2, macOS Terminal, modern GNOME Terminal
- May have alignment issues on some terminals due to emoji width variations

---

## Future Theme Ideas

Potential themes for future expansion:
- **Minimal**: Ultra-clean, minimal colors, maximum simplicity
- **High Contrast**: For accessibility, maximum contrast ratios
- **Seasonal**: Holiday-themed variations (winter, halloween, etc.)
- **8-bit**: Pixel art style with block characters
- **Rainbow**: Each game element in a different vibrant color

---

## Contributing

Theme contributions are welcome! When adding a new theme:

1. Create a new class in `themes.py` inheriting from `Theme`
2. Override character mappings and colors
3. Add comprehensive tests in `tests/test_themes.py`
4. Update this documentation
5. Add the theme to the CLI argument choices in `main.py`
