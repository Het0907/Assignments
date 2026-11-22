import requests
import json
import os
import csv
from pathlib import Path

print("Starting PDF to JSON conversion script...\n")

input_dir = Path("app/data/input")
# output_dir = "data/output"
csv_path = "app/data/output/summary.csv"

print(f"Input directory: {input_dir}")
# print(f"Output directory: {output_dir}")
print(f"CSV summary path: {csv_path}\n")

url = "http://localhost:8511/rx/extract"
normalize_json = "false"

# Ensure output directory exists
# os.makedirs(output_dir, exist_ok=True)
# print("Ensured output directory exists.\n")

header_written = False

tiff_files = list(input_dir.rglob("*.tif"))
total_tiffs = len(tiff_files)
print(f"Found {total_tiffs} TIFF  files to process: {tiff_files}\n")

for idx, tiff_file_path in enumerate(tiff_files):
    dir_path = os.path.dirname(tiff_file_path)
    output_dir_path = dir_path.replace("input", "output")
    filename = tiff_file_path.name

    os.makedirs(output_dir_path, exist_ok=True)
    print(f"output directory: {output_dir_path}")
    print(f"[{idx+1}/{total_tiffs}] Processing file: {filename}")
    

    try:
        with open(tiff_file_path, "rb") as f:
            print(f"Uploading {filename} to server at {url} ...")
            files = {"file": f}
            response = requests.post(
                url, files=files, data={"normalize_json": normalize_json}
            )
            print(f"Server responded with status code: {response.status_code}")

        if response.status_code == 200:
            output_json = response.json()
            print(
                f"Received JSON response for {filename}. Keys: {list(output_json.keys())}"
            )

            json_to_save = output_json.get("response", {})
            total_input_tokens = output_json.get("total_input_tokens", 0)
            total_output_tokens = output_json.get("total_output_tokens", 0)
            total_tokens = total_input_tokens + total_output_tokens

            output_filename = os.path.splitext(filename)[0] + ".json"

            output_path = os.path.join(output_dir_path, output_filename)
            print(f"Saving JSON output to: {output_path}")

            with open(output_path, "w", encoding="utf-8") as out_f:
                json.dump(json_to_save, out_f, ensure_ascii=False, indent=2)
            print(f"JSON saved successfully for {filename}")

            # Write/update CSV after each iteration
            write_header = not os.path.exists(csv_path) or not header_written
            with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                if write_header:
                    writer.writerow(
                        [
                            "Filename",
                            "Total Input Tokens",
                            "Total Output Tokens",
                            "Total Tokens",
                        ]
                    )
                    header_written = True
                    print(f"CSV header written to {csv_path}")

                writer.writerow(
                    [filename, total_input_tokens, total_output_tokens, total_tokens]
                )
                print(
                    f"CSV row added for {filename}: {total_input_tokens}, {total_output_tokens}, {total_tokens}"
                )

        else:
            print(f"❌ Failed to process {filename}: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Exception occurred while processing {filename}: {e}")

    print(f"Finished processing {filename}")
    print(f"Current CSV summary saved at: {csv_path}")
    print("-" * 60 + "\n")

print("All files processed successfully!")
