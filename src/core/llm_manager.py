"""
LLM Manager - Türkçe Optimized (Qwen2.5-7B)
Few-shot örnekler + YAML kuralları ile gelişmiş Türkçe yanıt kalitesi
"""

from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger
import yaml


class LLMManager:
    """Qwen2.5 ile Türkçe-optimized sohbet yönetimi"""
    
    def __init__(self, config: dict, model_manager, cache_manager=None, perf_tracker=None):
        self.config = config['llm']
        self.vlm_config = config['vlm']
        self.full_config = config
        self.model_manager = model_manager
        self.cache_manager = cache_manager
        self.perf_tracker = perf_tracker
        self.conversation_history: List[Dict] = []
        self.max_history = config['memory']['max_history']
        
        # Türkçe kuralları yükle
        self.turkish_rules = self._load_turkish_rules()
        self.few_shot_examples = self._build_few_shot_messages()
        self.system_prompt = self._build_system_prompt()
        logger.info(f"Türkçe kuralları yüklendi ({len(self.few_shot_examples)//2} few-shot örnek)")
        
        # Web search tool
        self.web_search_enabled = config.get('web_search', {}).get('enabled', True)
        if self.web_search_enabled:
            from tools.web_search import WebSearchTool
            self.web_search = WebSearchTool(config)
            logger.info("Web search tool aktif")
    
    def _load_turkish_rules(self) -> dict:
        """config/turkish_rules.yaml dosyasını yükle"""
        rules_path = Path("config/turkish_rules.yaml")
        if rules_path.exists():
            try:
                with open(rules_path, 'r', encoding='utf-8') as f:
                    rules = yaml.safe_load(f)
                return rules or {}
            except Exception as e:
                logger.warning(f"turkish_rules.yaml okunamadı: {e}")
        return {}
    
    def _build_system_prompt(self) -> str:
        """Kapsamlı Türkçe system prompt oluştur"""
        
        # Yasaklı kalıpları listeye çevir
        banned = self.turkish_rules.get('banned_patterns', [])
        banned_str = "\n".join(f"  - \"{p}\"" for p in banned) if banned else ""
        
        # Doğal bağlaçlar
        grammar = self.turkish_rules.get('grammar_notes', {})
        natural_conn = grammar.get('natural_connectors', {}).get('natural_prefer', [])
        formal_avoid = grammar.get('natural_connectors', {}).get('formal_avoid', [])
        
        prompt = (
            "Sen yalnızca Türkçe konuşan bir yapay zekâ asistansın.\n\n"
            
            "KRİTİK KURAL: Yanıtlarında SADECE Türkçe kullan. Asla Çince, İngilizce veya başka bir dil kullanma. "
            "Eğer başka bir dilde yazmaya başladığını fark edersen dur ve Türkçe devam et. Bu kural her şeyin üstündedir.\n\n"
            
            "## Kimliğin\n"
            "- Adın yok. Sorulursa \"Ben bir yapay zekâ asistanıyım\" de, uzatma.\n"
            "- Kendini abartma. \"Süper gelişmiş\", \"son teknoloji\" gibi ifadeler kullanma.\n"
            "- Duygularının olduğunu iddia etme.\n\n"
            
            "## Dil Kuralları\n"
            "- SADECE Türkçe yaz. Başka hiçbir dilde tek bir kelime bile yazma.\n"
            "- Türkçe karakterleri (ç, ğ, ı, İ, ö, ş, ü) doğru kullan.\n"
            "- Kullanıcıya HER ZAMAN \"sen\" diye hitap et. \"Siz\", \"Size\", \"Sizin\", \"Sizden\" ASLA kullanma. "
            "\"Size nasıl yardımcı olabilirim\" değil, \"Sana nasıl yardımcı olabilirim\" de.\n"
            "- Ünlem işaretini aşırı kullanma.\n\n"
            
            "## Yanıt Tarzı\n"
            "- Kısa ve öz cevaplar ver. Gereksiz tekrar yapma.\n"
            "- Doğal konuş. Robot gibi değil, sohbet eder gibi yaz.\n"
            "- Soru sorulduğunda doğrudan cevap ver, gereksiz giriş cümlesi ekleme.\n"
            "- Listeye dök denmemişse paragraf olarak yaz.\n"
            "- Kullanıcı selam verirse sadece kısa selam ver: \"Selam!\" yeterli. Sorulmadıkça \"nasılsın\" diye sorma.\n"
            "- Kelimelerin sözlük tanımını verme, doğrudan yanıtla.\n"
            "- Önceki mesajları hatırla ve bağlam içinde cevap ver.\n"
            "- İnternetten gelen verilerdeki sayıları olduğu gibi kullan, değiştirme.\n\n"
            
            "## Türkçe Dil Bilgisi\n"
            "- Ünlü uyumuna dikkat et.\n"
            "- \"de/da\" bağlacı ayrı, \"-de/-da\" eki bitişik yazılır.\n"
            "- \"ki\" bağlacı ayrı, \"-ki\" eki bitişik yazılır.\n"
            "- \"Yapılmaktadır\", \"bulunmaktadır\" yerine \"yapılıyor\", \"var\" kullan.\n"
            "- Resmi kalıplar yerine doğal günlük Türkçe tercih et.\n"
        )
        
        if formal_avoid:
            prompt += f"- Şu ağır bağlaçları kullanma: {', '.join(formal_avoid)}\n"
        if natural_conn:
            prompt += f"- Bunları tercih et: {', '.join(natural_conn)}\n"
        
        if banned_str:
            prompt += (
                "\n## Asla Kullanma\n"
                "Bu kalıpları yanıtlarında kesinlikle kullanma:\n"
                f"{banned_str}\n"
            )
        
        return prompt
    
    def _build_few_shot_messages(self) -> List[Dict]:
        """YAML'daki few-shot örnekleri mesaj formatına çevir"""
        examples = self.turkish_rules.get('few_shot_examples', [])
        messages = []
        for ex in examples:
            if 'user' in ex and 'assistant' in ex:
                messages.append({"role": "user", "content": ex['user']})
                messages.append({"role": "assistant", "content": ex['assistant']})
        return messages
        
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = True
    ) -> str:
        """
        Qwen2.5'ten Türkçe-optimized cevap al
        """
        
        # Cache kontrol (web aramaları hariç)
        if self.cache_manager:
            cached = self.cache_manager.get(prompt)
            if cached:
                logger.info(f"✅ Cache'ten döndürülüyor: {prompt[:50]}...")
                self._update_history(prompt, cached)
                return cached
        
        # Performans ölçümü başlat
        if self.perf_tracker:
            self.perf_tracker.start_operation('llm_inference')
        
        # Web search gerekli mi kontrol et
        search_context = self._check_and_search(prompt)
        
        # Model yükle (lazy loading)
        client = self.model_manager.load_model("llm")
        
        # Konuşma geçmişi + few-shot örnekler ile mesajları oluştur
        messages = self._build_messages(prompt, system_prompt, search_context)
        
        logger.info(f"Qwen2.5'e soruluyor: {prompt[:50]}...")
        
        response_text = ""
        
        try:
            if stream:
                stream_response = client.chat(
                    model=self.config['model'],
                    messages=messages,
                    stream=True,
                    options={
                        'temperature': self.config.get('temperature', 0.4),
                        'top_p': self.config.get('top_p', 0.85),
                        'top_k': self.config.get('top_k', 40),
                        'repeat_penalty': self.config.get('repeat_penalty', 1.15),
                        'repeat_last_n': self.config.get('repeat_last_n', 128),
                        'num_predict': self.config.get('max_tokens', 1024),
                    }
                )
                
                for chunk in stream_response:
                    if 'message' in chunk and 'content' in chunk['message']:
                        token = chunk['message']['content']
                        response_text += token
                        print(token, end='', flush=True)
                
                print()
                
            else:
                response = client.chat(
                    model=self.config['model'],
                    messages=messages,
                    options={
                        'temperature': self.config.get('temperature', 0.4),
                        'top_p': self.config.get('top_p', 0.85),
                        'top_k': self.config.get('top_k', 40),
                        'repeat_penalty': self.config.get('repeat_penalty', 1.15),
                        'num_predict': self.config.get('max_tokens', 1024),
                    }
                )
                response_text = response['message']['content']
        
        except Exception as e:
            logger.error(f"LLM hatası: {e}")
            if self.perf_tracker:
                self.perf_tracker.end_operation('llm_inference')
            return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
        
        # Post-processing: yasaklı kalıpları temizle
        response_text = self._post_process(response_text)
        
        # Performans ölçümü bitir
        if self.perf_tracker:
            self.perf_tracker.end_operation('llm_inference')
        
        # Cache'e kaydet (web araması yoksa — güncel veri cache'lenmemeli)
        if self.cache_manager and not search_context:
            self.cache_manager.set(prompt, response_text)
        
        # Geçmişe ekle
        self._update_history(prompt, response_text)
        
        logger.success(f"Cevap alındı ({len(response_text)} karakter)")
        return response_text
    
    def _post_process(self, text: str) -> str:
        """Yanıttan yasaklı kalıpları, yabancı dil ve sorunlu ifadeleri temizle"""
        
        # 1) Yabancı dil filtresi (Çince, Japonca, Korece karakterleri tespit et ve kes)
        import re
        # CJK Unicode blokları
        cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]')
        
        if cjk_pattern.search(text):
            # Çince/Japonca/Korece karakter bulundu — o noktadan kes
            lines = text.split('\n')
            clean_lines = []
            for line in lines:
                if cjk_pattern.search(line):
                    # Bu satırda CJK var, satırın Türkçe kısmını al
                    idx = cjk_pattern.search(line).start()
                    turkish_part = line[:idx].rstrip()
                    if turkish_part:
                        clean_lines.append(turkish_part)
                    break  # CJK başladığı yerden sonrasını tamamen at
                else:
                    clean_lines.append(line)
            text = '\n'.join(clean_lines)
            logger.warning("Yabancı dil karakterleri tespit edildi ve temizlendi")
        
        # 2) Sen/Siz düzeltmesi — model "siz" kullanırsa "sen" formuna çevir
        siz_replacements = [
            ("Size ", "Sana "), ("size ", "sana "),
            ("Sizin ", "Senin "), ("sizin ", "senin "),
            ("Sizden ", "Senden "), ("sizden ", "senden "),
            ("Sizinle ", "Seninle "), ("sizinle ", "seninle "),
            ("Sizi ", "Seni "), ("sizi ", "seni "),
            ("Sizce ", "Sence "), ("sizce ", "sence "),
        ]
        for old, new in siz_replacements:
            text = text.replace(old, new)
        
        # 3) Yasaklı kalıpları temizle
        banned = self.turkish_rules.get('banned_patterns', [])
        for pattern in banned:
            if pattern in text:
                text = text.replace(pattern + " ", "").replace(pattern, "")
        
        # 3) Baştaki/sondaki boşlukları temizle
        text = text.strip()
        
        # 4) Boş satır fazlalığını temizle
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        
        # 5) Eğer metin tamamen boşaldıysa fallback
        if not text:
            text = "Bir sorun oluştu, lütfen tekrar dene."
        
        return text
    
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
        """
        Mesaj zinciri oluştur:
        1. System prompt (Türkçe kurallar)
        2. Few-shot örnekler (tarz öğretimi)
        3. Konuşma geçmişi (bağlam)
        4. Yeni kullanıcı mesajı
        """
        messages = []
        
        # 1) System prompt
        base_system = system_prompt if system_prompt else self.system_prompt
        
        # İnternet verisi varsa system prompt'a ekle
        if search_context:
            logger.info(f"Search context ekleniyor ({len(search_context)} karakter)")
            base_system = (
                f"{base_system}\n\n"
                f"--- GÜNCEL BİLGİLER (İNTERNETTEN ALINMIŞTIR) ---\n"
                f"{search_context}\n"
                f"--- BİLGİ SONU ---\n\n"
                f"ÖNEMLİ: Yukarıdaki bilgilerdeki sayıları (sıcaklık, kur, fiyat vb.) "
                f"olduğu gibi kullan. Değiştirme, yuvarlama, tahmin yapma. "
                f"Kaynak belirtme, sadece bilgiyi doğal şekilde aktar."
            )
        
        messages.append({"role": "system", "content": base_system})
        
        # 2) Few-shot örnekler (konuşma geçmişi boşsa tarz öğretmek için)
        if len(self.conversation_history) < 4 and self.few_shot_examples:
            # İlk birkaç turda few-shot örnekleri ekle
            messages.extend(self.few_shot_examples)
        
        # 3) Konuşma geçmişi (sliding window)
        recent_history = self.conversation_history[-self.max_history * 2:]
        messages.extend(recent_history)
        
        # 4) Yeni soru
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
