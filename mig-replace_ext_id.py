import csv
import re

teacher_replacements = {
    "lea_teacher_7_b7cbf626": "lea_teacher_1_f5f9e4b8",
    "lea_teacher_8_a0391f7a": "lea_teacher_2_c3816fed",
    "lea_teacher_9_1e75b174": "lea_teacher_3_b36906f2",
    "lea_teacher_13_419d7533": "lea_teacher_4_ae5ec8b8",
    "lea_teacher_14_a99cdbe8": "lea_teacher_5_1688e997",
    "lea_teacher_16_840db5ac": "lea_teacher_6_ef3e78e5",
    "lea_teacher_17_15f24d8a": "lea_teacher_7_1fed62d0",
    "lea_teacher_18_78f92967": "lea_teacher_8_46074c20",
    "lea_teacher_19_b1d416c7": "lea_teacher_9_58b7af7c",
    "lea_teacher_20_00516390": "lea_teacher_10_83b3957a",
    "lea_teacher_21_4056cd43": "lea_teacher_11_c895da34",
    "lea_teacher_23_1e176764": "lea_teacher_12_c872f307",
    "lea_teacher_25_2f42c51d": "lea_teacher_13_04c9334f",
    "lea_teacher_26_f67a8e84": "lea_teacher_14_4ecc330a",
    "lea_teacher_27_769f3ca3": "lea_teacher_15_b2fb3777",
    "lea_teacher_28_c4ea1d41": "lea_teacher_16_80c2acc8",
    "lea_teacher_29_a3bbd68d": "lea_teacher_17_431f6fff",
    "lea_teacher_30_aad03865": "lea_teacher_18_ab43f7bc",
}

def replace_ext_id(input_file, output_file):
    # Function to replace teacher IDs in a single cell of CSV data
    def replace_teacher_ids_in_cell(cell, replacements):
        for old_id, new_id in replacements.items():
            cell = re.sub(rf'\b{re.escape(old_id)}\b', new_id, cell)  # Ensure it matches the whole word
        return cell

    # Load CSV data
    with open(input_file, mode='r', encoding='utf-8') as input_file:
        csv_reader = csv.reader(input_file)
        rows = []

        # Iterate through the rows and replace teacher IDs
        for row in csv_reader:
            updated_row = [replace_teacher_ids_in_cell(cell, teacher_replacements) for cell in row]
            rows.append(updated_row)

    # Save the updated CSV data to a new file, with quotes around all fields
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        csv_writer = csv.writer(output_file, quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writerows(rows)

    print(f"Updated CSV data has been saved to {output_file}")


input_file_path = r"C:\Users\pmark\Downloads\LEA - Student (lea.student).csv"  # Replace with your input CSV file path
output_file_path = r"C:\Users\pmark\Downloads\LEA - Student (lea.student) - EXT-ID-UPDATED.csv"  # Replace with your output CSV file path
input_file_path2 = r"C:\Users\pmark\Downloads\LEA - Schedule (lea.schedule).csv"  # Replace with your input CSV file path
output_file_path2 = r"C:\Users\pmark\Downloads\LEA - Schedule (lea.schedule) - EXT-ID-UPDATED.csv"  # Replace with your output CSV file path

replace_ext_id(input_file_path, output_file_path)
replace_ext_id(input_file_path2, output_file_path2)
