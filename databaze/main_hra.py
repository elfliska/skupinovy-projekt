# ===================================================================
# PONG HRA - Kompletní komentáře ke každému řádku
# ===================================================================
# Importujeme funkce z našeho souboru db/models.py
# "get_connection" = otevře spojení s databází
# "create_tables"  = vytvoří tabulky v databázi pokud ještě neexistují
from db.models import get_connection, create_tables, get_now, get_or_create_player
import os

# pygame je knihovna pro tvorbu 2D her v Pythonu
import pygame

# time je vestavěná knihovna Pythonu pro práci s časem
# Použijeme ji na měření délky hry a detekci rychlosti nárazů
import time

# math je vestavěná matematická knihovna
# Použijeme ji pro funkci sin() - vytváří vlnový pohyb v animaci menu
import math

# Inicializace pygame - MUSÍ se zavolat jako první před čímkoli jiným
# Připraví všechny pygame moduly (zvuk, grafika, události...)
pygame.init()


# ===================================================================
# FONTY - různé velikosti textu
# ===================================================================
# pygame.font.Font(soubor_fontu, velikost_v_pixelech)
# 'freesansbold.ttf' je font zabudovaný přímo v pygame, vždy dostupný
font_large  = pygame.font.Font('freesansbold.ttf', 50)   # Velký font  - nadpisy (PONG, PAUZA)
font_medium = pygame.font.Font('freesansbold.ttf', 30)   # Střední font - tlačítka (START, UKONČIT)
font_small  = pygame.font.Font('freesansbold.ttf', 24)   # Malý font   - skóre, popisky
font_tiny   = pygame.font.Font('freesansbold.ttf', 16)   # Nejmenší font - nápovědy, verze hry


# ===================================================================
# BARVY - uložené jako trojice čísel (Red, Green, Blue)
# ===================================================================
# Každá složka může být 0-255. (0,0,0)=černá, (255,255,255)=bílá
BLACK       = (0,   0,   0)        # Čistě černá
WHITE       = (255, 255, 255)      # Čistě bílá
GREEN       = (0,   255, 120)      # Neonová zelená - levá pálka, tlačítko START
CYAN        = (0,   220, 255)      # Neonová azurová - nadpisy, ohraničení, logo
RED_NEON    = (255,  50,  80)      # Neonová červená - pravá pálka, tlačítko UKONČIT
YELLOW_NEON = (255, 220,   0)      # Žlutá - varování (zadejte jméno)
COLOR_BG    = (10,  10,  18)       # Skoro černá s modrým nádechem - pozadí hry
COLOR_BAR   = (18,  18,  32)       # Tmavě modro-šedá - horní a dolní lišta
COLOR_LINE  = (40,  40,  80)       # Tmavě fialová - ohraničení tlačítek, čáry

# Barvy tlačítka PAUZA / MENU (normální stav a stav po najetí myší)
BTN_MENU_NORMAL   = (30,  30,  60)   # Tmavě modrá
BTN_MENU_HOVER    = (50,  50, 110)   # Světlejší modrá při najetí myší

# Barvy tlačítka UKONČIT
BTN_QUIT_NORMAL   = (70,  15,  20)   # Tmavě červená
BTN_QUIT_HOVER    = (140,  25,  35)  # Světlejší červená při najetí myší

# Barvy tlačítka POKRAČOVAT
BTN_RESUME_NORMAL = (15,  60,  30)   # Tmavě zelená
BTN_RESUME_HOVER  = (25, 110,  55)   # Světlejší zelená při najetí myší


# ===================================================================
# NASTAVENÍ OKNA / OBRAZOVKY
# ===================================================================
WIDTH          = 900   # Šířka okna v pixelech
HEIGHT         = 600   # Výška okna v pixelech
TOP_BAR_HEIGHT = 60    # Výška horní lišty (kde je logo a tlačítko PAUZA)

# Vytvoříme herní okno zadané velikosti
# pygame.display.set_mode vrátí "surface" = plocha na které kreslíme
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Nastavíme název okna (vidět v záhlaví / na taskbaru)
pygame.display.set_caption("PONG")

# Clock objekt slouží k omezení FPS (snímků za sekundu)
# Bez toho by hra běžela co nejrychleji = nestabilní rychlost
clock = pygame.time.Clock()

# Cílový počet snímků za sekundu
# 60 FPS = hra se překreslí 60x za sekundu = plynulý pohyb
FPS = 60


# ===================================================================
# POMOCNÉ FUNKCE PRO KRESLENÍ
# ===================================================================

def draw_neon_rect(surface, color, rect, radius=8, glow=True):
    """
    Nakreslí obdélník s volitelným 'glow' (záře) efektem.

    surface = plocha na které kreslíme (vždy 'screen')
    color   = barva obdélníku jako (R, G, B)
    rect    = pygame.Rect objekt (x, y, šířka, výška)
    radius  = zaoblení rohů v pixelech
    glow    = True/False, zda přidat záři kolem
    """
    if glow:
        # Vytvoříme dočasnou průhlednou plochu o trochu větší než obdélník
        # pygame.SRCALPHA = plocha podporuje průhlednost (alpha kanál)
        glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)

        # Barva záře = stejná barva ale s průhledností 60 (0=neviditelná, 255=plná)
        glow_color = (*color, 60)  # *color rozbalí (R,G,B) a přidáme 4. hodnotu = alpha

        # Nakreslíme záři na dočasnou plochu (posunutou o 10px kvůli centování)
        pygame.draw.rect(glow_surf, glow_color,
                         pygame.Rect(10, 10, rect.width, rect.height), border_radius=radius + 4)

        # Přilepíme záři na hlavní plochu (o 10px vlevo a nahoru = záře přesahuje)
        surface.blit(glow_surf, (rect.x - 10, rect.y - 10))

    # Nakreslíme samotný obdélník se zaoblenými rohy
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_button(surface, rect, text, font, normal_color, hover_color, mouse_pos,
                text_color=WHITE, radius=8, border_color=None):
    """
    Nakreslí interaktivní tlačítko a vrátí True pokud je myš nahoře.

    surface      = plocha na které kreslíme
    rect         = poloha a velikost tlačítka (pygame.Rect)
    text         = text zobrazený na tlačítku
    font         = font pro text
    normal_color = barva tlačítka v klidovém stavu
    hover_color  = barva tlačítka když je myš nahoře
    mouse_pos    = aktuální pozice myši (x, y)
    text_color   = barva textu
    radius       = zaoblení rohů
    border_color = barva ohraničení (None = bez ohraničení)
    """
    # collidepoint vrátí True pokud je bod (myš) uvnitř obdélníku
    hovered = rect.collidepoint(mouse_pos)

    # Vybereme barvu podle toho jestli je myš nahoře
    color = hover_color if hovered else normal_color

    # Nakreslíme tělo tlačítka (se září jen při hover)
    draw_neon_rect(surface, color, rect, radius=radius, glow=hovered)

    # Pokud máme barvu ohraničení, nakreslíme tenký rámeček (width=2 = jen obrys)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=radius)

    # Vykreslíme text tlačítka
    label = font.render(text, True, text_color)  # True = antialiasing (hladší text)

    # Vycentrujeme text uvnitř tlačítka matematicky
    # (šířka tlačítka - šířka textu) / 2 = odsazení zleva pro vycentrování
    surface.blit(label, (rect.x + (rect.width  - label.get_width())  // 2,
                         rect.y + (rect.height - label.get_height()) // 2))

    # Vrátíme stav hover - hodí se pokud chceme vědět jestli uživatel najel myší
    return hovered


def draw_dashed_center_line(surface):
    """Nakreslí přerušovanou čáru uprostřed hřiště (jako v klasickém Pongu)."""
    dash_h = 15   # Délka jedné čárky v pixelech
    gap_h  = 10   # Mezera mezi čárkami v pixelech
    x      = WIDTH // 2 - 1   # X pozice = přesně uprostřed obrazovky
    y      = TOP_BAR_HEIGHT   # Začínáme pod horní lištou

    # Kreslíme čárky dokud nedosáhneme dolní lišty
    while y < HEIGHT - 50:
        # min() zajistí, že poslední čárka nepřesáhne dolní hranu
        pygame.draw.rect(surface, COLOR_LINE, (x, y, 3, min(dash_h, HEIGHT - 50 - y)))
        y += dash_h + gap_h   # Posuneme se o délku čárky + mezeru


def draw_score_bar(surface, player_name, geek1Score, geek2Score, mode):
    """Nakreslí dolní lištu se jmény hráčů a jejich skóre."""

    # Tmavé pozadí dolní lišty
    pygame.draw.rect(surface, COLOR_BAR, (0, HEIGHT - 50, WIDTH, 50))

    # Tenká svítící čára na horním okraji lišty (vizuální oddělení od hřiště)
    pygame.draw.line(surface, CYAN, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 1)

    # Skóre hráče 1 (levý) - zobrazí jeho zadané jméno
    p1_text = font_small.render(f"{player_name}:  {geek1Score}", True, GREEN)

    # Jméno soupeře záleží na módu hry
    p2_label = "BOT" if mode == "BOT" else "Hráč 2"
    p2_text  = font_small.render(f"{p2_label}:  {geek2Score}", True, RED_NEON)

    # Hráč 1 vlevo, hráč 2 vpravo
    surface.blit(p1_text, (20, HEIGHT - 35))
    surface.blit(p2_text, (WIDTH - p2_text.get_width() - 20, HEIGHT - 35))

    # Malý nápis "VS" přesně uprostřed dolní lišty
    mid = font_tiny.render("VS", True, (100, 100, 160))
    surface.blit(mid, (WIDTH // 2 - mid.get_width() // 2, HEIGHT - 32))


def draw_top_bar(surface, pause_button, mouse):
    """Nakreslí horní lištu s logem hry a tlačítkem PAUZA."""

    # Tmavé pozadí horní lišty
    pygame.draw.rect(surface, COLOR_BAR, (0, 0, WIDTH, TOP_BAR_HEIGHT))

    # Tenká čára na spodním okraji lišty
    pygame.draw.line(surface, CYAN, (0, TOP_BAR_HEIGHT), (WIDTH, TOP_BAR_HEIGHT), 1)

    # Logo "PONG" vlevo v liště, svisle vycentrované
    logo = font_medium.render("PONG", True, CYAN)
    surface.blit(logo, (20, TOP_BAR_HEIGHT // 2 - logo.get_height() // 2))

    # Tlačítko PAUZA uprostřed horní lišty
    # "II" jsou dvě svislé čárky = klasická ikona pauzy
    draw_button(surface, pause_button, "II  PAUZA", font_tiny,
                BTN_MENU_NORMAL, BTN_MENU_HOVER, mouse,
                text_color=WHITE, radius=6, border_color=COLOR_LINE)


def draw_pause_overlay(surface, player_name, geek1Score, geek2Score, mode,
                       resume_button, menu_button, quit_button, mouse):
    """
    Nakreslí poloprůhledné překrytí celé obrazovky při pauze.
    Zobrazí panel s tlačítky: POKRAČOVAT, MENU, UKONČIT.
    """
    # Vytvoříme průhlednou plochu přes celou obrazovku
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 5, 15, 200))   # Téměř černá s průhledností 200/255
    surface.blit(overlay, (0, 0))   # Přilepíme přes celou obrazovku

    # Tmavý panel uprostřed obrazovky (pozadí pro tlačítka)
    panel_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 170, 320, 340)
    pygame.draw.rect(surface, (20, 20, 45), panel_rect, border_radius=16)

    # Svítící rámeček kolem panelu (width=2 = jen obrys, ne výplň)
    pygame.draw.rect(surface, CYAN, panel_rect, width=2, border_radius=16)

    # Nadpis "PAUZA" vycentrovaný nad panelem
    pause_title = font_large.render("PAUZA", True, CYAN)
    surface.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2,
                               HEIGHT // 2 - 155))

    # Zobrazíme aktuální skóre uvnitř pause panelu
    score_txt = font_small.render(
        f"{player_name}  {geek1Score} : {geek2Score}  {'BOT' if mode == 'BOT' else 'Hráč 2'}",
        True, WHITE
    )
    surface.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2,
                             HEIGHT // 2 - 80))

    # Tlačítko POKRAČOVAT - zelené, vrátí hru do chodu
    draw_button(surface, resume_button, "  POKRAČOVAT", font_small,
                BTN_RESUME_NORMAL, BTN_RESUME_HOVER, mouse,
                text_color=GREEN, radius=10, border_color=(0, 80, 40))

    # Tlačítko MENU - modré, vrátí do hlavního menu
    draw_button(surface, menu_button, "  MENU", font_small,
                BTN_MENU_NORMAL, BTN_MENU_HOVER, mouse,
                text_color=CYAN, radius=10, border_color=(30, 30, 80))

    # Tlačítko UKONČIT - červené, zavře celou aplikaci
    draw_button(surface, quit_button, "  UKONČIT HRU", font_small,
                BTN_QUIT_NORMAL, BTN_QUIT_HOVER, mouse,
                text_color=RED_NEON, radius=10, border_color=(80, 15, 20))


# ===================================================================
# TŘÍDA STRIKER - Pálka hráče
# ===================================================================
class Striker:
    """
    Reprezentuje jednu pálku (levou nebo pravou).
    Každý hráč má svůj vlastní objekt Striker.
    """

    def __init__(self, posx, posy, width, height, speed, color):
        """
        Konstruktor - zavolá se při vytvoření objektu pomocí Striker(...).

        posx   = vodorovná pozice pálky (X souřadnice)
        posy   = svislá pozice pálky (Y souřadnice) - přičteme TOP_BAR_HEIGHT
        width  = šířka pálky v pixelech
        height = výška pálky v pixelech
        speed  = rychlost pohybu (pixelů za snímek)
        color  = barva pálky jako (R, G, B)
        """
        self.posx   = posx                    # Uložíme X pozici
        self.posy   = posy + TOP_BAR_HEIGHT   # Y posunutá pod horní lištu
        self.width  = width                   # Uložíme šířku
        self.height = height                  # Uložíme výšku
        self.speed  = speed                   # Uložíme rychlost
        self.color  = color                   # Uložíme barvu

        # pygame.Rect je obdélník - slouží pro detekci kolizí a kreslení
        # parametry: (x, y, šířka, výška)
        self.geekRect = pygame.Rect(posx, self.posy, width, height)

    def display(self):
        """Vykreslí pálku na obrazovku s glow efektem."""

        # --- Glow (záře) efekt ---
        # Vytvoříme průhlednou plochu o 12px větší než pálka
        glow_surf = pygame.Surface((self.width + 12, self.height + 12), pygame.SRCALPHA)

        # Barva záře = barva pálky s nízkou průhledností (50/255)
        glow_color = (*self.color, 50)  # Rozbalíme barvu a přidáme alpha hodnotu

        # Nakreslíme záři na dočasnou plochu (posunutou o 6px od okraje)
        pygame.draw.rect(glow_surf, glow_color,
                         pygame.Rect(6, 6, self.width, self.height), border_radius=4)

        # Přilepíme záři na herní plochu (o 6px vlevo a nahoru = záře přesahuje)
        screen.blit(glow_surf, (self.posx - 6, self.posy - 6))

        # --- Samotná pálka ---
        # border_radius=4 = mírně zaoblené rohy
        pygame.draw.rect(screen, self.color, self.geekRect, border_radius=4)

    def update(self, yFac):
        """
        Pohne pálkou nahoru nebo dolů.

        yFac = směrový faktor:
               -1 = pohyb nahoru (Y souřadnice klesá)
                0 = stůj
               +1 = pohyb dolů (Y souřadnice roste)
        """
        # Změníme Y pozici: rychlost * směr
        self.posy += self.speed * yFac

        # Zabráníme pálce vyjet ven z hrací plochy
        if self.posy <= TOP_BAR_HEIGHT:               # Narazila na horní hranici
            self.posy = TOP_BAR_HEIGHT                # Zastavíme ji přesně na hranici
        elif self.posy + self.height >= HEIGHT - 50:  # Narazila na dolní hranici
            self.posy = HEIGHT - 50 - self.height     # Zastavíme ji přesně na hranici

        # Aktualizujeme Rect na novou pozici (potřebné pro detekci kolizí)
        self.geekRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def getRect(self):
        """Vrátí pygame.Rect pálky - používáme pro detekci kolizí s míčkem."""
        return self.geekRect


# ===================================================================
# TŘÍDA BALL - Míček
# ===================================================================
class Ball:
    """
    Reprezentuje míček. Pohybuje se diagonálně a odráží se od stěn a pálek.
    """

    def __init__(self, posx, posy, radius, speed, color):
        """
        Konstruktor míčku.

        posx   = počáteční X pozice
        posy   = počáteční Y pozice (přičteme TOP_BAR_HEIGHT)
        radius = poloměr míčku v pixelech
        speed  = rychlost míčku (pixelů za snímek)
        color  = barva míčku
        """
        self.posx          = posx                    # X pozice středu míčku
        self.posy          = posy + TOP_BAR_HEIGHT   # Y pozice středu míčku
        self.radius        = radius                  # Poloměr
        self.speed         = speed                   # Aktuální rychlost
        self.initial_speed = speed                   # Původní rychlost pro reset po gólu
        self.color         = color                   # Barva míčku
        self.xFac          = 1                       # Směr X: +1=doprava, -1=doleva
        self.yFac          = -1                      # Směr Y: -1=nahoru, +1=dolů
        self.firstTime     = 1                       # Ochrana proti dvojitému skóre
        self.last_hit_time = 0                       # Čas posledního odrazu od pálky
        self.trail         = []                      # Seznam posledních pozic pro trail efekt

    def display(self):
        """Vykreslí míček i s ocasem (trail) a září (glow)."""

        # --- Trail efekt (ocas za míčkem) ---
        # self.trail je seznam starých pozic [(x1,y1), (x2,y2), ...]
        for i, (tx, ty) in enumerate(self.trail):
            # Čím starší pozice, tím průhlednější a menší
            alpha  = int(180 * (i / max(len(self.trail), 1)))    # Průhlednost 0-180
            radius = max(1, self.radius - (len(self.trail) - i)) # Poloměr se zmenšuje

            # Průhledná plocha pro jeden bod ocasu
            trail_surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*self.color, alpha), (radius + 1, radius + 1), radius)
            screen.blit(trail_surf, (tx - radius - 1, ty - radius - 1))

        # --- Glow kolem míčku ---
        # Průhledná plocha 4x větší než míček
        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 40),        # 40/255 průhlednost
                           (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow_surf, (self.posx - self.radius * 2, self.posy - self.radius * 2))

        # --- Samotný míček ---
        pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        """
        Posune míček a zkontroluje kolize se stěnami.
        Vrací: 0 = nic, 1 = levý hráč dal gól, -1 = pravý hráč dal gól.
        """
        # Uložíme aktuální pozici do ocasu (pro trail efekt)
        self.trail.append((self.posx, self.posy))

        # Uchováváme max 8 posledních pozic (kratší = kratší ocas)
        if len(self.trail) > 8:
            self.trail.pop(0)   # Smažeme nejstarší pozici

        # Posuneme míček o rychlost * směr na obou osách
        self.posx += self.speed * self.xFac   # Vodorovný pohyb
        self.posy += self.speed * self.yFac   # Svislý pohyb

        # Odraz od horní stěny nebo dolní hranice hrací plochy
        if self.posy - self.radius <= TOP_BAR_HEIGHT or self.posy + self.radius >= HEIGHT - 50:
            self.yFac *= -1   # Otočíme svislý směr (-1 na +1 nebo +1 na -1)

            # Opravíme pozici aby míček nevyjel mimo hranice
            if self.posy - self.radius < TOP_BAR_HEIGHT:
                self.posy = TOP_BAR_HEIGHT + self.radius   # Posuneme zpět dovnitř
            if self.posy + self.radius > HEIGHT - 50:
                self.posy = HEIGHT - 50 - self.radius      # Posuneme zpět dovnitř

        # Detekce gólu: míček vyjel z levé strany obrazovky
        if self.posx <= 0 and self.firstTime:
            self.firstTime = 0   # Zabráníme dvojitému skóre
            return 1             # Pravý hráč (geek2) boduje

        # Detekce gólu: míček vyjel z pravé strany obrazovky
        elif self.posx >= WIDTH and self.firstTime:
            self.firstTime = 0   # Zabráníme dvojitému skóre
            return -1            # Levý hráč (geek1) boduje

        return 0   # Žádný gól

    def reset(self):
        """Resetuje míček na střed po gólu."""
        self.posx          = WIDTH // 2                            # Střed X
        self.posy          = (HEIGHT - 50 + TOP_BAR_HEIGHT) // 2  # Střed Y hrací plochy
        self.xFac         *= -1    # Otočíme vodorovný směr (míček letí na druhou stranu)
        self.firstTime     = 1     # Povolíme znovu detekci gólu
        self.speed         = self.initial_speed   # Resetujeme rychlost na počáteční
        self.last_hit_time = 0     # Resetujeme čas posledního odrazu
        self.trail         = []    # Vymažeme ocas

    def hit(self):
        """
        Zavolá se při odrazu od pálky.
        Otočí vodorovný směr a trochu zrychlí míček.
        """
        current_time = time.time()   # Aktuální čas v sekundách

        # Ochrana: pokud od posledního odrazu uplynulo méně než 0.1s, ignorujeme
        # Zabraňuje "zaseknutí" míčku uvnitř pálky (dvojitý odraz)
        if current_time - self.last_hit_time < 0.1:
            return

        self.xFac         *= -1    # Otočíme vodorovný směr
        self.speed        += 0.5   # Zrychlíme o půl pixelu za snímek

        if self.speed > 15:        # Maximální rychlost = 15, aby hra nebyla nehratelná
            self.speed = 15

        self.last_hit_time = current_time   # Uložíme čas tohoto odrazu

    def getRect(self):
        """Vrátí pygame.Rect míčku pro detekci kolizí s pálkami."""
        # Obdélník ohraničující kruh (levý horní roh + šířka/výška = průměr)
        return pygame.Rect(self.posx - self.radius, self.posy - self.radius,
                           self.radius * 2, self.radius * 2)


# ===================================================================
# FUNKCE MENU - Hlavní menu hry
# ===================================================================
def menu():
    """
    Zobrazí hlavní menu. Hráč zadá jméno a vybere herní mód.
    Vrátí: (mode, player_name) = ("PVP" nebo "BOT", jméno hráče)
    """
    player_name  = ""     # Jméno hráče začíná prázdné
    input_active = False  # Input box zatím není aktivní (nepíšeme do něj)
    mode         = "PVP"  # Výchozí herní mód

    # Barvy pro input box
    COLOR_ACTIVE  = CYAN           # Modré ohraničení když píšeme
    COLOR_PASSIVE = (60, 60, 90)   # Tmavě modré ohraničení v klidu
    COLOR_BTN     = (25, 25, 50)   # Tmavé pozadí nevybraného tlačítka
    COLOR_BTN_SEL = (40, 40, 90)   # Světlejší pozadí vybraného tlačítka

    tick = 0   # Čítač snímků - používáme pro animace (blikání kurzoru, vlny)

    while True:   # Nekonečná smyčka menu - běží dokud hráč nestiskne START
        tick += 1   # Zvýšíme čítač každý snímek

        # Vyplníme celou obrazovku barvou pozadí
        screen.fill(COLOR_BG)

        # --- Animované pozadí (svislé barevné pruhy s vlnovým pohybem) ---
        for i in range(0, WIDTH, 40):   # Každých 40 pixelů nakreslíme svislou čáru
            # math.sin() vrací hodnotu mezi -1 a +1 (tvar vlny)
            # tick * 0.02 = časová složka (animace se pohybuje v čase)
            # i * 0.01 = prostorová složka (různé fáze pro různé čáry = vlna)
            alpha = int(15 + 10 * math.sin((tick * 0.02) + i * 0.01))
            pygame.draw.line(screen, (0, alpha, alpha * 2), (i, 0), (i, HEIGHT))

        # --- Nadpis "PONG" s glow efektem ---
        # Nejdřív nakreslíme tmavší kopii mírně posunutou = imitace záře/stínu
        title_glow = font_large.render("PONG", True, (0, 80, 100))
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:   # 4 směry = záře ze všech stran
            screen.blit(title_glow, (WIDTH // 2 - title_glow.get_width() // 2 + dx, 38 + dy))

        # Pak nakreslíme ostrý světlý nápis (překryje tmavé kopie)
        title = font_large.render("PONG", True, CYAN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 38))

        # Podtitul s verzí hry
        sub = font_tiny.render("CLASSIC ARCADE  •  v0.2", True, (80, 80, 130))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 98))

        # Varování pokud hráč ještě nezadal jméno
        if player_name == "":
            warn = font_tiny.render("Zadejte jméno pro start hry", True, YELLOW_NEON)
            screen.blit(warn, (WIDTH // 2 - warn.get_width() // 2, 128))

        # --- Popisek nad input boxem ---
        label = font_small.render("Jméno hráče:", True, (160, 160, 210))
        screen.blit(label, (WIDTH // 2 - 150, 158))

        # --- Input box (textové pole pro zadání jména) ---
        input_rect = pygame.Rect(WIDTH // 2 - 150, 188, 300, 44)
        border_c   = CYAN if input_active else COLOR_PASSIVE   # Barva rámu záleží na aktivitě

        pygame.draw.rect(screen, (15, 15, 30), input_rect, border_radius=8)        # Tmavé pozadí pole
        pygame.draw.rect(screen, border_c, input_rect, width=2, border_radius=8)   # Barevný rámeček

        # Zobrazíme aktuálně zadané jméno uvnitř pole
        name_text = font_small.render(player_name, True, WHITE)
        screen.blit(name_text, (input_rect.x + 10, input_rect.y + 10))

        # Blikající textový kurzor (jen když je input aktivní)
        # (tick // 30) % 2 == 0 přepíná mezi True/False každých 30 snímků = blikání
        if input_active and (tick // 30) % 2 == 0:
            cursor_x = input_rect.x + 12 + name_text.get_width()   # Pozice za posledním písmenem
            pygame.draw.line(screen, CYAN,
                             (cursor_x, input_rect.y + 8),
                             (cursor_x, input_rect.y + 36), 2)   # Svislá čárka = kurzor

        # --- Popisek nad tlačítky herního módu ---
        mode_label = font_small.render("Režim hry:", True, (160, 160, 210))
        screen.blit(mode_label, (WIDTH // 2 - 150, 250))

        # Aktuální pozice myši (potřebujeme pro hover efekty)
        mouse = pygame.mouse.get_pos()

        # --- Tlačítko PVP (Hráč vs Hráč) - levá polovina ---
        pvp_button = pygame.Rect(WIDTH // 2 - 150, 284, 142, 40)
        pvp_color  = COLOR_BTN_SEL if mode == "PVP" else COLOR_BTN   # Zvýraznění vybraného
        pvp_border = CYAN if mode == "PVP" else COLOR_PASSIVE
        pygame.draw.rect(screen, pvp_color, pvp_button, border_radius=8)
        pygame.draw.rect(screen, pvp_border, pvp_button, width=2, border_radius=8)
        pvp_t = font_small.render("Hráč vs Hráč", True, CYAN if mode == "PVP" else WHITE)
        screen.blit(pvp_t, (pvp_button.x + (pvp_button.width - pvp_t.get_width()) // 2,
                            pvp_button.y + 8))

        # --- Tlačítko BOT (Hráč vs Bot) - pravá polovina ---
        bot_button = pygame.Rect(WIDTH // 2 + 8, 284, 142, 40)
        bot_color  = COLOR_BTN_SEL if mode == "BOT" else COLOR_BTN
        bot_border = CYAN if mode == "BOT" else COLOR_PASSIVE
        pygame.draw.rect(screen, bot_color, bot_button, border_radius=8)
        pygame.draw.rect(screen, bot_border, bot_button, width=2, border_radius=8)
        bot_t = font_small.render("Hráč vs Bot", True, CYAN if mode == "BOT" else WHITE)
        screen.blit(bot_t, (bot_button.x + (bot_button.width - bot_t.get_width()) // 2,
                            bot_button.y + 8))

        # --- Tlačítko START ---
        start_button = pygame.Rect(WIDTH // 2 - 110, 350, 220, 52)
        if player_name == "":
            # Šedé neaktivní tlačítko dokud není zadáno jméno
            pygame.draw.rect(screen, (30, 30, 30), start_button, border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), start_button, width=2, border_radius=10)
            st = font_medium.render("START", True, (80, 80, 80))   # Šedý text
        else:
            # Zelené aktivní tlačítko
            hover_start = start_button.collidepoint(mouse)           # Je myš nahoře?
            sc = (0, 170, 80) if hover_start else (0, 130, 55)       # Světlejší při hover
            draw_neon_rect(screen, sc, start_button, radius=10, glow=hover_start)
            pygame.draw.rect(screen, GREEN, start_button, width=2, border_radius=10)
            st = font_medium.render("  START", True, WHITE)

        # Vycentrujeme text tlačítka START uvnitř tlačítka
        screen.blit(st, (start_button.x + (start_button.width  - st.get_width())  // 2,
                         start_button.y + (start_button.height - st.get_height()) // 2))

        # --- Tlačítko HISTORIE ---
        history_button = pygame.Rect(WIDTH // 2 - 110, 418, 220, 44)
        hover_hist = history_button.collidepoint(mouse)
        hc = BTN_MENU_HOVER if hover_hist else BTN_MENU_NORMAL
        draw_neon_rect(screen, hc, history_button, radius=10, glow=hover_hist)
        pygame.draw.rect(screen, COLOR_LINE, history_button, width=2, border_radius=10)
        ht = font_medium.render("HISTORIE", True, CYAN)
        screen.blit(ht, (history_button.x + (history_button.width  - ht.get_width())  // 2,
                         history_button.y + (history_button.height - ht.get_height()) // 2))

        # --- Tlačítko UKONČIT ---
        quit_button = pygame.Rect(WIDTH // 2 - 110, 476, 220, 44)
        hover_quit  = quit_button.collidepoint(mouse)                # Je myš nahoře?
        qc = (160, 20, 30) if hover_quit else (110, 15, 20)          # Barva záleží na hover
        draw_neon_rect(screen, qc, quit_button, radius=10, glow=hover_quit)
        pygame.draw.rect(screen, RED_NEON, quit_button, width=2, border_radius=10)
        qt = font_medium.render("UKONČIT", True, WHITE)
        screen.blit(qt, (quit_button.x + (quit_button.width  - qt.get_width())  // 2,
                         quit_button.y + (quit_button.height - qt.get_height()) // 2))

        # --- Nápověda k ovládání dole na obrazovce ---
        hint = font_tiny.render(
            "W/S  -  levá pálka       UP/DOWN  -  pravá pálka       ESC  -  pauza",
            True, (60, 60, 100))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

        # --- Zpracování událostí (vstup od uživatele) ---
        for event in pygame.event.get():

            # Uživatel kliknul na X (zavřít okno)
            if event.type == pygame.QUIT:
                pygame.quit()   # Ukončíme pygame
                quit()          # Ukončíme Python program

            # Uživatel kliknul myší
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True    # Klik do input boxu = začni psát
                else:
                    input_active = False   # Klik jinam = přestaň psát

                if pvp_button.collidepoint(event.pos):   # Klik na tlačítko PVP
                    mode = "PVP"
                if bot_button.collidepoint(event.pos):   # Klik na tlačítko BOT
                    mode = "BOT"
                if start_button.collidepoint(event.pos) and player_name != "":
                    return mode, player_name   # Spusť hru - vrátíme data do volajícího kódu
                if history_button.collidepoint(event.pos):
                    show_history()   # Zobraz historii, po návratu jsme zpět v menu
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    quit()

            # Uživatel zmáčkl klávesu (jen pokud je input box aktivní)
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]   # Smažeme poslední znak jména
                elif event.key == pygame.K_RETURN and player_name != "":
                    return mode, player_name   # Enter = potvrzení jména = start hry
                elif len(player_name) < 12:   # Maximální délka jména = 12 znaků
                    player_name += event.unicode   # Přidáme napsaný znak na konec

        # Překreslíme obrazovku (zobrazíme vše co jsme nakreslili v tomto snímku)
        pygame.display.update()

        # Počkáme aby byl snímek přesně 1/60 sekundy dlouhý = stabilní 60 FPS
        clock.tick(FPS)


# ===================================================================
# FUNKCE SAVE_RESULT - Uložení výsledku do databáze
# ===================================================================
def save_result(username, geek1Score, geek2Score, hits, game_mode, duration):
    p2_name = "BOT" if game_mode == "BOT" else "Hráč 2"

    conn = get_connection()
    cur = conn.cursor()

    # Zajistíme existenci hráčů v tabulce player
    player1_id = get_or_create_player(cur, username)
    player2_id = get_or_create_player(cur, p2_name)

    # Určíme vítěze (jako player_id)
    if geek1Score > geek2Score:
        winner_id = player1_id
        winner_name = username
    elif geek2Score > geek1Score:
        winner_id = player2_id
        winner_name = p2_name
    else:
        winner_id = None
        winner_name = "Remíza"

    # Vložíme záznam hry
    cur.execute("""
        INSERT INTO game (played_at, duration_seconds, game_mode, player1_id, player2_id, winner_player)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (get_now(), duration, game_mode, player1_id, player2_id, winner_id))
    game_id = cur.lastrowid

    # Vložíme skóre pro oba hráče
    cur.execute("""
        INSERT INTO score (points, hits, player_id, game_id)
        VALUES (?, ?, ?, ?)
    """, (geek1Score, hits, player1_id, game_id))

    cur.execute("""
        INSERT INTO score (points, hits, player_id, game_id)
        VALUES (?, ?, ?, ?)
    """, (geek2Score, 0, player2_id, game_id))

    conn.commit()
    conn.close()
    print(f"✅ Uloženo: {username} {geek1Score} : {geek2Score} {p2_name} | Vítěz: {winner_name} | Délka: {duration}s")


# ===================================================================
# FUNKCE HISTORY - Obrazovka s historií výsledků
# ===================================================================
def show_history():
    """
    Zobrazí přehled posledních her s filtry:
      - rozbalovací seznam hráčů (dropdown)
      - přepínač režimu: Vše / PVP / BOT
    """

    # ------------------------------------------------------------------
    # Pomocné funkce pro kreslení
    # ------------------------------------------------------------------
    def draw_cell(text, x, w, y, color, align="l", fnt=None):
        fnt = fnt or font_tiny
        surf = fnt.render(str(text), True, color)
        if align == "c":
            bx = x + (w - surf.get_width()) // 2
        elif align == "r":
            bx = x + w - surf.get_width()
        else:
            bx = x
        screen.blit(surf, (bx, y))

    # ------------------------------------------------------------------
    # Načteme všechny hráče z DB pro dropdown
    # ------------------------------------------------------------------
    def load_players():
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT username FROM player ORDER BY username")
        names = [r[0] for r in cur.fetchall()]
        conn.close()
        return ["Všichni"] + names

    # ------------------------------------------------------------------
    # Dotaz na hry podle aktivních filtrů
    # ------------------------------------------------------------------
    def load_rows(player_filter, mode_filter):
        conn = get_connection()
        cur  = conn.cursor()

        conditions = []
        params     = []

        if player_filter != "Všichni":
            conditions.append("(p1.username = ? OR p2.username = ?)")
            params += [player_filter, player_filter]

        if mode_filter != "Vše":
            conditions.append("g.game_mode = ?")
            params.append(mode_filter)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        cur.execute(f"""
            SELECT
                g.game_id,
                g.played_at,
                g.duration_seconds,
                g.game_mode,
                p1.username                    AS hrac1,
                s1.points                      AS skore1,
                s1.hits                        AS hity1,
                p2.username                    AS hrac2,
                s2.points                      AS skore2,
                COALESCE(pw.username, 'Remíza') AS vitez
            FROM game g
            JOIN player  p1 ON p1.player_id = g.player1_id
            JOIN player  p2 ON p2.player_id = g.player2_id
            JOIN score   s1 ON s1.game_id   = g.game_id AND s1.player_id = g.player1_id
            JOIN score   s2 ON s2.game_id   = g.game_id AND s2.player_id = g.player2_id
            LEFT JOIN player pw ON pw.player_id = g.winner_player
            {where}
            ORDER BY g.played_at DESC
            LIMIT 50
        """, params)
        data = cur.fetchall()
        conn.close()
        return data

    # ------------------------------------------------------------------
    # Počáteční stav
    # ------------------------------------------------------------------
    players       = load_players()          # ["Všichni", "hráč1", ...]
    sel_player    = 0                        # index do players[]
    mode_options  = ["Vše", "PVP", "BOT"]
    sel_mode      = 0                        # index do mode_options[]
    dropdown_open = False                    # je dropdown rozbalený?

    rows      = load_rows(players[sel_player], mode_options[sel_mode])
    scroll_y  = 0
    ROW_HEIGHT = 48
    FILTER_H   = 56    # výška pruhu s filtry
    HEADER_H   = 56    # výška záhlaví sloupců  (pod filtry)
    TABLE_TOP  = FILTER_H + HEADER_H + 4   # kde začínají datové řádky
    TABLE_BOT  = HEIGHT - 62               # kde končí (nad tlačítkem ZPĚT)

    def recalc_scroll():
        return max(0, len(rows) * ROW_HEIGHT - (TABLE_BOT - TABLE_TOP))

    max_scroll = recalc_scroll()

    # ------------------------------------------------------------------
    # UI prvky – pozice
    # ------------------------------------------------------------------
    back_button = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 54, 180, 40)

    # Dropdown hráče
    DD_X, DD_Y, DD_W, DD_H = 16, 12, 200, 32
    dd_rect = pygame.Rect(DD_X, DD_Y, DD_W, DD_H)

    # Přepínače režimu (tři tlačítka vedle sebe)
    MODE_X = DD_X + DD_W + 20
    mode_rects = [pygame.Rect(MODE_X + i * 80, DD_Y, 74, DD_H) for i in range(3)]

    # Záhlaví sloupců tabulky (x, šířka, zarovnání, popisek)
    cols = [
        ("#",       16,  30, "l"),
        ("Datum",   54, 152, "l"),
        ("Čas",    214,  50, "r"),
        ("Režim",  276,  54, "l"),
        ("Hráč 1", 342, 112, "l"),
        ("Skóre",  462,  64, "c"),
        ("Hráč 2", 534, 112, "l"),
        ("Vítěz",  656, 230, "l"),
    ]

    running = True
    while running:
        screen.fill(COLOR_BG)
        mouse = pygame.mouse.get_pos()

        # ==============================================================
        # PRUH S FILTRY (nahoře)
        # ==============================================================
        pygame.draw.rect(screen, COLOR_BAR, (0, 0, WIDTH, FILTER_H))
        pygame.draw.line(screen, CYAN, (0, FILTER_H), (WIDTH, FILTER_H), 1)

        # -- Popisek filtru hráče --
        lbl = font_tiny.render("Hráč:", True, (120, 120, 180))
        screen.blit(lbl, (DD_X, DD_Y - 2))   # nad dropdownem není místo → vlevo

        # -- Dropdown box --
        dd_hovered = dd_rect.collidepoint(mouse) and not dropdown_open
        dd_bg = (40, 40, 80) if dd_hovered else (25, 25, 50)
        pygame.draw.rect(screen, dd_bg, dd_rect, border_radius=6)
        pygame.draw.rect(screen, CYAN, dd_rect, width=1, border_radius=6)
        dd_txt = font_tiny.render(players[sel_player], True, WHITE)
        screen.blit(dd_txt, (dd_rect.x + 8, dd_rect.y + 8))
        # šipka dolů ▼
        arrow = font_tiny.render("▼", True, CYAN)
        screen.blit(arrow, (dd_rect.right - arrow.get_width() - 6, dd_rect.y + 8))

        # -- Přepínače režimu --
        for i, (mrect, mlabel) in enumerate(zip(mode_rects, mode_options)):
            selected = (i == sel_mode)
            bg  = (40, 40, 90) if selected else (20, 20, 40)
            brd = CYAN if selected else COLOR_LINE
            pygame.draw.rect(screen, bg, mrect, border_radius=6)
            pygame.draw.rect(screen, brd, mrect, width=1, border_radius=6)
            mc = CYAN if selected else (140, 140, 180)
            mt = font_tiny.render(mlabel, True, mc)
            screen.blit(mt, (mrect.x + (mrect.width - mt.get_width()) // 2,
                             mrect.y + (mrect.height - mt.get_height()) // 2))

        # Počet nalezených záznamů (vpravo v pruhu)
        cnt = font_tiny.render(f"Nalezeno: {len(rows)}", True, (80, 80, 130))
        screen.blit(cnt, (WIDTH - cnt.get_width() - 14, DD_Y + 8))

        # ==============================================================
        # ZÁHLAVÍ SLOUPCŮ
        # ==============================================================
        hdr_y = FILTER_H + 6
        for label, x, w, align in cols:
            draw_cell(label, x, w, hdr_y, (120, 120, 180), align)
        pygame.draw.line(screen, COLOR_LINE,
                         (0, FILTER_H + HEADER_H - 2),
                         (WIDTH, FILTER_H + HEADER_H - 2), 1)

        # ==============================================================
        # TABULKA (ořezaná oblast)
        # ==============================================================
        clip_rect = pygame.Rect(0, TABLE_TOP, WIDTH, TABLE_BOT - TABLE_TOP)
        screen.set_clip(clip_rect)

        for i, r in enumerate(rows):
            ry = TABLE_TOP + i * ROW_HEIGHT - scroll_y

            row_bg = (16, 16, 28) if i % 2 == 0 else (20, 20, 36)
            pygame.draw.rect(screen, row_bg, (0, ry, WIDTH, ROW_HEIGHT - 1))

            if clip_rect.collidepoint(mouse) and ry <= mouse[1] < ry + ROW_HEIGHT:
                pygame.draw.rect(screen, (30, 30, 60), (0, ry, WIDTH, ROW_HEIGHT - 1))

            game_id, played_at, dur, mode_g, h1, s1, hits, h2, s2, win = r
            datum = str(played_at)[:16] if played_at else "?"

            vitez_color = GREEN if win == h1 else (YELLOW_NEON if win == "Remíza" else RED_NEON)

            cy = ry + (ROW_HEIGHT - 16) // 2   # svislé středění

            cell_data = [
                (str(game_id),    cols[0][1], cols[0][2], cols[0][3], WHITE),
                (datum,           cols[1][1], cols[1][2], cols[1][3], (150, 150, 195)),
                (f"{dur}s",       cols[2][1], cols[2][2], cols[2][3], (120, 120, 165)),
                (mode_g,          cols[3][1], cols[3][2], cols[3][3], CYAN),
                (h1,              cols[4][1], cols[4][2], cols[4][3], GREEN),
                (f"{s1} : {s2}",  cols[5][1], cols[5][2], cols[5][3], WHITE),
                (h2,              cols[6][1], cols[6][2], cols[6][3], RED_NEON),
                (win,             cols[7][1], cols[7][2], cols[7][3], vitez_color),
            ]
            for text, x, w, align, color in cell_data:
                draw_cell(text, x, w, cy, color, align)

        screen.set_clip(None)

        # Oddělovač nad spodním panelem
        pygame.draw.line(screen, COLOR_LINE, (0, TABLE_BOT + 2), (WIDTH, TABLE_BOT + 2), 1)

        if not rows:
            no_data = font_medium.render("Žádné výsledky.", True, (80, 80, 120))
            screen.blit(no_data, (WIDTH // 2 - no_data.get_width() // 2,
                                  (TABLE_TOP + TABLE_BOT) // 2 - 15))

        # ==============================================================
        # SCROLLBAR
        # ==============================================================
        if max_scroll > 0:
            track_h = TABLE_BOT - TABLE_TOP
            thumb_h = max(30, int(track_h * track_h / (track_h + max_scroll)))
            thumb_y = TABLE_TOP + int(scroll_y / max_scroll * (track_h - thumb_h))
            pygame.draw.rect(screen, (30, 30, 60), (WIDTH - 8, TABLE_TOP, 8, track_h))
            pygame.draw.rect(screen, (80, 80, 140), (WIDTH - 7, thumb_y, 6, thumb_h), border_radius=3)

        # ==============================================================
        # TLAČÍTKO ZPĚT
        # ==============================================================
        draw_button(screen, back_button, "← ZPĚT", font_small,
                    BTN_MENU_NORMAL, BTN_MENU_HOVER, mouse,
                    text_color=CYAN, radius=10, border_color=COLOR_LINE)

        # ==============================================================
        # DROPDOWN SEZNAM (kreslíme jako poslední = přes vše ostatní)
        # ==============================================================
        if dropdown_open:
            item_h  = 28
            dd_list = pygame.Rect(DD_X, DD_Y + DD_H, DD_W, min(len(players), 10) * item_h)
            pygame.draw.rect(screen, (20, 20, 45), dd_list, border_radius=4)
            pygame.draw.rect(screen, CYAN, dd_list, width=1, border_radius=4)

            for j, name in enumerate(players[:10]):   # max 10 položek bez scrollu
                iy = DD_Y + DD_H + j * item_h
                ir = pygame.Rect(DD_X, iy, DD_W, item_h)

                item_hov = ir.collidepoint(mouse)
                if j == sel_player:
                    pygame.draw.rect(screen, (40, 40, 90), ir)
                elif item_hov:
                    pygame.draw.rect(screen, (30, 30, 70), ir)

                ic = CYAN if j == sel_player else WHITE
                it = font_tiny.render(name, True, ic)
                screen.blit(it, (ir.x + 8, ir.y + (item_h - it.get_height()) // 2))

        # ==============================================================
        # UDÁLOSTI
        # ==============================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if dropdown_open:
                        dropdown_open = False
                    else:
                        return
                if not dropdown_open:
                    if event.key == pygame.K_UP:
                        scroll_y = max(0, scroll_y - ROW_HEIGHT)
                    if event.key == pygame.K_DOWN:
                        scroll_y = min(max_scroll, scroll_y + ROW_HEIGHT)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Scrollování kolečkem
                if event.button == 4:
                    scroll_y = max(0, scroll_y - ROW_HEIGHT)
                if event.button == 5:
                    scroll_y = min(max_scroll, scroll_y + ROW_HEIGHT)

                if event.button == 1:
                    # Tlačítko ZPĚT
                    if back_button.collidepoint(event.pos):
                        return

                    # Klik na dropdown box = otevřít / zavřít
                    if dd_rect.collidepoint(event.pos):
                        dropdown_open = not dropdown_open

                    # Klik na položku v otevřeném dropdownu
                    elif dropdown_open:
                        item_h = 28
                        for j, name in enumerate(players[:10]):
                            ir = pygame.Rect(DD_X, DD_Y + DD_H + j * item_h, DD_W, item_h)
                            if ir.collidepoint(event.pos):
                                sel_player    = j
                                dropdown_open = False
                                rows          = load_rows(players[sel_player],
                                                          mode_options[sel_mode])
                                scroll_y      = 0
                                max_scroll    = recalc_scroll()
                                break
                        else:
                            dropdown_open = False  # klik mimo = zavřít

                    # Přepínače režimu
                    else:
                        for i, mrect in enumerate(mode_rects):
                            if mrect.collidepoint(event.pos):
                                sel_mode   = i
                                rows       = load_rows(players[sel_player],
                                                       mode_options[sel_mode])
                                scroll_y   = 0
                                max_scroll = recalc_scroll()
                                break

        pygame.display.update()
        clock.tick(FPS)


# ===================================================================
# FUNKCE MAIN - Hlavní herní smyčka
# ===================================================================
def main(mode, player_name):
    """
    Spustí samotnou hru.

    mode        = "PVP" nebo "BOT"
    player_name = jméno hráče 1
    """

    # Vytvoříme objekty pálek a míčku pomocí našich tříd
    # Parametry Striker: (X pozice, Y pozice, šířka, výška, rychlost, barva)
    geek1 = Striker(20,         0, 10, 100, 10, GREEN)     # Levá pálka (zelená)
    geek2 = Striker(WIDTH - 30, 0, 10, 100, 10, RED_NEON)  # Pravá pálka (červená)

    # Míček uprostřed hrací plochy
    # Parametry Ball: (X, Y, poloměr, rychlost, barva)
    ball = Ball(WIDTH // 2, (HEIGHT - TOP_BAR_HEIGHT - 50) // 2, 7, 7, WHITE)

    geek1Score = 0   # Skóre levého hráče (počet gólů)
    geek2Score = 0   # Skóre pravého hráče / bota
    geek1Hits  = 0   # Počet odrazů od levé pálky (uložíme do databáze jako statistiku)

    start_time = time.time()   # Uložíme čas startu hry (pro výpočet celkové délky)

    # Slovníky pro sledování stisknutých kláves
    # Tato metoda (True/False) je lepší než pygame.key.get_pressed()
    # protože správně funguje při simultánním stisku W+S nebo nahoru+dolů
    geek1_keys = {'w': False, 's': False}          # Klávesy pro levou pálku (W = nahoru, S = dolů)
    geek2_keys = {'up': False, 'down': False}      # Klávesy pro pravou pálku (šipky)

    # Definujeme obdélníky (polohu a velikost) tlačítek v horní liště
    pause_button = pygame.Rect(WIDTH // 2 - 60, 10, 120, 40)   # Tlačítko PAUZA uprostřed

    # Definujeme obdélníky tlačítek v pause overlay (poloprůhledném překrytí)
    resume_button = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 - 30, 260, 48)  # POKRAČOVAT
    menu_button   = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 30, 260, 48)  # MENU
    quit_button   = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 90, 260, 48)  # UKONČIT

    paused  = False   # Je hra aktuálně pozastavená?
    running = True    # Řídicí proměnná herní smyčky (True = hra běží)

    # ---------------------------------------------------------------
    # HLAVNÍ HERNÍ SMYČKA
    # Tato smyčka se opakuje 60x za sekundu.
    # Každá iterace = jeden snímek = vykresli + zpracuj vstup + pohni objekty
    # ---------------------------------------------------------------
    while running:

        # Vyplníme celé pozadí tmavou barvou (smažeme předchozí snímek)
        screen.fill(COLOR_BG)

        # Aktuální pozice myši (potřebujeme pro hover efekty tlačítek)
        mouse = pygame.mouse.get_pos()

        # --- Pozadí hřiště: jemná mřížka pro retro vzhled ---
        for x in range(0, WIDTH, 60):   # Svislé čáry každých 60 pixelů
            pygame.draw.line(screen, (18, 18, 30), (x, TOP_BAR_HEIGHT), (x, HEIGHT - 50))
        for y in range(TOP_BAR_HEIGHT, HEIGHT - 50, 60):   # Vodorovné čáry každých 60px
            pygame.draw.line(screen, (18, 18, 30), (0, y), (WIDTH, y))

        # Přerušovaná čára uprostřed hřiště (vizuální rozdělení stran)
        draw_dashed_center_line(screen)

        # Horní lišta s logem "PONG" a tlačítkem PAUZA
        draw_top_bar(screen, pause_button, mouse)

        # --- Zpracování všech událostí (vstup od uživatele v tomto snímku) ---
        for event in pygame.event.get():

            # Uživatel kliknul na X = zavřít okno
            if event.type == pygame.QUIT:
                duration = int(time.time() - start_time)   # Vypočítáme délku hry v sekundách
                save_result(player_name, geek1Score, geek2Score, geek1Hits, mode, duration) # Uložíme výsledek
                pygame.quit()
                quit()

            # Uživatel kliknul myší
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Klik na tlačítko PAUZA v horní liště = přepnout pauzu
                if pause_button.collidepoint(event.pos):
                    paused = not paused   # not True = False, not False = True (přepnutí)

                # Kliknutí na tlačítka v pause overlay (jen pokud je hra pozastavená)
                if paused:
                    if resume_button.collidepoint(event.pos):
                        paused = False   # Zrušíme pauzu = hra pokračuje

                    if menu_button.collidepoint(event.pos):
                        # Uložíme výsledek a vrátíme se do hlavního menu
                        duration = int(time.time() - start_time)
                        save_result(player_name, geek1Score, geek2Score, geek1Hits, mode, duration)
                        return   # "return" ukončí funkci main() a vrátíme se do while True v __main__

                    if quit_button.collidepoint(event.pos):
                        # Uložíme výsledek a ukončíme celou aplikaci
                        duration = int(time.time() - start_time)
                        save_result(player_name, geek1Score, geek2Score, geek1Hits, mode, duration)
                        pygame.quit()
                        quit()

            # Stisk klávesy
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:       geek1_keys['w']    = True   # W = levá pálka nahoru
                if event.key == pygame.K_s:       geek1_keys['s']    = True   # S = levá pálka dolů
                if event.key == pygame.K_ESCAPE:  paused = not paused         # ESC = přepnout pauzu
                if mode == "PVP":   # Šipky fungují jen v PVP módu (ne v BOT módu)
                    if event.key == pygame.K_UP:   geek2_keys['up']   = True  # Šipka nahoru
                    if event.key == pygame.K_DOWN: geek2_keys['down'] = True  # Šipka dolů

            # Puštění klávesy - musíme sledovat aby se pálka zastavila
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:       geek1_keys['w']    = False
                if event.key == pygame.K_s:       geek1_keys['s']    = False
                if mode == "PVP":
                    if event.key == pygame.K_UP:   geek2_keys['up']   = False
                    if event.key == pygame.K_DOWN: geek2_keys['down'] = False

        # --- Herní logika (přeskočí se pokud je hra pozastavená) ---
        if not paused:

            # Výpočet směru pohybu levé pálky
            # Podmíněný výraz: hodnota_a if podmínka else hodnota_b (zkrácený if-else)
            geek1YFac = (-1 if geek1_keys['w'] and not geek1_keys['s']    # Jen W = nahoru (-1)
                         else 1 if geek1_keys['s'] and not geek1_keys['w'] # Jen S = dolů (+1)
                         else 0)   # Obě klávesy nebo žádná = stůj (0)

            # Výpočet směru pohybu pravé pálky
            if mode == "PVP":
                # V PVP módu - druhý hráč ovládá pravou pálku šipkami
                geek2YFac = (-1 if geek2_keys['up'] and not geek2_keys['down']
                             else 1 if geek2_keys['down'] and not geek2_keys['up']
                             else 0)
            else:
                # V BOT módu - počítač automaticky sleduje míček
                mid = geek2.posy + geek2.height // 2   # Vypočítáme střed pravé pálky
                geek2YFac = (-1 if ball.posy < mid     # Míček je výš než střed = jdi nahoru
                             else 1 if ball.posy > mid  # Míček je níž než střed = jdi dolů
                             else 0)                    # Míček je přesně na středu = stůj

            # Detekce kolize míčku s pálkami pomocí colliderect()
            # colliderect() vrátí True pokud se dva obdélníky překrývají
            if ball.getRect().colliderect(geek1.getRect()):   # Levá pálka zasáhla míček
                ball.hit()       # Odraz + mírné zrychlení
                geek1Hits += 1   # Zaznamenáme hit pro statistiky do databáze

            if ball.getRect().colliderect(geek2.getRect()):   # Pravá pálka zasáhla míček
                ball.hit()       # Odraz + mírné zrychlení

            # Aktualizujeme pozice všech pohyblivých objektů
            geek1.update(geek1YFac)   # Posuneme levou pálku
            geek2.update(geek2YFac)   # Posuneme pravou pálku
            point = ball.update()     # Posuneme míček, vrátí 0, 1 nebo -1 (gól)

            # Zpracování gólu
            if point == -1:    # Míček vyjel vpravo = levý hráč (geek1) boduje
                geek1Score += 1
            elif point == 1:   # Míček vyjel vlevo = pravý hráč (geek2) boduje
                geek2Score += 1
            if point:          # Byl gól (cokoliv jiného než 0)? Resetujeme míček
                ball.reset()

        # --- Vykreslení všech herních objektů ---
        geek1.display()   # Levá pálka (zelená)
        geek2.display()   # Pravá pálka (červená)
        ball.display()    # Míček (s ocasem a září)

        # Dolní lišta se jmény hráčů a skóre
        draw_score_bar(screen, player_name, geek1Score, geek2Score, mode)

        # Pause overlay se kreslí jako POSLEDNÍ = překryje vše ostatní
        # (jinak by se herní objekty kreslily přes pause menu)
        if paused:
            draw_pause_overlay(screen, player_name, geek1Score, geek2Score, mode,
                               resume_button, menu_button, quit_button, mouse)

        # Zobrazíme nakreslený snímek na obrazovku
        # pygame používá "double buffering" = kreslíme na skrytou plochu, pak ji zobrazíme
        # Díky tomu nedochází k blikání
        pygame.display.update()

        # Omezíme rychlost herní smyčky na maximálně 60 snímků za sekundu
        # Bez toho by hra na rychlých počítačích běžela příliš rychle
        clock.tick(FPS)


# ===================================================================
# SPUŠTĚNÍ PROGRAMU
# ===================================================================
# Tento blok se spustí POUZE pokud spouštíme tento soubor přímo (python main_hra.py)
# Pokud by byl soubor importován jako modul (import main_hra), tento blok se přeskočí
if __name__ == "__main__":

    # Jako první vytvoříme tabulky v databázi (pokud ještě neexistují)
    # Je důležité to udělat PŘED spuštěním hry, jinak save_result() selže
    create_tables()

    # Nekonečná smyčka umožňuje hrát více her za sebou bez restartu programu
    # Po návratu z main() (klik na MENU tlačítko) se smyčka opakuje → menu se znovu zobrazí
    while True:
        mode, player_name = menu()   # Zobraz menu, počkej dokud hráč nezvolí START
        main(mode, player_name)      # Spusť hru s vybraným módem a jménem hráče