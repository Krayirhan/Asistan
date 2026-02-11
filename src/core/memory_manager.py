"""
Memory Manager - Konuşma Geçmişi Yönetimi
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger
from pathlib import Path


class MemoryManager:
    """
    Konuşma geçmişi ve context yönetimi
    """
    
    def __init__(self, config: dict):
        self.config = config['memory']
        self.max_history = self.config['max_history']
        self.save_to_disk = self.config.get('save_to_disk', True)
        
        # Conversation storage
        self.conversations: List[Dict] = []
        self.current_session_id = self._generate_session_id()
        
        # Save path
        if self.save_to_disk:
            self.save_dir = Path("logs/conversations")
            self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """Unique session ID oluştur"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Konuşmaya mesaj ekle
        
        Args:
            role: 'user' veya 'assistant'
            content: Mesaj içeriği
            metadata: Ek bilgiler (opsiyonel)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations.append(message)
        logger.debug(f"Mesaj eklendi: {role} - {len(content)} karakter")
        
        # Limit kontrolü
        if len(self.conversations) > self.max_history * 2:
            self._trim_history()
    
    def _trim_history(self):
        """Eski mesajları sil (FIFO)"""
        removed = len(self.conversations) - (self.max_history * 2)
        self.conversations = self.conversations[removed:]
        logger.info(f"{removed} eski mesaj silindi")
    
    def get_recent_messages(self, count: Optional[int] = None) -> List[Dict]:
        """
        Son N mesajı al
        
        Args:
            count: Kaç mesaj (None = tümü)
        
        Returns:
            Mesaj listesi
        """
        if count is None:
            return self.conversations.copy()
        
        return self.conversations[-count:]
    
    def get_context_for_llm(self) -> List[Dict]:
        """
        LLM için formatlı context
        
        Returns:
            LLM mesaj formatında liste
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversations
        ]
    
    def clear(self):
        """Tüm geçmişi temizle"""
        if self.save_to_disk:
            self.save_session()
        
        self.conversations = []
        self.current_session_id = self._generate_session_id()
        logger.info("Konuşma geçmişi temizlendi")
    
    def save_session(self):
        """Mevcut session'ı diske kaydet"""
        if not self.save_to_disk or not self.conversations:
            return
        
        filename = self.save_dir / f"session_{self.current_session_id}.json"
        
        session_data = {
            "session_id": self.current_session_id,
            "start_time": self.conversations[0]["timestamp"],
            "end_time": self.conversations[-1]["timestamp"],
            "message_count": len(self.conversations),
            "messages": self.conversations
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Session kaydedildi: {filename}")
        except Exception as e:
            logger.error(f"Session kaydetme hatası: {e}")
    
    def load_session(self, session_id: str) -> bool:
        """
        Eski session'ı yükle
        
        Args:
            session_id: Session ID
        
        Returns:
            Başarılı mı?
        """
        filename = self.save_dir / f"session_{session_id}.json"
        
        if not filename.exists():
            logger.warning(f"Session bulunamadı: {session_id}")
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.conversations = session_data["messages"]
            self.current_session_id = session_id
            
            logger.success(f"Session yüklendi: {len(self.conversations)} mesaj")
            return True
            
        except Exception as e:
            logger.error(f"Session yükleme hatası: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Konuşma istatistikleri
        
        Returns:
            İstatistik dict'i
        """
        if not self.conversations:
            return {"message_count": 0}
        
        user_messages = [m for m in self.conversations if m["role"] == "user"]
        assistant_messages = [m for m in self.conversations if m["role"] == "assistant"]
        
        return {
            "message_count": len(self.conversations),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "session_id": self.current_session_id,
            "start_time": self.conversations[0]["timestamp"],
            "duration_minutes": self._calculate_duration()
        }
    
    def _calculate_duration(self) -> float:
        """Session süresini hesapla (dakika)"""
        if len(self.conversations) < 2:
            return 0.0
        
        start = datetime.fromisoformat(self.conversations[0]["timestamp"])
        end = datetime.fromisoformat(self.conversations[-1]["timestamp"])
        
        duration = (end - start).total_seconds() / 60
        return round(duration, 2)
    
    def __del__(self):
        """Cleanup - son session'ı kaydet"""
        if self.save_to_disk and self.conversations:
            self.save_session()
