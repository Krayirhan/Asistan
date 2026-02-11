"""
LLM Manager - Qwen2.5-3B Optimized
"""

from typing import List, Dict, Optional
from loguru import logger


class LLMManager:
    """Qwen2.5 ile akıllı sohbet yönetimi"""
    
    def __init__(self, config: dict, model_manager):
        self.config = config['llm']
        self.vlm_config = config['vlm']  # VLM config'i de kaydet
        self.full_config = config  # Tüm config'i de kaydet
        self.model_manager = model_manager
        self.conversation_history: List[Dict] = []
        self.max_history = config['memory']['max_history']
        
        # Web search tool
        self.web_search_enabled = config.get('web_search', {}).get('enabled', True)
        if self.web_search_enabled:
            from tools.web_search import WebSearchTool
            self.web_search = WebSearchTool(config)
            logger.info("Web search tool aktif")
        
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = True
    ) -> str:
        """
        Qwen2.5'ten cevap al
        
        Args:
            prompt: Kullanıcı sorusu
            system_prompt: Sistem talimatı (opsiyonel)
            stream: Kelime kelime göster
        
        Returns:
            Model cevabı
        """
        
        # Web search gerekli mi kontrol et
        search_context = self._check_and_search(prompt)
        
        # Model yükle (lazy loading)
        client = self.model_manager.load_model("llm")
        
        # Konuşma geçmişini ekle
        messages = self._build_messages(prompt, system_prompt, search_context)
        
        # Cevap üret
        logger.info(f"Qwen2.5'e soruluyor: {prompt[:50]}...")
        
        response_text = ""
        
        try:
            if stream:
                # Stream mode
                stream_response = client.chat(
                    model=self.config['model'],
                    messages=messages,
                    stream=True,
                    options={
                        'temperature': self.config['temperature'],
                        'top_p': self.config['top_p'],
                        'repeat_penalty': self.config['repeat_penalty'],
                        'num_predict': self.config['max_tokens'],
                    }
                )
                
                for chunk in stream_response:
                    if 'message' in chunk and 'content' in chunk['message']:
                        token = chunk['message']['content']
                        response_text += token
                        print(token, end='', flush=True)  # Real-time output
                
                print()  # Newline
                
            else:
                # Non-stream mode
                response = client.chat(
                    model=self.config['model'],
                    messages=messages,
                    options={
                        'temperature': self.config['temperature'],
                        'num_predict': self.config['max_tokens'],
                    }
                )
                response_text = response['message']['content']
        
        except Exception as e:
            logger.error(f"LLM hatası: {e}")
            return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
        
        # Geçmişe ekle
        self._update_history(prompt, response_text)
        
        logger.success(f"Cevap alındı ({len(response_text)} karakter)")
        return response_text
    
    def _check_and_search(self, prompt: str) -> Optional[str]:
        """
        Akilli web arama - WebSearchTool.smart_search() kullanir.
        Tum kategori tespiti ve API yonetimi web_search modülünde.
        """
        if not self.web_search_enabled:
            return None
        
        try:
            result = self.web_search.smart_search(prompt)
            if result:
                logger.info(f"Web arama sonucu alindi ({len(result)} karakter)")
            return result
        except Exception as e:
            logger.error(f"Web arama hatasi: {e}")
            return None
    
    def _build_messages(self, prompt: str, system_prompt: Optional[str], search_context: Optional[str] = None) -> List[Dict]:
        """Konusma gecmisi + yeni soru"""
        messages = []
        
        # System prompt
        if system_prompt:
            base_system = system_prompt
        else:
            base_system = (
                "Sen Turkce konusan bir yapay zeka asistanisin. Adin yok, sadece yardimci bir asistansin.\n\n"
                "Nasil konusmalisin:\n"
                "- Her zaman Turkce yaz. Hicbir zaman Ingilizce kelime kullanma.\n"
                "- Kullaniciya 'sen' diye hitap et, 'siz' deme.\n"
                "- Kisa ve oz cevaplar ver. Gereksiz uzatma, tekrar yapma.\n"
                "- Dogal ve rahat bir dil kullan. Robot gibi degil, normal bir insan gibi konus.\n"
                "- Soru soruldugunda dogrudan cevap ver, gereksiz giris cumleleri ekleme.\n"
                "- Kendini tanimlarken abartma. 'Ben bir yapay zeka asistaniyim' de yeter.\n"
                "- Selama kisa selam ver. 'Merhaba!' veya 'Selam!' yeterli, aciklama yapma.\n"
                "- Kelimelerin sozluk anlamini verme, normal cevap ver.\n"
                "- Onceki mesajlari hatirla ve baglam icinde cevap ver.\n"
                "- Internetten gelen verilerdeki sayilari oldugu gibi kullan, degistirme."
            )
        
        # GUNCEL BILGILERI SYSTEM MESSAGE'A EKLE
        if search_context:
            logger.info(f"Search context ekleniyor ({len(search_context)} karakter)")
            
            system_with_context = (
                f"{base_system}\n\n"
                f"--- GUNCEL BILGILER (INTERNETTEN ALINMISTIR) ---\n"
                f"{search_context}\n"
                f"--- BILGI SONU ---\n\n"
                f"ONEMLI: Yukaridaki bilgilerdeki sayilari (sicaklik, kur, fiyat vb.) "
                f"oldugu gibi kullan. Degistirme, yuvarlama, tahmin yapma. "
                f"Kaynak belirtme, sadece bilgiyi dogal sekilde aktar."
            )
            messages.append({"role": "system", "content": system_with_context})
        else:
            messages.append({"role": "system", "content": base_system})
        
        # Son N mesaji ekle (sliding window)
        recent_history = self.conversation_history[-self.max_history * 2:]
        messages.extend(recent_history)
        
        # Yeni soru
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _update_history(self, user_msg: str, assistant_msg: str):
        """Konuşma geçmişini güncelle"""
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})
        
        # Limit aşarsa eski mesajları sil (FIFO)
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]
    
    def clear_history(self):
        """Geçmişi temizle"""
        self.conversation_history = []
        logger.info("Konuşma geçmişi temizlendi")
    
    def analyze_image(self, image_path: str, question: str = "Bu resimde ne var?") -> str:
        """
        LLaVA ile görsel analiz
        
        Args:
            image_path: Resim dosya yolu
            question: Resim hakkında soru
        
        Returns:
            Görsel açıklaması
        """
        # VLM yükle (LLM'i boşalt)
        self.model_manager.unload_model("llm")
        client = self.model_manager.load_model("vlm")
        
        logger.info(f"Görsel analiz ediliyor: {image_path}")
        
        try:
            response = client.chat(
                model=self.vlm_config['model'],  # vlm_config kullan
                messages=[{
                    "role": "user",
                    "content": question,
                    "images": [image_path]
                }]
            )
            
            result = response['message']['content']
            logger.success(f"Görsel analiz tamamlandı (İngilizce) - Cevap: {result[:100]}...")
            
            # Boş cevap kontrolü
            if not result or result.strip() == "":
                logger.warning("Moondream boş cevap döndürdü, varsayılan mesaj kullanılıyor")
                result = "Üzgünüm, bu resmi analiz edemedim. Lütfen daha net bir resim deneyin veya sorunuzu değiştirin."
                self.model_manager.unload_model("vlm")
                return result
            
            # VLM'i boşalt, LLM'i geri yükle
            self.model_manager.unload_model("vlm")
            
            # Cevabı Türkçe'ye çevir
            logger.info("Cevap Türkçe'ye çevriliyor...")
            llm_client = self.model_manager.load_model("llm")
            
            translate_response = llm_client.chat(
                model=self.config['model'],  # self.config kullan (llm config'i zaten __init__'te self.config'e atandı)
                messages=[{
                    "role": "system",
                    "content": "Sen bir çevirmen asistansın. İngilizce metinleri akıcı Türkçe'ye çevirirsin."
                }, {
                    "role": "user",
                    "content": f"Aşağıdaki İngilizce metni Türkçe'ye çevir:\n\n{result}"
                }],
                options={
                    "temperature": 0.3  # Çeviri için düşük temperature
                }
            )
            
            turkish_result = translate_response['message']['content']
            logger.success(f"Türkçe çeviri tamamlandı: {turkish_result[:100]}...")
            
            return turkish_result
            
        except Exception as e:
            logger.error(f"Görsel analiz hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Resmi analiz edemedim. Hata: {str(e)}"
    
    def get_history_summary(self) -> str:
        """Konuşma geçmişinin özetini ver"""
        if not self.conversation_history:
            return "Henüz konuşma yok."
        
        total = len(self.conversation_history) // 2
        return f"Toplam {total} mesaj geçmişi var."
