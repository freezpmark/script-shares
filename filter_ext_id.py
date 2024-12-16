import csv

lea_lesson = r"C:\Users\pmark\Downloads\LEA - Lesson (lea.lesson) - ext ID updated.csv"
lea_lesson_expression = r"C:\Users\pmark\Downloads\LEA - Lesson Expression (lea.lesson.expression) EMOJI-UPDATED.csv"
lea_lesson_expression_filtered = r"C:\Users\pmark\Downloads\LEA - Lesson Expression (lea.lesson.expression) EMOJI-UPDATED - FILTERED.csv"

# Read lea.lesson.csv to get all the existing External IDs
lesson_external_ids = set()
with open(lea_lesson, mode='r', encoding='utf-8') as lesson_file:
    lesson_reader = csv.DictReader(lesson_file)
    for row in lesson_reader:
        lesson_external_ids.add(row['External ID'])

# Read lea.lesson.expression.csv and filter out rows with non-existent External IDs
filtered_rows = []
with open(lea_lesson_expression, mode='r', encoding='utf-8') as expression_file:
    expression_reader = csv.DictReader(expression_file)
    for row in expression_reader:
        if row['Lesson/External ID'] in lesson_external_ids:
            filtered_rows.append(row)
        else:
            print(f"Expressions with this English text are missing: {row['English']}")

# Write the filtered data back to a new CSV file
with open(lea_lesson_expression_filtered, mode='w', encoding='utf-8', newline='') as output_file:
    fieldnames = filtered_rows[0].keys() if filtered_rows else []
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in filtered_rows:
        writer.writerow(row)

print("Filtered rows have been written to 'filtered_lea.lesson.expression.csv'.")
