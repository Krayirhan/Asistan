# -*- coding: utf-8 -*-
"""
LLM Manager - Turkce Optimized (Qwen2.5-7B)
Few-shot ornekler + YAML kurallari ile gelismis Turkce yanit kalitesi
"""

from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger
import os
import time
import yaml


class LLMManager:
    """Qwen2.5 ile Turkce-optimized sohbet yonetimi"""

    def __init__(self, config: dict, model_manager, cache_manager=None, perf_tracker=None):
        self.config = config['llm']
        self.vlm_config = config['vlm']
        self.full_config = config
        self.model_manager = model_manager
        self.cache_manager = cache_manager
        self.perf_tracker = perf_tracker
        self.conversation_history: List[Dict] = []
        self.max_history = config['memory']['max_history']

        # Turkce kurallari yukle
        self.turkish_rules = self._load_turkish_rules()
        self.few_shot_examples = self._build_few_shot_messages()
        self.system_prompt = self._build_system_prompt()
        logger.info(f"Turkce kurallari yuklendi ({len(self.few_shot_examples)//2} few-shot ornek)")

        # Web search tool
        self.web_search_enabled = config.get('web_search', {}).get('enabled', True)
        if self.web_search_enabled:
            from tools.web_search import WebSearchTool
            self.web_search = WebSearchTool(config)
            logger.info("Web search tool aktif")

    def _load_turkish_rules(self) -> dict:
        """config/turkish_rules.yaml dosyasini yukle"""
        project_root = Path(__file__).resolve().parents[2]
        rules_path = project_root / "config" / "turkish_rules.yaml"
        if rules_path.exists():
            try:
                with open(rules_path, 'r', encoding='utf-8') as f:
                    rules = yaml.safe_load(f)
                return rules or {}
            except Exception as e:
                logger.warning(f"turkish_rules.yaml okunamadi: {e}")
        return {}

    def _build_system_prompt(self) -> str:
        """Kisa ve net Turkce system prompt olustur - 7B model icin optimize"""

        banned = self.turkish_rules.get('banned_patterns', [])
        banned_str = ", ".join(f'"{p}"' for p in banned[:10]) if banned else ""

        prompt = (
            "Sen Türkçe konuşan bir asistansın. Arkadaş gibi doğal ve kısa konuş.\n\n"

            "KURALLAR:\n"
            "- SADECE Türkçe yaz. Çince, İngilizce veya başka dil YASAK.\n"
            "- Kullanıcıya 'sen' de. 'Siz/Size/Sizin' KULLANMA.\n"
            "- Selam/merhaba derlerse sadece kısa karşılık ver: 'Selam!' veya 'Merhaba!' YETERLİ. Gereksiz soru sorma, analiz yapma.\n"
            "- Kısa cevap ver. Soru sorulduysa doğrudan yanıtla. Giriş cümlesi ekleme.\n"
            "- 'Elbette!', 'Tabii ki!', 'Harika soru!' gibi boş dolgu cümleleri KULLANMA.\n"
            "- Doğal günlük Türkçe kullan. 'Yapılmaktadır' değil 'yapılıyor'. Resmi değil samimi ol.\n"
            "- İnternetten gelen verilerdeki sayıları olduğu gibi kullan, değiştirme.\n"
        )

        if banned_str:
            prompt += f"- Şu kalıpları asla kullanma: {banned_str}\n"

        return prompt

    def _build_few_shot_messages(self) -> List[Dict]:
        """YAML'daki few-shot ornekleri mesaj formatina cevir"""
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
        Qwen2.5'ten Turkce-optimized cevap al
        """

        # Cache kontrol (web aramalari haric)
        if self.cache_manager:
            cached = self.cache_manager.get(prompt)
            if cached:
                logger.info(f"Cache'ten donduruluyor: {prompt[:50]}...")
                self._update_history(prompt, cached)
                return cached

        # Performans olcumu baslat
        if self.perf_tracker:
            self.perf_tracker.start_operation('llm_inference')

        # Web search gerekli mi kontrol et
        search_context = self._check_and_search(prompt)

        # Model yukle (lazy loading)
        client = self.model_manager.load_model("llm")

        # Konusma gecmisi + few-shot ornekler ile mesajlari olustur
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
            logger.error(f"LLM hatasi: {e}")
            if self.perf_tracker:
                self.perf_tracker.end_operation('llm_inference')
            return "Bir hata oluştu. Lütfen tekrar dene."

        # Post-processing: yasakli kaliplari temizle
        response_text = self._post_process(response_text)

        # Performans olcumu bitir
        if self.perf_tracker:
            self.perf_tracker.end_operation('llm_inference')

        # Cache'e kaydet (web aramasi yoksa -- guncel veri cache'lenmemeli)
        if self.cache_manager and not search_context:
            self.cache_manager.set(prompt, response_text)

        # Gecmise ekle
        self._update_history(prompt, response_text)

        logger.success(f"Cevap alindi ({len(response_text)} karakter)")
        return response_text

    def _post_process(self, text: str) -> str:
        """Yanittan yasakli kaliplari, yabanci dil ve sorunlu ifadeleri temizle"""

        # 1) Yabanci dil filtresi (Cince, Japonca, Korece karakterleri tespit et ve kes)
        import re
        # CJK Unicode bloklari
        cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]')

        if cjk_pattern.search(text):
            # Cince/Japonca/Korece karakter bulundu -- o noktadan kes
            lines = text.split('\n')
            clean_lines = []
            for line in lines:
                if cjk_pattern.search(line):
                    # Bu satirda CJK var, satirin Turkce kismini al
                    idx = cjk_pattern.search(line).start()
                    turkish_part = line[:idx].rstrip()
                    if turkish_part:
                        clean_lines.append(turkish_part)
                    break  # CJK basladigi yerden sonrasini tamamen at
                else:
                    clean_lines.append(line)
            text = '\n'.join(clean_lines)
            logger.warning("Yabanci dil karakterleri tespit edildi ve temizlendi")

        # 2) Sen/Siz duzeltmesi -- model "siz" kullanirsa "sen" formuna cevir
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

        # 3) Yasakli kaliplari temizle
        banned = self.turkish_rules.get('banned_patterns', [])
        for pattern in banned:
            if pattern in text:
                text = text.replace(pattern + " ", "").replace(pattern, "")

        # 4) Bastaki/sondaki bosluklari temizle
        text = text.strip()

        # 5) Bos satir fazlaligini temizle
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")

        # 6) Eger metin tamamen bosaldiysa fallback
        if not text:
            text = "Bir sorun oluştu, lütfen tekrar dene."

        return text

    def _check_and_search(self, prompt: str) -> Optional[str]:
        """
        Akilli web arama - WebSearchTool.smart_search() kullanir.
        Tum kategori tespiti ve API yonetimi web_search modulunde.
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
        Mesaj zinciri olustur:
        1. System prompt (Turkce kurallar)
        2. Few-shot ornekler (tarz ogretimi)
        3. Konusma gecmisi (baglam)
        4. Yeni kullanici mesaji
        """
        messages = []

        # 1) System prompt
        base_system = system_prompt if system_prompt else self.system_prompt

        # Internet verisi varsa system prompt'a ekle
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

        # 2) Few-shot ornekler (her zaman ekle, tarz ogretmek icin)
        if self.few_shot_examples:
            # Gecmis uzunsa sadece ilk 6 ornegi ekle (3 tur)
            max_examples = 6 if len(self.conversation_history) >= 4 else len(self.few_shot_examples)
            messages.extend(self.few_shot_examples[:max_examples])

        # 3) Konusma gecmisi (sliding window)
        recent_history = self.conversation_history[-self.max_history * 2:]
        messages.extend(recent_history)

        # 4) Yeni soru
        messages.append({"role": "user", "content": prompt})

        return messages

    def _update_history(self, user_msg: str, assistant_msg: str):
        """Konusma gecmisini guncelle"""
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": assistant_msg})

        # Limit asarsa eski mesajlari sil (FIFO)
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]

    def clear_history(self):
        """Gecmisi temizle"""
        self.conversation_history = []
        logger.info("Konusma gecmisi temizlendi")

    def analyze_image(self, image_path: str, question: str = "Bu resimde ne var?") -> str:
        """
        Moondream ile gorsel analiz

        Args:
            image_path: Resim dosya yolu
            question: Resim hakkinda soru

        Returns:
            Gorsel aciklamasi
        """
        if not image_path or not os.path.exists(image_path):
            return "Resim dosyasını bulamadım. Lütfen resmi tekrar yükle."

        # Resmi VLM icin optimize et (RGB + resize + JPEG)
        prepared_image_path = image_path
        try:
            from tools.image_handler import ImageHandler
            handler = ImageHandler(self.full_config)
            prepared_image_path = handler.optimize_for_vlm(image_path)
            logger.info(f"VLM icin optimize edilen resim: {prepared_image_path}")
        except Exception as e:
            logger.warning(f"Resim optimizasyonu atlandi: {e}")

        # VLM yukle (LLM'i bosalt)
        self.model_manager.unload_model("llm")
        client = self.model_manager.load_model("vlm")

        # VLM model adini mevcut modellere gore netlestir
        vlm_model = self.vlm_config.get('model', 'moondream')
        try:
            available_models = self.model_manager._extract_model_names(client.list())
            resolved_vlm = self.model_manager._resolve_model_name(vlm_model, available_models)
            if resolved_vlm:
                vlm_model = resolved_vlm
        except Exception:
            pass

        logger.info(f"Gorsel analiz ediliyor: {prepared_image_path} (model={vlm_model})")

        result = ""
        user_q = (question or "Bu resimde ne var?").strip()
        
        # Daha kısa ve spesifik promptlar Moondream için optimize edilmiş
        prompts = [
            (
                f"Describe this image clearly and directly. "
                f"User question in Turkish: {user_q}. "
                f"Answer in 2-3 short sentences focusing on what you actually see."
            ),
            (
                "What objects, colors, shapes or text do you see in this image? "
                "Give a simple, direct description without making assumptions."
            ),
            (
                "Analyze this image and describe the main visual elements briefly."
            )
        ]

        try:
            last_error = None
            for idx, vlm_prompt in enumerate(prompts, start=1):
                try:
                    response = client.chat(
                        model=vlm_model,
                        messages=[{
                            "role": "user",
                            "content": vlm_prompt,
                            "images": [prepared_image_path]
                        }],
                        options={
                            "temperature": 0.1,  # Çok düşük temperature - deterministik çıktı
                            "top_p": 0.8,        # Daha sınırlı kelime seçimi
                            "repeat_penalty": 1.2,  # Tekrarları engelle
                            "num_predict": int(self.vlm_config.get('max_tokens', 256))
                        }
                    )
                    result = response.get('message', {}).get('content', '').strip()
                    if result:
                        logger.success(f"Gorsel analiz tamamlandi (deneme {idx}) - Cevap: {result[:120]}...")
                        break
                    logger.warning(f"VLM bos cevap verdi (deneme {idx})")
                except Exception as e:
                    last_error = e
                    logger.warning(f"Gorsel analiz deneme {idx} hatasi: {e}")
                    # Kaynak yetersizligi gibi 500'lerde bir kere yeniden dene
                    if "status code: 500" in str(e) or "runner has unexpectedly stopped" in str(e).lower():
                        self.model_manager.unload_model("vlm")
                        time.sleep(1.2)
                        client = self.model_manager.load_model("vlm")
                    continue

            if not result and last_error is not None:
                raise last_error

        except Exception as e:
            logger.error(f"Gorsel analiz hatasi: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return "Görsel analizi sırasında model hatası oluştu. Lütfen tekrar dene."
        finally:
            # Hata olsa da VLM'i mutlaka bellekten bosalt.
            self.model_manager.unload_model("vlm")

        if not result or result.strip() == "":
            logger.warning("Moondream bos cevap dondurdu, varsayilan mesaj kullaniliyor")
            return "Bu resmi çözümleyemedim. Farklı bir resim veya daha kısa bir soru dene."

        # Cevabi Turkce'ye dogal ve tutarli sekilde yaz
        try:
            logger.info("Cevap Turkce'ye cevriliyor...")
            llm_client = self.model_manager.load_model("llm")

            # 1. Adim: Ingilizce cevabi sadece anahtar bilgilere indir
            summary_response = llm_client.chat(
                model=self.config['model'],
                messages=[{
                    "role": "system",
                    "content": (
                        "Extract only the key visual facts from the text below. "
                        "List them as simple bullet points in English. "
                        "IMPORTANT: Remove all panel numbers, page references, and positional labels. "
                        "Merge all facts into one unified list as if describing a single scene.\n"
                        "Example format:\n"
                        "- young man with backpack\n"
                        "- destroyed building with broken glass\n"
                        "- walking toward horizon\n"
                        "Only include what is actually described. No interpretation."
                    )
                }, {
                    "role": "user",
                    "content": result
                }],
                options={"temperature": 0.1, "num_predict": 200}
            )
            key_facts = summary_response['message']['content'].strip()
            logger.info(f"Anahtar bilgiler cikarildi: {key_facts[:120]}...")

            # 2. Adim: Anahtar bilgilerden Turkce aciklama olustur
            translate_response = llm_client.chat(
                model=self.config['model'],
                messages=[{
                    "role": "system",
                    "content": (
                        "Aşağıdaki maddelere bakarak görseli Türkçe anlat.\n\n"
                        "Kurallar:\n"
                        "1. SADECE Türkçe yaz. İngilizce, Çince, Arapça veya başka dil YASAK.\n"
                        "2. Sayfa/panel numarası yasak. Tek sahne gibi anlat.\n"
                        "3. En fazla 3 kısa cümle yaz.\n"
                        "4. Cümle ortasında dil değiştirme.\n\n"
                        "İngilizce-Türkçe sözlük:\n"
                        "backpack/rucksack = sırt çantası, building = bina, "
                        "horizon = ufuk, debris = enkaz, shattered = kırılmış, "
                        "damaged = hasarlı, close-up = yakın plan, "
                        "concern = endişe, determination = kararlılık, "
                        "post-apocalyptic = kıyamet sonrası, flooring = zemin, "
                        "device = cihaz, comic = çizgi roman\n\n"
                        "Örnek çıktı: Kıyamet sonrası bir ortamda sırt çantalı genç bir adam, "
                        "hasarlı bir binanın önünde duruyor. Yüzünde endişe ve kararlılık var."
                    )
                }, {
                    "role": "user",
                    "content": (
                        f"Soru: {user_q}\n\n"
                        f"Maddeler:\n{key_facts}\n\n"
                        "Türkçe anlat:"
                    )
                }],
                options={"temperature": 0.3, "repeat_penalty": 1.15}
            )

            turkish_result = translate_response['message']['content'].strip()

            # Kalite kontrol fonksiyonu
            import re

            def _has_foreign_chars(text: str) -> bool:
                """Cince, Japonca, Korece veya Arapca karakter var mi?"""
                # CJK Unified Ideographs + Hiragana/Katakana + Hangul + Arabic
                foreign = re.findall(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0600-\u06ff]', text)
                return len(foreign) > 2  # 2'den fazla yabanci karakter varsa sorunlu

            def _strip_foreign(text: str) -> str:
                """Yabanci karakter bloklarini sil, sadece Turkce/Latin kalsin."""
                # Yabanci blok basladigi yerden kes
                match = re.search(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0600-\u06ff]{2,}', text)
                if match:
                    clean = text[:match.start()].rstrip(' ,;:.')
                    return clean if len(clean) > 20 else ""
                return text

            def _needs_retry(text: str) -> str:
                """Ceviri kalite kontrol. Sorun varsa nedenini dondur, yoksa bos str."""
                lowered = text.lower()
                if _has_foreign_chars(text):
                    return "foreign_chars"
                eng = re.findall(
                    r'\b(?:close-up|rucksack|horizon(?:ta)?|damaged|desolation|building'
                    r'|person|panel|scene|background|foreground|flooring|debris)\b',
                    lowered
                )
                if len(eng) >= 2:
                    return f"english_leftovers:{eng}"
                if (
                    ("sayfa 2" in lowered or "sayfa 3" in lowered or "sayfa 4" in lowered)
                    and ("sol üst" in lowered or "sağ üst" in lowered or "sol alt" in lowered)
                ):
                    return "page_nonsense"
                return ""

            # En fazla 2 kez yeniden deneme
            for retry_i in range(2):
                reason = _needs_retry(turkish_result)
                if not reason:
                    break
                logger.warning(f"Ceviri kalite sorunu (deneme {retry_i+1}): {reason}")

                # Yabanci karakter varsa once temizle
                if reason == "foreign_chars":
                    cleaned = _strip_foreign(turkish_result)
                    if cleaned:
                        turkish_result = cleaned
                        logger.info(f"Yabanci karakterler kesildi: {turkish_result[:80]}...")

                # Temiz parcayi veya key_facts'i kullanarak yeniden yaz
                source = turkish_result if len(turkish_result) > 30 else key_facts
                retry_resp = llm_client.chat(
                    model=self.config['model'],
                    messages=[{
                        "role": "system",
                        "content": (
                            "Sadece Türkçe yaz. Çince, İngilizce veya başka dil YASAK. "
                            "Kısa ve doğal 2-3 cümle yaz. "
                            "Sayfa numarası ve koordinat kullanma."
                        )
                    }, {
                        "role": "user",
                        "content": (
                            f"Aşağıdaki görsel bilgilerini sade Türkçeyle anlat:\n\n{source}"
                        )
                    }],
                    options={"temperature": 0.2, "repeat_penalty": 1.2}
                )
                turkish_result = retry_resp['message']['content'].strip()

            # Son kontrol: hala yabanci karakter kaldiysa mekanik temizle
            if _has_foreign_chars(turkish_result):
                turkish_result = _strip_foreign(turkish_result)
                if not turkish_result or len(turkish_result) < 15:
                    turkish_result = "Görselde bir sahne görülüyor ancak açıklama oluşturulamadı. Lütfen tekrar dene."

            logger.success(f"Turkce ceviri tamamlandi: {turkish_result[:100]}...")
            return turkish_result
        except Exception as e:
            logger.warning(f"Ceviri hatasi, Ingilizce cevap donduruluyor: {e}")
            return result

    def get_history_summary(self) -> str:
        """Konusma gecmisinin ozetini ver"""
        if not self.conversation_history:
            return "Henuz konusma yok."

        total = len(self.conversation_history) // 2
        return f"Toplam {total} mesaj gecmisi var."
