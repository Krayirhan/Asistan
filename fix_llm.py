"""Fix llm_manager.py system prompt section"""

with open('src/core/llm_manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace the problematic section
new_lines = []
skip_until_else = False
found = False

for i, line in enumerate(lines):
    if "# WEB SEARCH SONUÇLARINI SYSTEM MESSAGE" in line:
        found = True
        skip_until_else = True
        # Write new section
        new_lines.append("        # GÜNCEL BİLGİLERİ SYSTEM MESSAGE'A EKLE\n")
        new_lines.append("        if search_context:\n")
        new_lines.append('            logger.info(f"📤 Search context ekleniyor ({len(search_context)} karakter)")\n')
        new_lines.append("            \n")
        new_lines.append('            system_with_context = f"""{base_system}\n')
        new_lines.append("\n")
        new_lines.append("--- GÜNCEL BİLGİLER (İNTERNETTEN ALINMIŞTIR) ---\n")
        new_lines.append("{search_context}\n")
        new_lines.append("--- BİLGİ SONU ---\n")
        new_lines.append("\n")
        new_lines.append('ÖNEMLİ: Yukarıdaki bilgilerdeki sayıları (sıcaklık, nem, rüzgar vb.) olduğu gibi kullan. Değiştirme, yuvarlama, tahmin yapma."""\n')
        new_lines.append('            messages.append({"role": "system", "content": system_with_context})\n')
        new_lines.append("        else:\n")
        new_lines.append('            messages.append({"role": "system", "content": base_system})\n')
        continue
    
    if skip_until_else:
        # Skip old lines until we see the line after the else block's append
        if 'messages.append({"role": "system", "content": base_system})' in line:
            skip_until_else = False
            continue
        continue
    
    new_lines.append(line)

if found:
    with open('src/core/llm_manager.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✅ Başarıyla güncellendi!")
else:
    print("❌ Hedef bölüm bulunamadı!")
