#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import asyncio
import signal
from datetime import datetime
from telethon import TelegramClient, events
from colorama import init, Fore, Back, Style
import pyfiglet

# Initialize colorama
init(autoreset=True)

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG_FILE = '/storage/emulated/0/Download/Scan_Results/scraper_config.json'
SESSION_FILE = 'fast_scraper_session'
OUTPUT_FILE = '/storage/emulated/0/Download/Scan_Results/cards_collected.txt'

# Global flag for listening mode
listening = False

class ConfigManager:
    """Manage configuration and session"""
    
    @staticmethod
    def save_config(api_id, api_hash, phone):
        try:
            config = {
                'api_id': api_id,
                'api_hash': api_hash,
                'phone': phone,
                'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except:
            return False
    
    @staticmethod
    def load_config():
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return None
        except:
            return None

class FastCardScraper:
    def __init__(self):
        self.api_id = None
        self.api_hash = None
        self.phone = None
        self.channel = None
        self.client = None
        self.total_cards = 0
        self.new_cards = 0
        self.start_time = None
        self.listening_active = False
        
        # Load config
        config = ConfigManager.load_config()
        if config:
            self.api_id = config.get('api_id')
            self.api_hash = config.get('api_hash')
            self.phone = config.get('phone')
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_animated_banner(self):
        """Print animated banner"""
        self.clear_screen()
        
        # Big ASCII Banner
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════╗
{Fore.RED}║{Fore.YELLOW}              ⚡ SUPER FAST CARD SCRAPER v5.0 ⚡          {Fore.RED}║
{Fore.RED}╠══════════════════════════════════════════════════════════╣
{Fore.RED}║{Fore.CYAN}             Created by: Mr Raj | Mr Tech Hacker          {Fore.RED}║
{Fore.RED}║{Fore.GREEN}             10x Faster | Batch Processing | Turbo Mode   {Fore.RED}║
{Fore.RED}╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
        
        # Login status
        if self.api_id:
            print(Fore.GREEN + "✅ LOGIN STATUS: ACTIVE")
        else:
            print(Fore.RED + "❌ LOGIN STATUS: NOT LOGGED IN")
        print()
    
    def print_menu(self):
        """Print main menu"""
        menu = f"""
{Fore.CYAN}┌──────────────────────────────────────────────────┐
{Fore.CYAN}│{Fore.YELLOW}              📋 MAIN MENU OPTIONS                {Fore.CYAN}│
{Fore.CYAN}├──────────────────────────────────────────────────┤
{Fore.CYAN}│  {Fore.GREEN}1️⃣  Login / Configure API                        {Fore.CYAN}│
{Fore.CYAN}│  {Fore.BLUE}2️⃣  🚀 START FAST SCRAPING (TURBO MODE)          {Fore.CYAN}│
{Fore.CYAN}│  {Fore.MAGENTA}3️⃣  📁 View Saved Cards                          {Fore.CYAN}│
{Fore.CYAN}│  {Fore.RED}4️⃣  🗑️  Clear All Data                            {Fore.CYAN}│
{Fore.CYAN}│  {Fore.RED}5️⃣  ❌ Exit                                      {Fore.CYAN}│
{Fore.CYAN}└──────────────────────────────────────────────────┘
        """
        print(menu)
    
    def print_login_screen(self):
        """Login screen"""
        self.clear_screen()
        self.print_animated_banner()
        
        print(Fore.CYAN + "╔════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Fore.YELLOW + "     🔐 LOGIN CONFIGURATION                     " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚════════════════════════════════════════════════╝\n")
        
        # API ID
        self.api_id = input(Fore.GREEN + "➤ Enter API ID: " + Fore.WHITE)
        
        # API Hash
        self.api_hash = input(Fore.GREEN + "➤ Enter API Hash: " + Fore.WHITE)
        
        # Phone
        self.phone = input(Fore.GREEN + "➤ Enter Phone (+91...): " + Fore.WHITE)
        
        # Save config
        if ConfigManager.save_config(self.api_id, self.api_hash, self.phone):
            print(Fore.GREEN + "\n✅ Configuration saved successfully!")
        else:
            print(Fore.RED + "\n❌ Failed to save config!")
        
        input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
    
    async def fast_login(self):
        """Fast login with session reuse"""
        try:
            self.client = TelegramClient(SESSION_FILE, int(self.api_id), self.api_hash)
            
            # Try to connect
            await self.client.connect()
            
            # Check if already authorized
            if await self.client.is_user_authorized():
                print(Fore.GREEN + "✅ Using existing session!")
                return True
            
            # Need new login
            print(Fore.YELLOW + "📱 New login required...")
            await self.client.start(phone=self.phone)
            print(Fore.GREEN + "✅ Login successful! Session saved.")
            return True
            
        except Exception as e:
            print(Fore.RED + f"❌ Login error: {e}")
            return False
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        global listening
        listening = False
        print(Fore.YELLOW + "\n\n⏹️ Stopping listener...")
    
    async def fast_scrape(self):
        """Ultra fast scraping function"""
        global listening
        
        # Set signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.start_time = datetime.now()
        
        # Login first
        print(Fore.CYAN + "\n🔄 Connecting to Telegram..." + Style.RESET_ALL)
        if not await self.fast_login():
            input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
            return
        
        # Get channel
        try:
            channel_entity = await self.client.get_entity(self.channel)
            print(Fore.GREEN + f"✅ Connected to: {channel_entity.title}")
        except Exception as e:
            print(Fore.RED + f"❌ Channel error: {e}")
            input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
            return
        
        # Create output file with header
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'w') as f:
                f.write(f"# CARDS COLLECTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# FORMAT: NUMBER|MONTH|YEAR|CVV\n\n")
        
        # ===== FAST BATCH PROCESSING =====
        print(Fore.MAGENTA + "\n🔍 SCANNING MESSAGES (TURBO MODE)..." + Style.RESET_ALL)
        
        self.total_cards = 0
        messages_processed = 0
        progress_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        progress_idx = 0
        
        # Get messages
        async for message in self.client.iter_messages(channel_entity, limit=1000):
            messages_processed += 1
            
            if message and message.text:
                pattern = r'(\d{16})\|(\d{2})\|(\d{2})\|(\d{3})'
                matches = re.findall(pattern, message.text)
                
                if matches:
                    with open(OUTPUT_FILE, 'a') as f:
                        for match in matches:
                            f.write(f"{match[0]}|{match[1]}|{match[2]}|{match[3]}\n")
                            self.total_cards += 1
                    
                    # Show progress
                    progress = progress_chars[progress_idx % len(progress_chars)]
                    print(f"\r{Fore.CYAN}{progress} Processing: {messages_processed} msgs | "
                          f"{Fore.GREEN}Found: {self.total_cards} cards", end="", flush=True)
                    progress_idx += 1
        
        print()  # New line after progress
        
        # ===== COMPLETION MESSAGE =====
        time_taken = (datetime.now() - self.start_time).total_seconds()
        
        print(Fore.GREEN + "\n" + "="*60)
        print(Fore.YELLOW + "          ✅ PROCESSING COMPLETE! ✅")
        print(Fore.GREEN + "="*60)
        print(Fore.CYAN + f"📊 Total Messages Scanned: {messages_processed}")
        print(Fore.GREEN + f"💳 Cards Found: {self.total_cards}")
        print(Fore.BLUE + f"⏱️  Time Taken: {time_taken:.2f} seconds")
        print(Fore.MAGENTA + f"📁 Saved to: {OUTPUT_FILE}")
        print(Fore.GREEN + "="*60)
        
        # ===== ASK FOR LISTENING MODE =====
        print(Fore.YELLOW + "\n🔔 Do you want to listen for new cards?")
        listen_choice = input(Fore.CYAN + "➤ Press 'Y' for Yes, any other key for Menu: " + Fore.WHITE)
        
        if listen_choice.upper() == 'Y':
            # ===== REAL-TIME LISTENER =====
            print(Fore.GREEN + "\n👂 LISTENING FOR NEW CARDS... (Press Ctrl+C to stop)\n")
            listening = True
            
            @self.client.on(events.NewMessage(chats=channel_entity))
            async def handler(event):
                if listening and event.message and event.message.text:
                    pattern = r'(\d{16})\|(\d{2})\|(\d{2})\|(\d{3})'
                    matches = re.findall(pattern, event.message.text)
                    
                    if matches:
                        with open(OUTPUT_FILE, 'a') as f:
                            for match in matches:
                                f.write(f"{match[0]}|{match[1]}|{match[2]}|{match[3]}\n")
                                self.new_cards += 1
                        
                        print(Fore.GREEN + f"✨ NEW CARD FOUND! Total: {self.total_cards + self.new_cards}")
            
            try:
                await self.client.run_until_disconnected()
            except asyncio.CancelledError:
                pass
            finally:
                listening = False
                print(Fore.YELLOW + "\n\n👂 Listener stopped.")
        else:
            print(Fore.YELLOW + "\n⏹️ Returning to menu...")
        
        # Disconnect client
        if self.client:
            await self.client.disconnect()
        
        # ===== RETURN TO MENU =====
        input(Fore.MAGENTA + "\n📌 Press Enter to return to main menu..." + Style.RESET_ALL)
    
    def print_start_screen(self):
        """Start scraping screen"""
        self.clear_screen()
        self.print_animated_banner()
        
        if not all([self.api_id, self.api_hash, self.phone]):
            print(Fore.RED + "❌ Please login first! (Option 1)")
            input(Fore.MAGENTA + "\n📌 Press Enter to continue...")
            return False
        
        print(Fore.CYAN + "╔════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Fore.YELLOW + "  FAST SCRAPING CONFIGURATION                   " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚════════════════════════════════════════════════╝\n")
        
        self.channel = input(Fore.GREEN + "➤ Enter Channel (e.g., @channel): " + Fore.WHITE)
        
        if self.channel:
            print(Fore.YELLOW + "\n⚡ TURBO MODE ACTIVATED! Processing..." + Style.RESET_ALL)
            return True
        return False
    
    def view_cards(self):
        """View saved cards"""
        self.clear_screen()
        self.print_animated_banner()
        
        print(Fore.CYAN + "╔════════════════════════════════════════════════╗")
        print(Fore.CYAN + "║" + Fore.YELLOW + "            📁 SAVED CARDS PREVIEW             " + Fore.CYAN + "║")
        print(Fore.CYAN + "╚════════════════════════════════════════════════╝\n")
        
        try:
            if os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, 'r') as f:
                    lines = f.readlines()
                
                # Count actual cards
                cards = [l for l in lines if '|' in l and not l.startswith('#')]
                total = len(cards)
                
                print(Fore.GREEN + f"📊 Total Cards: {total}")
                print(Fore.CYAN + f"📁 File: {OUTPUT_FILE}\n")
                
                if total > 0:
                    print(Fore.YELLOW + "📋 Last 10 Cards:")
                    print(Fore.CYAN + "-"*50)
                    
                    for line in cards[-10:]:
                        card = line.strip().split('|')
                        if len(card) == 4:
                            preview = f"{card[0][:4]}...{card[0][-4:]}|{card[1]}|{card[2]}|{card[3]}"
                            print(Fore.GREEN + f"  {preview}")
                    
                    print(Fore.CYAN + "-"*50)
                else:
                    print(Fore.RED + "❌ No cards found yet!")
            else:
                print(Fore.RED + "❌ No file found! Start scraping first.")
        
        except Exception as e:
            print(Fore.RED + f"❌ Error: {e}")
        
        input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
    
    def clear_all(self):
        """Clear all data"""
        self.clear_screen()
        self.print_animated_banner()
        
        print(Fore.RED + "╔════════════════════════════════════════════════╗")
        print(Fore.RED + "║" + Fore.YELLOW + "      ⚠️  CLEAR ALL DATA  ⚠️     " + Fore.RED + "║")
        print(Fore.RED + "╚════════════════════════════════════════════════╝\n")
        
        print(Fore.RED + "This will delete:")
        print(Fore.YELLOW + "  • Login credentials")
        print(Fore.YELLOW + "  • Session files")
        print(Fore.YELLOW + "  • All saved cards\n")
        
        confirm = input(Fore.RED + "Type 'DELETE ALL' to confirm: " + Fore.WHITE)
        
        if confirm == 'DELETE ALL':
            # Delete config
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            
            # Delete session
            if os.path.exists(f"{SESSION_FILE}.session"):
                os.remove(f"{SESSION_FILE}.session")
            
            # Delete cards
            if os.path.exists(OUTPUT_FILE):
                os.remove(OUTPUT_FILE)
            
            # Reset vars
            self.api_id = None
            self.api_hash = None
            self.phone = None
            
            print(Fore.GREEN + "\n✅ All data cleared successfully!")
        else:
            print(Fore.YELLOW + "\n❌ Operation cancelled.")
        
        input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
    
    def run(self):
        """Main loop"""
        while True:
            self.clear_screen()
            self.print_animated_banner()
            self.print_menu()
            
            choice = input(Fore.YELLOW + "➤ Select option (1-5): " + Fore.WHITE)
            
            if choice == '1':
                self.print_login_screen()
            
            elif choice == '2':
                if self.print_start_screen():
                    try:
                        asyncio.run(self.fast_scrape())
                    except KeyboardInterrupt:
                        print(Fore.YELLOW + "\n\n⏹️ Scraping stopped by user.")
                        input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"\n❌ Error: {e}")
                        input(Fore.MAGENTA + "\n📌 Press Enter to return to menu..." + Style.RESET_ALL)
            
            elif choice == '3':
                self.view_cards()
            
            elif choice == '4':
                self.clear_all()
            
            elif choice == '5':
                print(Fore.GREEN + "\n👋 Thanks for using Fast Card Scraper!")
                print(Fore.CYAN + "   Created by Mr Raj | Mr Tech Hacker\n")
                break
            
            else:
                print(Fore.RED + "\n❌ Invalid option!")
                input(Fore.MAGENTA + "\n📌 Press Enter to continue...")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    try:
        # Install requirements if needed
        try:
            from colorama import init
            import pyfiglet
        except ImportError:
            print("📦 Installing required packages...")
            os.system('pip install colorama pyfiglet telethon')
            print("✅ Packages installed! Please run again.")
            sys.exit(0)
        
        # Run scraper
        scraper = FastCardScraper()
        scraper.run()
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Goodbye!")
    except Exception as e:
        print(Fore.RED + f"\n❌ Fatal Error: {e}")
