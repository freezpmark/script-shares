import csv
import emoji


def remove_emojis(text):
    # Remove all emojis by replacing them with an empty string
    return emoji.replace_emoji(text, replace="")


def process_csv(input_file, output_file):
    with open(input_file, "r", encoding="utf-8", errors="replace") as infile, open(
        output_file, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row_number, row in enumerate(reader, start=1):
            cleaned_row = []
            for item in row:
                cleaned_item = remove_emojis(item)
                cleaned_row.append(cleaned_item)

                # Check if an emoji was removed
                if cleaned_item != item:
                    print(f"Emoji removed from row {row_number}: '{item}' -> '{cleaned_item}'")

            writer.writerow(cleaned_row)

input_csv_file = r"C:\Users\pmark\Downloads\LEA - Diary (lea.diary).csv"
output_csv_file = r"C:\Users\pmark\Downloads\LEA - Diary (lea.diary) EMOJI-UPDATED.csv"
input_csv_file2 = r"C:\Users\pmark\Downloads\LEA - Lesson Expression (lea.lesson.expression).csv"
output_csv_file2 = r"C:\Users\pmark\Downloads\LEA - Lesson Expression (lea.lesson.expression) EMOJI-UPDATED.csv"
input_csv_file3 = r"C:\Users\pmark\Downloads\LEA - Diary Expression (lea.diary.expression).csv"
output_csv_file3 = r"C:\Users\pmark\Downloads\LEA - Diary Expression (lea.diary.expression) EMOJI-UPDATED.csv"

process_csv(input_csv_file, output_csv_file)
process_csv(input_csv_file2, output_csv_file2)
process_csv(input_csv_file3, output_csv_file3)
