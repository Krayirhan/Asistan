"""
AI Sesli Asistan - Gradio UI
4 Sekme: Sohbet | Sesli | Gorsel | Sistem
"""

from loguru import logger
import numpy as np

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False


CUSTOM_CSS = """
/* Layout */
.gradio-container { max-width: 900px !important; margin: 0 auto !important; }

/* Header */
.hdr { text-align:center; padding:18px 0 2px; }
.hdr h1 { margin:0; font-size:24px; font-weight:800; letter-spacing:-0.5px;
           background:linear-gradient(135deg,#6366f1,#8b5cf6);
           -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hdr p  { margin:4px 0 0; font-size:11px; opacity:0.4; }

/* Tabs */
.tab-nav { border-bottom: 2px solid rgba(99,102,241,0.1) !important; }
.tab-nav button { font-weight:600 !important; font-size:14px !important;
                  padding:10px 20px !important; border-radius:8px 8px 0 0 !important; }
.tab-nav button.selected { color:#6366f1 !important;
                           border-bottom:3px solid #6366f1 !important;
                           background:rgba(99,102,241,0.05) !important; }

/* Primary button */
.btn-go { background:linear-gradient(135deg,#6366f1,#7c3aed) !important;
          border:none !important; color:#fff !important; font-weight:600 !important;
          border-radius:10px !important; min-height:44px !important;
          box-shadow:0 2px 8px rgba(99,102,241,0.3) !important;
          transition:all .15s !important; }
.btn-go:hover { transform:translateY(-1px) !important;
                box-shadow:0 4px 14px rgba(99,102,241,0.4) !important; }

/* Secondary / danger buttons */
.btn-sec { background:transparent !important; border:1px solid #e2e8f0 !important;
           font-weight:500 !important; border-radius:10px !important; }
.btn-del { background:transparent !important; border:1px solid #fecaca !important;
           color:#dc2626 !important; font-weight:500 !important; border-radius:10px !important; }

/* Mic button (voice in chat) */
.btn-mic { background:#f0fdf4 !important; border:2px solid #86efac !important;
           color:#16a34a !important; font-weight:700 !important;
           border-radius:10px !important; min-height:44px !important;
           font-size:18px !important; }

/* Status pill */
.status-pill textarea { text-align:center !important; font-weight:600 !important;
                        border-radius:20px !important; font-size:13px !important; }

/* Voice mode selector */
.voice-mode label { font-weight:600 !important; }

/* System table */
.sys-tbl { width:100%; border-collapse:collapse; font-size:13px; }
.sys-tbl td { padding:8px 6px; border-bottom:1px solid rgba(0,0,0,0.04); }
.sys-tbl td:first-child { opacity:0.5; width:45%; }
.sys-tbl td:last-child { font-weight:600; }
.sys-tbl tr:last-child td { border-bottom:none; }
"""


class GradioUI:
    def __init__(self, config, llm_manager, stt_engine, tts_engine):
        self.config = config
        self.llm = llm_manager
        self.stt = stt_engine
        self.tts = tts_engine
        self.port = config['ui']['gui'].get('server_port', 7860)
        self.share = config['ui']['gui'].get('share', False)

        if not GRADIO_AVAILABLE:
            self.interface = None
            return
        self._build()

    # ==============================================================
    # INTERFACE
    # ==============================================================

    def _build(self):
        with gr.Blocks(title="AI Asistan") as app:
            gr.HTML('<div class="hdr"><h1>AI Sesli Asistan</h1>'
                    '<p>Qwen 7B &middot; Whisper &middot; Piper TTS &middot; RTX 2060S</p></div>')

            with gr.Tabs():
                with gr.Tab("Sohbet"):
                    self._tab_chat()
                with gr.Tab("Sesli"):
                    self._tab_voice()
                with gr.Tab("Gorsel"):
                    self._tab_image()
                with gr.Tab("Sistem"):
                    self._tab_system()

        self.interface = app

    # ==============================================================
    # 1) SOHBET  -  metin + mikrofon + web arama hepsi burada
    # ==============================================================

    def _tab_chat(self):
        chatbot = gr.Chatbot(height=480, placeholder="Merhaba! Yaz veya mikrofona konus...")
        last_resp = gr.State("")

        # -- Input row: textbox + send + mic
        with gr.Row():
            msg = gr.Textbox(placeholder="Mesajini yaz...", lines=1, scale=5,
                             show_label=False, container=False)
            send_btn = gr.Button("Gonder", scale=1, elem_classes=["btn-go"], min_width=90)

        # -- Audio row (mic for quick voice in chat)
        with gr.Accordion("Sesli mesaj gonder", open=False):
            with gr.Row():
                mic = gr.Audio(sources=["microphone"], type="numpy", label="Mikrofon",
                               format="wav", scale=3)
                mic_btn = gr.Button("Sesli Gonder", elem_classes=["btn-mic"], scale=1, min_width=110)

        # -- Action row
        with gr.Row():
            speak_btn = gr.Button("Son yaniti seslendir", size="sm", elem_classes=["btn-sec"])
            clear_btn = gr.Button("Sohbeti temizle", size="sm", elem_classes=["btn-del"])

        tts_out = gr.Audio(label="Sesli Yanit", type="numpy", autoplay=True, visible=True)

        # -- handlers
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
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": resp})
            audio_out = self._tts(resp)
            return history, resp, audio_out

        def speak_last(txt):
            return self._tts(txt)

        def clear():
            self.llm.clear_history()
            return [], "", "", None

        send_btn.click(chat_text, [msg, chatbot], [chatbot, msg, last_resp, tts_out])
        msg.submit(chat_text, [msg, chatbot], [chatbot, msg, last_resp, tts_out])
        mic_btn.click(chat_voice, [mic, chatbot], [chatbot, last_resp, tts_out])
        speak_btn.click(speak_last, [last_resp], [tts_out])
        clear_btn.click(clear, outputs=[chatbot, msg, last_resp, tts_out])

    # ==============================================================
    # 2) SESLI  -  tam sesli konusma modu (manuel / kesintisiz)
    # ==============================================================

    def _tab_voice(self):
        mode = gr.Radio(["Manuel", "Kesintisiz"], value="Manuel",
                        label="Mod", elem_classes=["voice-mode"])

        status = gr.Textbox(value="Hazir", label="Durum", lines=1,
                            interactive=False, elem_classes=["status-pill"])

        with gr.Row():
            with gr.Column(scale=1):
                mic = gr.Audio(sources=["microphone"], type="numpy",
                               label="Mikrofon", format="wav")
                with gr.Row():
                    go_btn = gr.Button("Gonder", elem_classes=["btn-go"], visible=True)
                    clr_btn = gr.Button("Temizle", elem_classes=["btn-del"], size="sm")

            with gr.Column(scale=2):
                convo = gr.Chatbot(label="Konusma", height=380)

        audio_out = gr.Audio(label="Sesli Yanit", type="numpy", autoplay=True)

        # -- toggle visibility
        def on_mode(m):
            return gr.update(visible=(m == "Manuel"))

        mode.change(on_mode, [mode], [go_btn])

        # -- process (shared for both modes)
        def process(audio, mode_val):
            history = self._get_history()
            text = self._stt(audio)
            if not text:
                return ("Anlasilamadi" if audio is not None else "Bekleniyor..."), history, None

            resp = self.llm.generate(text, stream=False)
            history = self._get_history()
            tts_audio = self._tts(resp)
            return "Yanitlandi", history, tts_audio

        def clear():
            self.llm.clear_history()
            return "Temizlendi", [], None

        # Manuel: button click
        go_btn.click(process, [mic, mode], [status, convo, audio_out])

        # Kesintisiz: auto on audio change
        mic.change(process, [mic, mode], [status, convo, audio_out])

        clr_btn.click(clear, outputs=[status, convo, audio_out])

    # ==============================================================
    # 3) GORSEL  -  resim analizi
    # ==============================================================

    def _tab_image(self):
        with gr.Row():
            with gr.Column(scale=1):
                img = gr.Image(type="filepath", label="Resim", height=340)
                q = gr.Textbox(label="Soru", value="Bu resmi detayli acikla.", lines=2)
                btn = gr.Button("Analiz Et", elem_classes=["btn-go"])
            with gr.Column(scale=1):
                out = gr.Textbox(label="Sonuc", lines=16, interactive=False)

        def analyze(image, question):
            if not image:
                return "Lutfen bir resim yukleyin."
            return self.llm.analyze_image(image, question)

        btn.click(analyze, [img, q], [out])

    # ==============================================================
    # 4) SISTEM  -  bilgi + temizleme
    # ==============================================================

    def _tab_system(self):
        c = self.config
        gr.HTML(f"""<table class="sys-tbl">
            <tr><td>Dil Modeli</td><td>{c['llm']['model']}</td></tr>
            <tr><td>Gorsel Model</td><td>{c['vlm']['model']}</td></tr>
            <tr><td>Ses Tanima</td><td>Faster-Whisper {c['stt']['model_size']}</td></tr>
            <tr><td>Ses Sentezi</td><td>Piper TTS (Turkce)</td></tr>
            <tr><td>GPU</td><td>RTX 2060 Super &middot; {c['hardware']['gpu_memory_limit']} GB VRAM</td></tr>
            <tr><td>CPU</td><td>{c['hardware']['cpu_threads']} thread</td></tr>
            <tr><td>Gecmis Limiti</td><td>{c['llm']['context_length']} mesaj</td></tr>
            <tr><td>Sicaklik / Top P</td><td>{c['llm']['temperature']} / {c['llm']['top_p']}</td></tr>
            <tr><td>Tekrar Cezasi</td><td>{c['llm']['repeat_penalty']}</td></tr>
            <tr><td>Maks Token</td><td>{c['llm']['max_tokens']}</td></tr>
        </table>""")

        mem = gr.Textbox(label="Konusma Gecmisi", value=self.llm.get_history_summary(),
                         interactive=False, lines=1)

        with gr.Row():
            ref_btn = gr.Button("Yenile", size="sm", elem_classes=["btn-sec"])
            clr_btn = gr.Button("Gecmisi Sil", size="sm", elem_classes=["btn-del"])

        ref_btn.click(lambda: self.llm.get_history_summary(), outputs=[mem])
        clr_btn.click(lambda: (self.llm.clear_history(), "Temizlendi")[-1], outputs=[mem])

    # ==============================================================
    # HELPERS  -  ortak ses islemleri (tek yer, duplicate yok)
    # ==============================================================

    def _stt(self, audio):
        """Ses -> Metin. Hata/bos durumunda None doner."""
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
            logger.error(f"STT hatasi: {e}")
            return None

    def _tts(self, text):
        """Metin -> (sample_rate, int16_array) veya None"""
        if not text or not self.tts or not self.tts.model:
            return None
        try:
            chunks = []
            for c in self.tts.model.synthesize(text):
                chunks.append(c.audio_float_array)
            if chunks:
                arr = np.concatenate(chunks)
                return (self.tts.sample_rate, (arr * 32767).astype(np.int16))
        except Exception as e:
            logger.error(f"TTS hatasi: {e}")
        return None

    def _get_history(self):
        """LLM gecmisini Gradio chatbot formatina cevir"""
        return [{"role": "user" if m["role"] == "user" else "assistant",
                 "content": m["content"]} for m in self.llm.conversation_history]

    # ==============================================================
    # LAUNCH
    # ==============================================================

    def launch(self):
        if not self.interface:
            logger.error("Arayuz olusturulamadi!")
            return
        logger.info(f"Gradio baslatiliyor (:{self.port})...")
        self.interface.launch(
            server_port=self.port,
            share=self.share,
            inbrowser=True,
            css=CUSTOM_CSS,
            theme=gr.themes.Soft(
                primary_hue=gr.themes.colors.indigo,
                secondary_hue=gr.themes.colors.violet,
                neutral_hue=gr.themes.colors.slate,
                font=gr.themes.GoogleFont("Inter"),
            ),
        )
