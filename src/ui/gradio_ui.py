# -*- coding: utf-8 -*-
"""
AI Sesli Asistan - Gradio UI
Tek sayfa: Sohbet + Ses + Görsel — hepsi bir arada
"""

from loguru import logger
import numpy as np

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False


CUSTOM_CSS = """
/* Genel */
.gradio-container { max-width: 820px !important; margin: 0 auto !important; }
footer { display: none !important; }

/* Başlık */
.app-title { text-align:center; padding:14px 0 4px; }
.app-title h1 { margin:0; font-size:22px; font-weight:700;
                 background:linear-gradient(135deg,#6366f1,#8b5cf6);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.app-title p { margin:2px 0 0; font-size:11px; opacity:0.35; }

/* Chatbot */
.chatbot-wrap { border-radius:12px !important; }

/* Ana gönder butonu */
.btn-send { background:linear-gradient(135deg,#6366f1,#7c3aed) !important;
            border:none !important; color:#fff !important; font-weight:600 !important;
            border-radius:10px !important; min-height:42px !important;
            box-shadow:0 2px 8px rgba(99,102,241,0.25) !important; }
.btn-send:hover { box-shadow:0 4px 14px rgba(99,102,241,0.4) !important; }

/* Sesli gönder */
.btn-mic { background:#f0fdf4 !important; border:2px solid #86efac !important;
           color:#16a34a !important; font-weight:600 !important;
           border-radius:10px !important; min-height:42px !important; }

/* Küçük butonlar */
.btn-sm { border-radius:8px !important; font-size:13px !important; }
.btn-clear { border:1px solid #fecaca !important; color:#dc2626 !important; }
.btn-ghost { border:1px solid #e2e8f0 !important; }

/* Analiz butonu */
.btn-analyze { background:linear-gradient(135deg,#8b5cf6,#a855f7) !important;
               border:none !important; color:#fff !important; font-weight:600 !important;
               border-radius:10px !important; }

/* Sistem tablosu */
.sys-tbl { width:100%; border-collapse:collapse; font-size:12px; }
.sys-tbl td { padding:5px 6px; border-bottom:1px solid rgba(0,0,0,0.04); }
.sys-tbl td:first-child { opacity:0.45; width:42%; }
.sys-tbl td:last-child { font-weight:600; }

/* Accordion */
.accordion-compact { margin-top:4px !important; }
"""


class GradioUI:
    def __init__(self, config, llm_manager, stt_engine, tts_engine):
        self.config = config
        self.llm = llm_manager
        self.stt = stt_engine
        self.tts = tts_engine
        self.port = config['ui']['gui'].get('server_port', 7860)
        self.share = config['ui']['gui'].get('share', False)
        self.auth = self._resolve_auth(config['ui']['gui'].get('auth'))

        if not GRADIO_AVAILABLE:
            self.interface = None
            return
        self._build()

    def _resolve_auth(self, auth_config):
        """Convert ui.gui.auth config into a Gradio auth tuple."""
        if auth_config is None:
            return None
        if isinstance(auth_config, (list, tuple)) and len(auth_config) == 2:
            return (str(auth_config[0]), str(auth_config[1]))
        logger.warning("ui.gui.auth invalid; authentication disabled")
        return None

    # ─────────────────────────────────────────────
    # ANA ARAYÜZ — tek sayfa, her şey bir arada
    # ─────────────────────────────────────────────

    def _build(self):
        with gr.Blocks(title="AI Asistan") as app:

            # Başlık
            gr.HTML('<div class="app-title"><h1>\U0001f916 AI Asistan</h1>'
                    '<p>Türkçe \u00b7 Qwen 7B \u00b7 RTX 2060S</p></div>')

            # — Sohbet alanı —
            chatbot = gr.Chatbot(
                height=420,
                placeholder="\U0001f4ac Merhaba! Aşağıdan yazabilir veya mikrofon kullanabilirsin.",
                elem_classes=["chatbot-wrap"],
            )
            last_resp = gr.State("")

            # — Metin girişi + Gönder —
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Mesajını yaz...",
                    lines=1, scale=5,
                    show_label=False, container=False,
                )
                send_btn = gr.Button("Gönder", scale=1, elem_classes=["btn-send"], min_width=80)

            # — Sesli giriş —
            with gr.Row():
                mic = gr.Audio(
                    sources=["microphone"], type="numpy",
                    label="\U0001f3a4 Mikrofon", format="wav", scale=3,
                )
                mic_btn = gr.Button("\U0001f3a4 Sesli Gönder", scale=1, elem_classes=["btn-mic"], min_width=110)

            # — Ses çıkışı (otomatik oynatır) —
            # Not: Bazı tarayıcılarda gizli audio bileşeninde autoplay engellenebiliyor.
            # Bu yüzden görünür tutuyoruz.
            tts_out = gr.Audio(label="Sesli Yanıt", type="numpy", autoplay=True, visible=True)

            # — Alt butonlar —
            with gr.Row():
                tts_btn = gr.Button("\U0001f50a Son yanıtı seslendir", size="sm", elem_classes=["btn-sm", "btn-ghost"])
                clear_btn = gr.Button("\U0001f5d1\ufe0f Sohbeti temizle", size="sm", elem_classes=["btn-sm", "btn-clear"])

            # — Görsel Analiz (açılır) —
            with gr.Accordion("\U0001f4f8 Görsel Analiz", open=False, elem_classes=["accordion-compact"]):
                with gr.Row():
                    with gr.Column(scale=1, min_width=200):
                        img = gr.Image(type="filepath", label="Resim yükle", height=220)
                        img_q = gr.Textbox(label="Soru", value="Bu resimde ne var?", lines=1)
                        img_btn = gr.Button("Analiz Et", elem_classes=["btn-analyze"])
                    with gr.Column(scale=1, min_width=200):
                        img_out = gr.Textbox(label="Sonuç", lines=10, interactive=False)

            # — Sistem Bilgisi (açılır) —
            with gr.Accordion("\u2699\ufe0f Sistem Bilgisi", open=False, elem_classes=["accordion-compact"]):
                c = self.config
                gr.HTML(f"""<table class="sys-tbl">
                    <tr><td>Dil Modeli</td><td>{c['llm']['model']}</td></tr>
                    <tr><td>Görsel Model</td><td>{c['vlm']['model']}</td></tr>
                    <tr><td>Ses Tanıma</td><td>Faster-Whisper {c['stt']['model_size']} (CPU)</td></tr>
                    <tr><td>Ses Sentezi</td><td>Piper TTS (Türkçe, CPU)</td></tr>
                    <tr><td>GPU</td><td>RTX 2060 Super \u00b7 {c['hardware']['gpu_memory_limit']} GB</td></tr>
                    <tr><td>Sıcaklık / Top P</td><td>{c['llm']['temperature']} / {c['llm']['top_p']}</td></tr>
                    <tr><td>Maks Token</td><td>{c['llm']['max_tokens']}</td></tr>
                </table>""")

            # ─────────────────────────────────────
            # OLAYLAR
            # ─────────────────────────────────────

            def chat_text(message, history):
                if not message.strip():
                    return history, "", "", None
                resp = self.llm.generate(message, stream=False)
                history = history or []
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": resp})
                audio = self._tts(resp)
                return history, "", resp, audio

            def chat_voice(audio, history):
                text = self._stt(audio)
                if not text:
                    return history, "", None
                resp = self.llm.generate(text, stream=False)
                history = history or []
                history.append({"role": "user", "content": f"\U0001f3a4 {text}"})
                history.append({"role": "assistant", "content": resp})
                audio_out = self._tts(resp)
                return history, resp, audio_out

            def speak_last(txt):
                return self._tts(txt)

            def clear_chat():
                self.llm.clear_history()
                return [], "", "", None

            def analyze_image(image, question):
                if not image:
                    return "Lütfen bir resim yükle."
                return self.llm.analyze_image(image, question)

            # Bağlantılar
            send_btn.click(chat_text, [msg, chatbot], [chatbot, msg, last_resp, tts_out])
            msg.submit(chat_text, [msg, chatbot], [chatbot, msg, last_resp, tts_out])
            mic_btn.click(chat_voice, [mic, chatbot], [chatbot, last_resp, tts_out])
            tts_btn.click(speak_last, [last_resp], [tts_out])
            clear_btn.click(clear_chat, outputs=[chatbot, msg, last_resp, tts_out])
            img_btn.click(analyze_image, [img, img_q], [img_out])

        self.interface = app

    # ─────────────────────────────────────────────
    # YARDIMCI FONKSİYONLAR
    # ─────────────────────────────────────────────

    def _stt(self, audio):
        """Ses -> Metin"""
        if audio is None:
            return None
        try:
            sr, data = audio
            if data.dtype != np.float32:
                data = data.astype(np.float32) / 32767.0
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            if np.abs(data).max() < 0.01:
                return None
            if sr != 16000:
                from scipy import signal
                data = signal.resample(data, int(len(data) * 16000 / sr))
            text = self.stt.transcribe(audio_array=data, sample_rate=16000)
            return text.strip() if text and text.strip() else None
        except Exception as e:
            logger.error(f"STT hatası: {e}")
            return None

    def _tts(self, text):
        """Metin -> (sample_rate, float32_array) veya None"""
        if not text or not self.tts or not self.tts.model:
            return None
        try:
            chunks = []
            for c in self.tts.model.synthesize(text):
                chunks.append(c.audio_float_array)
            if chunks:
                arr = np.concatenate(chunks)
                # Gradio/browser tarafında en uyumlu format: float32 [-1, 1]
                arr = np.asarray(arr, dtype=np.float32)
                arr = np.clip(arr, -1.0, 1.0)
                return (self.tts.sample_rate, arr)
        except Exception as e:
            logger.error(f"TTS hatası: {e}")
        return None

    # ─────────────────────────────────────────────
    # BAŞLAT
    # ─────────────────────────────────────────────

    def launch(self):
        if not self.interface:
            logger.error("Arayüz oluşturulamadı!")
            return
        logger.info(f"Gradio başlatılıyor (:{self.port})...")
        try:
            self.interface.launch(
                server_port=self.port,
                share=self.share,
                auth=self.auth,
                inbrowser=True,
                css=CUSTOM_CSS,
                theme=gr.themes.Soft(
                    primary_hue=gr.themes.colors.indigo,
                    secondary_hue=gr.themes.colors.violet,
                    neutral_hue=gr.themes.colors.slate,
                    font=gr.themes.GoogleFont("Inter"),
                ),
            )
        except OSError:
            logger.warning(f"Port {self.port} meşgul, boş port aranıyor...")
            self.interface.launch(
                server_port=0,
                share=self.share,
                auth=self.auth,
                inbrowser=True,
                css=CUSTOM_CSS,
                theme=gr.themes.Soft(
                    primary_hue=gr.themes.colors.indigo,
                    secondary_hue=gr.themes.colors.violet,
                    neutral_hue=gr.themes.colors.slate,
                    font=gr.themes.GoogleFont("Inter"),
                ),
            )

