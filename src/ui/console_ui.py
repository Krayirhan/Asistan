"""
Console UI - Terminal Arayüzü
Rich library ile renkli ve interaktif konsol
"""

import sys
from typing import Optional
from loguru import logger

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.live import Live
    from rich.spinner import Spinner
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logger.warning("Rich yüklü değil! pip install rich")


class ConsoleUI:
    """Renkli terminal arayüzü"""
    
    def __init__(self, config: dict, llm_manager, stt_engine, tts_engine):
        self.config = config
        self.llm_manager = llm_manager
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        
        self.ui_config = config['ui']['console']
        self.colored = self.ui_config.get('colored_output', True)
        self.markdown = self.ui_config.get('markdown_rendering', True)
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def print(self, text: str, style: str = ""):
        """
        Konsola yazdır
        
        Args:
            text: Yazdırılacak metin
            style: Rich style (örn: "bold red")
        """
        
        if self.console and self.colored:
            self.console.print(text, style=style)
        else:
            print(text)
    
    def print_markdown(self, text: str):
        """
        Markdown formatında yazdır
        
        Args:
            text: Markdown metni
        """
        
        if self.console and self.markdown and RICH_AVAILABLE:
            md = Markdown(text)
            self.console.print(md)
        else:
            print(text)
    
    def print_panel(self, text: str, title: str = "", style: str = "blue"):
        """
        Panel içinde yazdır
        
        Args:
            text: Metin
            title: Panel başlığı
            style: Panel stili
        """
        
        if self.console and RICH_AVAILABLE:
            panel = Panel(text, title=title, border_style=style)
            self.console.print(panel)
        else:
            print(f"\n{'='*50}")
            if title:
                print(f"{title}")
                print('='*50)
            print(text)
            print('='*50)
    
    def input(self, prompt: str = "You: ") -> str:
        """
        Kullanıcıdan girdi al
        
        Args:
            prompt: Prompt metni
        
        Returns:
            Kullanıcı girdisi
        """
        
        if self.console and RICH_AVAILABLE:
            return Prompt.ask(f"[green]{prompt}[/green]")
        else:
            return input(prompt)
    
    def show_thinking(self, message: str = "Düşünüyor..."):
        """
        Düşünme animasyonu göster
        
        Args:
            message: Gösterilecek mesaj
        """
        
        if self.console and RICH_AVAILABLE:
            spinner = Spinner("dots", text=message)
            return Live(spinner, console=self.console, refresh_per_second=10)
        else:
            print(f"{message}")
            return None
    
    def run(self):
        """Ana konsol döngüsü"""
        
        self.print_panel(
            "🎤 AI Voice Assistant - Console Mode\n"
            "Komutlar:\n"
            "  /voice - Sesli mod\n"
            "  /image <path> - Resim analizi\n"
            "  /search <query> - Web araması\n"
            "  /clear - Geçmişi temizle\n"
            "  /exit - Çıkış\n",
            title="Hoş Geldiniz!",
            style="cyan"
        )
        
        try:
            while True:
                # Kullanıcı girdisi
                user_input = self.input("\nYou")
                
                if not user_input.strip():
                    continue
                
                # Komut kontrolü
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Normal soru - LLM'e sor
                self._process_query(user_input)
                
        except KeyboardInterrupt:
            self.print("\n\n👋 Güle güle!", style="yellow")
        except Exception as e:
            logger.error(f"UI hatası: {e}")
            self.print(f"\n❌ Hata: {e}", style="red")
    
    def _handle_command(self, command: str):
        """Komutları işle"""
        
        cmd = command.lower().split()[0]
        
        if cmd == '/exit' or cmd == '/quit':
            self.print("\n👋 Güle güle!", style="yellow")
            sys.exit(0)
        
        elif cmd == '/clear':
            self.llm_manager.clear_history()
            self.print("✅ Geçmiş temizlendi", style="green")
        
        elif cmd == '/voice':
            self._voice_mode()
        
        elif cmd == '/image':
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                self._analyze_image(parts[1])
            else:
                self.print("❌ Kullanım: /image <dosya_yolu>", style="red")
        
        elif cmd == '/search':
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                self._web_search(parts[1])
            else:
                self.print("❌ Kullanım: /search <sorgu>", style="red")
        
        else:
            self.print(f"❌ Bilinmeyen komut: {cmd}", style="red")
    
    def _process_query(self, query: str, speak: bool = False):
        """
        Kullanıcı sorgusunu işle
        
        Args:
            query: Kullanıcı sorusu
            speak: Cevabı sesli oku
        """
        
        # Düşünme animasyonu
        thinking = self.show_thinking("🤖 Düşünüyor...")
        if thinking:
            thinking.start()
        
        # LLM'den cevap al
        response = self.llm_manager.generate(query, stream=False)
        
        if thinking:
            thinking.stop()
        
        # Cevabı göster
        self.print("\n🤖 Assistant:", style="bold cyan")
        self.print_markdown(response)
        
        # Sesli okuma (opsiyonel)
        if speak and self.tts_engine:
            self.tts_engine.speak(response)
    
    def _voice_mode(self):
        """Sesli mod - mikrofon ile konuşma"""
        
        self.print("\n🎤 Sesli Mod Aktif! (5 saniye konuşun, Ctrl+C ile çık)\n", style="yellow")
        
        try:
            # Mikrofon ile kaydet
            audio = self.stt_engine.record_audio(duration=5)
            
            # Sessizlik kontrolü
            if self.stt_engine.is_audio_silent(audio):
                self.print("⚠️  Sessizlik algılandı, tekrar deneyin", style="yellow")
                return
            
            # Transkribe et
            self.print("✍️  Transkribe ediliyor...", style="cyan")
            text = self.stt_engine.transcribe(audio_array=audio)
            
            if not text:
                self.print("❌ Transkripsiyon başarısız", style="red")
                return
            
            self.print(f"\n📝 Siz: {text}\n", style="green")
            
            # LLM'e sor ve sesli yanıt ver
            self._process_query(text, speak=True)
            
        except KeyboardInterrupt:
            self.print("\n⏸️  Sesli mod iptal edildi", style="yellow")
        except Exception as e:
            logger.error(f"Sesli mod hatası: {e}")
            self.print(f"\n❌ Hata: {e}", style="red")
    
    def _analyze_image(self, image_path: str):
        """Resim analizi"""
        
        self.print(f"\n📸 Görsel analiz ediliyor: {image_path}\n", style="cyan")
        
        try:
            result = self.llm_manager.analyze_image(image_path)
            
            self.print("\n🤖 Görsel Analizi:", style="bold cyan")
            self.print_markdown(result)
            
        except Exception as e:
            logger.error(f"Görsel analiz hatası: {e}")
            self.print(f"\n❌ Hata: {e}", style="red")
    
    def _web_search(self, query: str):
        """Web araması"""
        
        from tools.web_search import WebSearchTool
        
        search_tool = WebSearchTool(self.config)
        
        self.print(f"\n🔍 Web'de aranıyor: '{query}'\n", style="cyan")
        
        results = search_tool.search(query, max_results=5)
        
        if not results:
            self.print("❌ Sonuç bulunamadı", style="red")
            return
        
        # Sonuçları göster
        self.print("\n📄 Arama Sonuçları:\n", style="bold green")
        
        for i, result in enumerate(results, 1):
            self.print(f"{i}. {result['title']}", style="bold")
            self.print(f"   {result['url']}", style="dim")
            self.print(f"   {result['snippet'][:150]}...\n")
