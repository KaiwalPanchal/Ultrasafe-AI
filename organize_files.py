import os
import re
import shutil
from pathlib import Path


def create_sanitized_name(name: str) -> str:
    """Creates a filesystem-safe name by lowercasing and replacing spaces/special chars with underscores."""
    # Remove characters that aren't letters, numbers, spaces, or hyphens
    sanitized = re.sub(r"[^\w\s-]", "", name.lower())
    # Replace one or more spaces or hyphens with a single underscore
    sanitized = re.sub(r"[-\s]+", "_", sanitized)
    return sanitized


def parse_topics_and_categories(md_file_path: str) -> dict[str, str]:
    """
    Parses the markdown file to create a map of topic filenames to their category names.

    Returns:
        A dictionary like: {"topic_filename_base": "Category Title"}
        e.g., {"machine_learning_for_beginners": "Technology & AI"}
    """
    if not Path(md_file_path).exists():
        raise FileNotFoundError(f"Markdown file not found at: {md_file_path}")

    print(f"📖 Parsing categories and topics from {md_file_path}...")

    topic_to_category_map = {}
    current_category = None

    # Regex to find a topic title within a numbered list item
    topic_title_pattern = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*")

    with open(md_file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Check for a new category header (e.g., "## Technology & AI (8 topics)")
            if line.startswith("## "):
                # Extract just the category title, removing "##" and "(X topics)"
                current_category = line.split("(")[0].replace("##", "").strip()
                print(f"  - Found category: {current_category}")
                continue

            # Check for a topic line under the current category
            if current_category:
                match = topic_title_pattern.match(line)
                if match:
                    topic_title = match.group(1).strip()
                    # Create the filename base using the *exact same logic* as the generator script
                    topic_filename_base = create_sanitized_name(topic_title)
                    topic_to_category_map[topic_filename_base] = current_category

    print(f"✅ Parsed {len(topic_to_category_map)} topics into categories.")
    return topic_to_category_map


def organize_files(source_dir: Path, dest_dir: Path, topic_map: dict[str, str]):
    """
    Organizes files from the source directory into categorized subdirectories in the destination.
    """
    print("\n🚀 Starting file organization...")

    # Ensure source directory exists
    if not source_dir.is_dir():
        print(
            f"❌ Error: Source directory '{source_dir}' not found. Did you run the generator script first?"
        )
        return

    # Create the main destination directory
    dest_dir.mkdir(exist_ok=True)
    print(f"📂 Destination folder: {dest_dir.resolve()}")

    moved_count = 0
    skipped_count = 0

    # Iterate over the generated files in the source directory
    for txt_file in source_dir.glob("*.txt"):
        filename_base = txt_file.stem  # Get filename without extension

        if filename_base in topic_map:
            # Get the category title (e.g., "Technology & AI")
            category_title = topic_map[filename_base]
            # Create a safe folder name (e.g., "technology_ai")
            category_folder_name = create_sanitized_name(category_title)

            # Create the category-specific subdirectory
            category_path = dest_dir / category_folder_name
            category_path.mkdir(exist_ok=True)

            # Define source and destination paths for the file
            source_path = txt_file
            destination_path = category_path / txt_file.name

            # Move the file
            shutil.move(source_path, destination_path)
            print(
                f"  -> Moved '{txt_file.name}' to '{category_path.relative_to(dest_dir.parent)}'"
            )
            moved_count += 1
        else:
            print(
                f"  -> ⏭️  Skipping '{txt_file.name}' (no matching topic found in map)."
            )
            skipped_count += 1

    print("\n🎉 Organization Complete!")
    print(f"   - Files moved: {moved_count}")
    print(f"   - Files skipped: {skipped_count}")


def main():
    """Main function to run the file organizer."""
    md_file = "example_topics_list.md"
    source_directory = Path("master_content")
    destination_directory = Path("organized_content")

    try:
        # 1. Parse the MD file to get the topic-to-category mapping
        topic_map = parse_topics_and_categories(md_file)

        # 2. Organize the files based on the map
        organize_files(source_directory, destination_directory, topic_map)

    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print("Please ensure the markdown file exists and has the correct name.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
