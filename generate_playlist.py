
import os
import json
import sys

def generate_playlist(directory):
    """
    Generates a playlist.json file for a given directory.
    It scans for .mp3 files and assumes corresponding .vtt files exist.
    The paths in the JSON will be relative to the directory itself.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.", file=sys.stderr)
        sys.exit(1)

    tracks = []
    # Sort files for consistent order
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".mp3"):
            name, _ = os.path.splitext(filename)
            vtt_filename = f"{name}.vtt"
            
            # We need to check if the VTT file actually exists in the directory
            if os.path.exists(os.path.join(directory, vtt_filename)):
                tracks.append({
                    "title": name,
                    "src": filename,
                    "vtt": vtt_filename
                })
            else:
                # If no VTT, add it without the vtt track so it can still be played
                tracks.append({
                    "title": name,
                    "src": filename,
                    "vtt": None
                })
                print(f"Info: VTT file not found for '{filename}'. It will be included without subtitles.")


    playlist_filepath = os.path.join(directory, "playlist.json")
    try:
        with open(playlist_filepath, 'w', encoding='utf-8') as f:
            json.dump(tracks, f, ensure_ascii=False, indent=2)
        print(f"Successfully created '{playlist_filepath}' with {len(tracks)} tracks.")
    except IOError as e:
        print(f"Error writing to '{playlist_filepath}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_playlist.py <directory>", file=sys.stderr)
        sys.exit(1)
    
    target_dir = sys.argv[1]
    generate_playlist(target_dir)
