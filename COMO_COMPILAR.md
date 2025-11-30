# Como Compilar AudioBook para .exe

## Requisitos

1. **Python 3.10+** instalado
2. **PyInstaller** instalado

## Passo a Passo

### 1. Instalar dependências

```bash
pip install pyautogui pynput mss opencv-python numpy Pillow customtkinter pyinstaller
```

### 2. Compilar para .exe

Execute o comando na pasta do projeto:

```bash
pyinstaller --onefile --windowed --icon=fire_icon.png --add-data "magma_background.jpg;." --add-data "power_icon.png;." --add-data "fire_icon.png;." --add-data "trophy_icon.png;." --add-data "sword_icon.png;." --add-data "location_icon.png;." --add-data "target_icon.png;." --add-data "checkbox_on.png;." --add-data "checkbox_off.png;." --add-data "mana_icon.png;." --add-data "sd_icon.png;." --add-data "sd_rune_icon.png;." --add-data "explo_rune_icon.png;." --add-data "uh_rune_icon.png;." --add-data "settings_icon.png;." --add-data "auto_icon.png;." --add-data "tibia_key_icon.png;." --name "AudioBook" audiobook.py
```

### 3. Encontrar o .exe

O arquivo `AudioBook.exe` estará na pasta `dist/`

## Hotkeys Globais

- **Alt+F12**: Pausa TODAS as automações instantaneamente (funciona mesmo com o jogo em foco)

## Dicas

- Execute como Administrador para melhor compatibilidade com jogos
- O arquivo `audiobook_config.json` deve estar na mesma pasta do .exe
