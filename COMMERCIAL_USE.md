# 📜 Ticari Kullanım Kılavuzu (Commercial Use Guide)

## ✅ **TİCARİ KULLANIM İÇİN UYGUN** (Safe for Commercial Use)

Bu proje, ticari kullanım için **tamamen ücretsiz ve açık kaynak** bileşenler kullanmaktadır:

### **1. AI Modelleri**

| Model | Lisans | Ticari Kullanım | Kaynak |
|-------|--------|-----------------|--------|
| **Qwen2.5-7B** | Apache 2.0 | ✅ Serbest | [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) |
| **LLaVA 7B** | Apache 2.0 | ✅ Serbest | [Hugging Face](https://huggingface.co/llava-hf/llava-1.5-7b-hf) |
| **Faster-Whisper** | MIT | ✅ Serbest | [GitHub](https://github.com/guillaumekln/faster-whisper) |
| **Piper TTS** | MIT | ✅ Serbest | [GitHub](https://github.com/rhasspy/piper) |

### **2. Yazılım Bileşenleri**

| Bileşen | Lisans | Ticari Kullanım |
|---------|--------|-----------------|
| Ollama | MIT | ✅ Serbest |
| Gradio | Apache 2.0 | ✅ Serbest |
| Python Kütüphaneleri | MIT/BSD/Apache 2.0 | ✅ Serbest |

---

## ⚠️ **DİKKAT EDİLMESİ GEREKEN NOKTALAR**

### **1. Wake Word Özelliği (pvporcupine)**

**DURUM:** Porcupine wake word motoru **ticari kullanım için lisans gerektirir**.

**Çözümler:**
- ✅ **Devre Dışı Bırakma** (Varsayılan): `config/settings.yaml` dosyasında `wake_word.enabled: false`
- ✅ **Alternatif Kullanın**: [OpenWakeWord](https://github.com/dscripka/openWakeWord) (MIT License - ücretsiz)
- ⚠️ **Ticari Lisans Satın Alın**: [Picovoice Pricing](https://picovoice.ai/pricing/)

**Şu anki durum:** Wake word özelliği **devre dışı** (ticari kullanım için güvenli)

### **2. Trademark ve Branding**

**İZİN VERİLMEYEN:**
- ❌ Ürününüzü "Qwen Assistant" olarak adlandırmak
- ❌ "Official Alibaba AI" gibi yanıltıcı ifadeler
- ❌ Qwen/Alibaba logolarını markanızın bir parçası olarak kullanmak

**İZİN VERİLEN:**
- ✅ "Powered by Qwen2.5" şeklinde kaynak belirtme
- ✅ "Built with Qwen2.5-7B model" açıklaması
- ✅ README'de kullanılan teknolojileri listeleme

### **3. Attribution (Kaynak Belirtme) Gereklilikleri**

Apache 2.0 lisansı gereği **şunları yapmalısınız:**

1. **LICENSE dosyasını koruyun** (✅ Zaten mevcut)
2. **Değişiklikleri belirtin** (Eğer model/kod değiştirildiyse)
3. **Orijinal lisans bildirimini gösterin**

**Örnek Kullanım Metni:**
```
Bu ürün aşağıdaki açık kaynak AI modellerini kullanmaktadır:
- Qwen2.5-7B (Apache 2.0) - Alibaba Cloud tarafından geliştirilmiştir
- LLaVA 7B (Apache 2.0) - Görsel anlama için
```

---

## 📋 **TİCARİ KULLANIM İÇİN KONTROL LİSTESİ**

### **Başlamadan Önce:**
- [x] Wake word özelliği devre dışı bırakıldı
- [x] LICENSE dosyası üçüncü parti lisansları içeriyor
- [ ] Ürün isimlendirmesi trademark ihlali içermiyor
- [ ] README/Hakkında kısmında "Powered by Qwen2.5" eklendi
- [ ] Müşterilere AI kullanımı hakkında bilgi verildi

### **Deployment Öncesi:**
- [ ] Kendi sunucunuzda self-host yapıldı (API bağımlılığı yok)
- [ ] Model weights indirme politikası kontrol edildi
- [ ] GDPR/KVKK gibi veri koruma yasalarına uyum sağlandı
- [ ] Kullanım koşulları AI oluşturulmuş içerik hakkında bilgilendirme içeriyor

---

## 🌍 **ULUSLARARASI KULLANIM**

### **AB (Avrupa Birliği)**
- ✅ Apache 2.0 ve MIT lisansları AB'de geçerli
- ⚠️ **AI Act** uyumluluğu: Kullanıcıları AI ile etkileşimde oldukları konusunda bilgilendirin
- ⚠️ **GDPR**: Ses/görüntü verilerini işliyorsanız onay alın

### **ABD (Amerika Birleşik Devletleri)**
- ✅ Tüm lisanslar ticari kullanım için uygun
- ⚠️ **CCPA** (California): Kaliforniya kullanıcıları için veri gizliliği
- ⚠️ Sağlık/Finans alanında kullanım için sektörel düzenlemelere dikkat

### **Türkiye**
- ✅ Açık kaynak lisansları geçerli
- ⚠️ **KVKK** (Kişisel Verilerin Korunması): Ses kaydı için açık rıza gerekli
- ⚠️ **E-Ticaret Kanunu**: Online satış yapıyorsanız bilgilendirme yükümlülüğü

---

## 💰 **MALİYET HESAPLAMA**

### **Tamamen Ücretsiz Bileşenler:**
- ✅ Tüm AI modelleri (Qwen, LLaVA, Whisper, Piper)
- ✅ Tüm Python kütüphaneleri
- ✅ Ollama runtime
- ✅ Self-host deployment

### **Potansiyel Maliyetler:**
- 🖥️ **Sunucu**: Kendi donanımınız (RTX 2060 Super) - 0₺/ay
- ☁️ **Cloud**: AWS/Azure GPU instance - ~300-1000₺/ay (opsiyonel)
- 🎙️ **Wake Word**: Porcupine ticari lisans - ~$55/ay (sadece kullanırsanız)

**Tavsiye:** Kendi donanımınızda çalıştırarak **tamamen ücretsiz** kullanın!

---

## 📞 **SORU-CEVAP**

### **S: Müşterilerime bu yazılımı satabilir miyim?**
**C:** ✅ Evet! Apache 2.0 lisansı ticari satışa izin verir. Sadece LICENSE dosyasını koruyun ve kaynak belirtin.

### **S: SaaS (Software as a Service) olarak sunabilir miyim?**
**C:** ✅ Evet! Kendi sunucunuzda çalıştırıp API olarak hizmet verebilirsiniz. Cloud provider kullanıyorsanız maliyetlere dikkat edin.

### **S: Modeli fine-tune edip satabilir miyim?**
**C:** ✅ Evet! Apache 2.0, türev çalışmalara izin verir. Fine-tune edilmiş modeli de Apache 2.0 ile paylaşmanız veya kapalı tutmanız serbest.

### **S: Kaynak kodunu gizli tutabilir miyim?**
**C:** ✅ Evet! Apache 2.0, kaynak kodunu kapatmanıza izin verir. Sadece LICENSE dosyasını dahil edin.

### **S: Porcupine olmadan wake word nasıl yapılır?**
**C:** [OpenWakeWord](https://github.com/dscripka/openWakeWord) kullanın (MIT lisanslı, tamamen ücretsiz) veya mikrofon butonu ile manuel aktivasyon yapın.

### **S: KVKK uyumluluğu için ne yapmalıyım?**
**C:** 
1. Kullanıcılardan ses kaydı için **açık rıza** alın
2. Ses verilerinin **ne kadar süre saklanacağını** belirtin (varsayılan: saklanmıyor)
3. **Aydınlatma Metni** hazırlayın (örnek template verebilirim)
4. Veri silme taleplerine **15 gün içinde** yanıt verin

---

## 📄 **ÖRNEK AYDINLATMA METNİ (KVKK)**

```markdown
# Kişisel Verilerin İşlenmesi Hakkında Aydınlatma Metni

Bu uygulama, sesli komutlarınızı işlemek için yapay zeka kullanmaktadır.

**İşlenen Veriler:**
- Mikrofondan kayıt edilen ses verileri

**İşlenme Amacı:**
- Ses komutlarınızı metne dönüştürme
- AI asistanının sorularınızı anlaması

**Saklama Süresi:**
- Ses kayıtları işlendikten sonra **anında silinir**
- Konuşma geçmişi **oturum süresince** bellekte tutulur
- Oturum kapandığında **tüm veriler silinir**

**Veri Paylaşımı:**
- Sesleriniz **yalnızca kendi sunucunuzda** işlenir
- Üçüncü parti servislere **gönderilmez**
- İnternet bağlantısı **sadece web araması** için kullanılır

**Haklarınız:**
- Ses kaydını **reddetme hakkı**
- İşlenmiş verilere **erişim hakkı**
- Verilerin **silinmesini talep etme hakkı**

İletişim: [e-posta adresiniz]
```

---

## ✅ **SONUÇ**

Bu proje **%100 ticari kullanıma uygun** şekilde yapılandırılmıştır:

✅ Tüm AI modelleri Apache 2.0/MIT lisanslı  
✅ Wake word özelliği devre dışı (lisans problemi yok)  
✅ LICENSE dosyası güncel ve detaylı  
✅ Self-host deployment (üçüncü parti bağımlılık yok)  
✅ Trademark ihlali riski minimized  

**Yapmanız gereken:** README'nize "Powered by Qwen2.5" ekleyin ve müşterilerinize AI kullanımını açıkça belirtin.

---

**Son Güncelleme:** 11 Şubat 2026  
**Lisans Kontrolü:** ✅ Tamamlandı  
**Ticari Kullanım:** ✅ Onaylandı
