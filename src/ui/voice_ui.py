"""
Voice UI - Tamamen Sesli Arayüz
Wake word ile aktivasyon + ses tanıma + sesli yanıt
"""

import time
from loguru import logger


class VoiceUI:
    """Tamamen sesli interaksiyon"""
    
    def __init__(self, config: dict, llm_manager, stt_engine, tts_engine, wake_word_detector):
        self.config = config
        self.llm_manager = llm_manager
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        self.wake_word = wake_word_detector
        
        self.voice_config = config['ui']['voice']
        self.auto_listen = self.voice_config.get('auto_listen', True)
        self.continuous = self.voice_config.get('continuous_mode', False)
    
    def run(self):
        """Ana sesli döngü"""
        
        logger.info("🎤 Voice Mode başlatıldı!")
        
        if self.tts_engine:
            self.tts_engine.speak("Merhaba! Ben AI asistanınızım. Size nasıl yardımcı olabilirim?")
        
        try:
            while True:
                # Wake word bekle
                if self.wake_word and self.wake_word.porcupine:
                    logger.info("👂 Wake word bekleniyor...")
                    
                    if self.tts_engine:
                        # Sessiz mod - sadece log
                        pass
                    
                    # Wake word dinle
                    self.wake_word.listen(callback=self._on_wake_word_detected)
                else:
                    # Wake word yoksa direkt dinle
                    self._listen_and_respond()
                
                # Continuous mode değilse bir kez çalıştır
                if not self.continuous:
                    break
                
                # Biraz bekle
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Voice Mode kapatılıyor...")
            
            if self.tts_engine:
                self.tts_engine.speak("Güle güle!")
    
    def _on_wake_word_detected(self):
        """Wake word algılandığında"""
        
        logger.success("✅ Wake word algılandı!")
        
        if self.tts_engine:
            self.tts_engine.speak("Evet, dinliyorum.")
        
        # Kullanıcıyı dinle ve yanıtla
        self._listen_and_respond()
    
    def _listen_and_respond(self):
        """Kullanıcıyı dinle ve yanıtla"""
        
        try:
            # Mikrofon ile kaydet (5 saniye)
            logger.info("🎤 Dinliyorum... (5 saniye)")
            
            audio = self.stt_engine.record_audio(duration=5)
            
            # Sessizlik kontrolü
            if self.stt_engine.is_audio_silent(audio):
                logger.warning("⚠️  Ses algılanamadı")
                
                if self.tts_engine:
                    self.tts_engine.speak("Sizi duyamadım, tekrar dener misiniz?")
                
                return
            
            # Transkribe et
            logger.info("✍️  Transkribe ediliyor...")
            text = self.stt_engine.transcribe(audio_array=audio)
            
            if not text:
                logger.warning("❌ Transkripsiyon başarısız")
                
                if self.tts_engine:
                    self.tts_engine.speak("Anlamadım, lütfen tekrar edin.")
                
                return
            
            logger.info(f"📝 Kullanıcı: {text}")
            
            # Çıkış komutu kontrolü
            exit_commands = ['çık', 'kapat', 'dur', 'exit', 'quit', 'stop']
            if any(cmd in text.lower() for cmd in exit_commands):
                logger.info("🛑 Çıkış komutu algılandı")
                
                if self.tts_engine:
                    self.tts_engine.speak("Tamam, kapatıyorum. Güle güle!")
                
                raise KeyboardInterrupt
            
            # LLM'den cevap al
            logger.info("🤖 Cevap oluşturuluyor...")
            response = self.llm_manager.generate(text, stream=False)
            
            logger.success(f"💬 Assistant: {response[:100]}...")
            
            # Sesli yanıt
            if self.tts_engine:
                self.tts_engine.speak(response)
            else:
                print(f"\nAssistant: {response}\n")
            
        except Exception as e:
            logger.error(f"Sesli işlem hatası: {e}")
            
            if self.tts_engine:
                self.tts_engine.speak("Üzgünüm, bir hata oluştu.")
