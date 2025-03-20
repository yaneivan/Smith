import re

def split_text_into_chunks(text, max_length, overlap=0, split_by="sentence"):
    """
    Разбивает текст на фрагменты (чанки) с учетом структуры текста.

    Args:
        text (str): Текст для разбиения.
        max_length (int): Максимальная длина фрагмента.
        overlap (int):  Количество перекрывающихся символов между фрагментами.  Должен быть меньше max_length.
        split_by (str):  Способ разбиения: "sentence" (по предложениям, точкам) или "newline" (по новым строкам).

    Returns:
        list: Список фрагментов текста.
    """

    if overlap >= max_length:
        raise ValueError("Overlap must be less than max_length")

    chunks = []
    start = 0

    if split_by == "sentence":
        sentences = re.split(r'(?<=[.!?])\s+', text)

        while start < len(sentences):
            current_chunk = ""
            end = start

            while end < len(sentences):
                potential_chunk = " ".join(sentences[start : end + 1])
                if len(potential_chunk) <= max_length:
                    current_chunk = potential_chunk
                    end += 1
                else:
                    break

            chunks.append(current_chunk)

            if end < len(sentences) and overlap > 0:
                overlap_sentences = 0
                overlap_length = 0
                for i in range(end -1, start -1, -1):
                    overlap_length += len(sentences[i]) + 1
                    overlap_sentences += 1
                    if overlap_length > overlap:
                        break
                start = max(start + 1, end - overlap_sentences + 1 )
            else:
                # Исправление: увеличиваем start, даже если не смогли сформировать чанк нужной длины
                start = end if end > start else start + 1

    elif split_by == "newline":
        lines = text.split('\n')
        while start < len(lines):
            current_chunk = ""
            end = start
            while end < len(lines):
                potential_chunk = "\n".join(lines[start:end+1])
                if len(potential_chunk) <= max_length:
                    current_chunk = potential_chunk
                    end += 1
                else:
                    break
            chunks.append(current_chunk)

            if end < len(lines) and overlap > 0:
                overlap_lines = 0
                overlap_length = 0
                for i in range(end - 1, start -1, -1):
                    overlap_length += len(lines[i]) + 1
                    overlap_lines += 1
                    if overlap_length > overlap:
                        break
                start = max(start + 1, end - overlap_lines + 1)
            else:
                # Исправление: увеличиваем start, даже если не смогли сформировать чанк нужной длины
                start = end if end > start else start + 1
    else:
        raise ValueError("Invalid split_by value.  Must be 'sentence' or 'newline'")

    return [chunk for chunk in chunks if chunk.strip()]