import os
import json
import logging
from paddleocr import PaddleOCR

logging.getLogger("ppocr").setLevel(logging.ERROR)


def extract_text_to_json(
    image_path, json_path, confidence_threshold=0.93, x_tolerance=15
):
    ocr = PaddleOCR(use_angle_cls=True, lang="en")
    result = ocr.ocr(image_path, cls=True)

    if not result or not result[0]: 
        print(f"Нет распознанного текста в файле: {os.path.basename(image_path)}")
        return

    words = []

    for line in result[0]:
        coord = line[0]
        text = line[1][0]
        confidence = line[1][1]

        if confidence < confidence_threshold:
            continue

        x1, y1 = int(coord[0][0]), int(coord[0][1])
        x2, y2 = int(coord[2][0]), int(coord[2][1])
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

        words.append((text, center_x, center_y, confidence))

    if not words:
        print(
            f"Все слова в {os.path.basename(image_path)} имели низкую уверенность и были отфильтрованы."
        )
        return

    words.sort(key=lambda w: w[1])

    grouped_sentences = []

    for text, center_x, center_y, confidence in words:
        added = False
        for group in grouped_sentences:
            ref_x = group[0][1]
            if abs(ref_x - center_x) <= x_tolerance:
                group.append((text, center_x, center_y))
                added = True
                break

        if not added:
            grouped_sentences.append([(text, center_x, center_y)])

    for group in grouped_sentences:
        group.sort(key=lambda w: w[2])

    grouped_sentences.sort(key=lambda group: group[0][2])

    sentences_json = {
        f"Text{i+1}": " ".join(word[0] for word in group)
        for i, group in enumerate(grouped_sentences)
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sentences_json, f, ensure_ascii=False, indent=4)

    print(
        f"Файл обработан: {os.path.basename(image_path)} → {os.path.basename(json_path)}"
    )


def process_folder(folder_path):
    jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]

    if not jpg_files:
        print("В папке нет изображений .jpg")
        return

    print(f"Найдено {len(jpg_files)} файлов, начинаю обработку...")

    for jpg_file in jpg_files:
        image_path = os.path.join(folder_path, jpg_file)
        json_path = os.path.join(folder_path, os.path.splitext(jpg_file)[0] + ".json")

        extract_text_to_json(image_path, json_path)


folder_path = r"B:\project\convert_webp_to_jpg\Gachi Hatsujou Kiken Chitai _ Super Estrus Danger Zone"
process_folder(folder_path)
