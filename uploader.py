import re
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# Project's won't have a export_presets.cfg file until someone clicks on the add export preset button in the export pop up.
# So here is the template that will be pasted into a project that doesn't have it so the godot CLI can work properly.
EXPORT_CONFIG_TEMPLATE = """[preset.0]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
patches=PackedStringArray()
patch_delta_encoding=false
patch_delta_compression_level_zstd=19
patch_delta_min_reduction=0.1
patch_delta_include_filters="*"
patch_delta_exclude_filters=""
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
progressive_web_app/ensure_cross_origin_isolation_headers=true
progressive_web_app/offline_page=""
progressive_web_app/display=1
progressive_web_app/orientation=0
progressive_web_app/icon_144x144=""
progressive_web_app/icon_180x180=""
progressive_web_app/icon_512x512=""
progressive_web_app/background_color=Color(0, 0, 0, 1)
threads/emscripten_pool_size=8
threads/godot_pool_size=4"""

output_file = Path.cwd() / "direct-link-codes.txt"
processed_students = set()

if output_file.exists():
    print("Found existing direct-link-codes.txt. Loading previously processed students...")
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                student_in_file = line.split(":")[0].strip()
                processed_students.add(student_in_file)

# Itch.io login

profile_dir = Path.home() / ".itch_automation" / "itch_profile"

print("Login into Itch.io")

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    
    page = context.pages[0]

    page.goto("https://itch.io/login")

    page.wait_for_url("https://itch.io/dashboard", timeout=0)

    page.close()
    context.close()

# Godot Automated Export

# Create a list to hold the dictionaries of our successfully built games
successful_builds = []

# Getting the absolute path of the uploads directory
uploads_dir = Path.cwd()

# loop through each of the directories inside the uploads directory (so basically the kids final games)
for game in uploads_dir.iterdir():
    # check if the game is a directory
    if game.is_dir():
        # check to see if a project.godot exists
        godot_file = game / "project.godot"
        if godot_file.exists():

            raw_folder_name = game.name

            is_private = raw_folder_name.lower().startswith("p-")

            if is_private:
                clean_folder_string = raw_folder_name[2:]
            else:
                clean_folder_string = raw_folder_name

            parts = clean_folder_string.split("-", 1)

            if len(parts) == 2:
                student_name = parts[0]
                raw_game_title = parts[1]
            
                clean_game_title = raw_game_title.replace("-", " ") 
            else:
                student_name = "Unknown"
                clean_game_title = clean_folder_string.replace("-", " ")

            if is_private:
                itch_title = f"Student - {clean_game_title}"
            else:
                itch_title = f"{student_name} - {clean_game_title}"

            if student_name in processed_students:
                print(f"Skipping folder {game.name} - {student_name} is already in the ledger.")
                continue

            # check if the godot project already has a export_presets.cfg
            export_file = game / "export_presets.cfg"
            if not export_file.exists():
                # if it doesn't exist then create one and use the template to create one
                export_file.write_text(EXPORT_CONFIG_TEMPLATE)
            # get the name of the game as use that to create the directory that the exported content will go too
            game_name = game.name
            staging_dir = uploads_dir / f"{game_name}_build"
            staging_dir.mkdir(exist_ok=True)

            # This is the command that will run through subprocess
            command = [
                "/bc/Software/Godot/Godot_v4.4.1-stable_linux.x86_64",
                "--headless",
                "--path", str(game),
                "--export-release", "Web",
                str(staging_dir / "index.html")
            ]

            try:
                # run the export command, all the trues are to see the outputs of the godot command being run
                result = subprocess.run(command, check=True, capture_output=True, text=True)

                # zipping up the exported file that result put the exported content into
                zip_destination = uploads_dir / f"{game_name}_export"

                shutil.make_archive(str(zip_destination), "zip", str(staging_dir))

                print(f"The project {game.name} has been exported")

                # delete the staging_dir after the thing as already been zipped
                if staging_dir.exists():
                    shutil.rmtree(staging_dir)

                successful_builds.append({
                    "zip_path": str(zip_destination),
                    "itch_title": itch_title,
                    "student_name": student_name,
                    "raw_folder": raw_folder_name
                })

            except subprocess.CalledProcessError as e:
                print(f"Export failed with error code {e.returncode}")
                print(e.stderr) 

print("Moving onto Itch.io")

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False, 
        args=["--disable-blink-features=AutomationControlled"]
    )

    for build in successful_builds:

        # ---- This portion was obtained using a tool called codegen ----
        print(f"Creating Itch.io page for {build['itch_title']}...")

        page = context.new_page()
        page.goto("https://itch.io/game/new")

        page.get_by_role("textbox", name="Title", exact=True).click()
        page.get_by_role("textbox", name="Title", exact=True).fill(build["itch_title"])
        
        page.get_by_role("textbox", name="Project URL https://").click()
        page.locator("div").filter(has_text=re.compile(r"^Downloadable — You only have files to be downloaded$")).nth(1).click()
        page.get_by_text("HTML — You have a ZIP or HTML").click()
        page.get_by_role("checkbox", name=" No payments").click()

        page.get_by_role("radio", name="No — This project does not").check()
        page.locator("#redactor-uuid-0").click()
        page.locator("#redactor-uuid-0").fill("Visit our website to see what camps are available near you!\nhttps://www.bytecamp.ca\nAt Byte Camp, we make tech education fun for kids! We help kids challenge themselves, learn awesome\nnew skills and be creative. This summer, we are teaching kids aged 9-14 how to code and design video\ngames, animate, 3D model, make music, video edit and more! Since 2003 over 30,000 kids have come\nthrough our programs!!")
        page.get_by_role("radio", name="Community Build a community").check()
        
        page.get_by_role("button", name="Save & view page").click()

        page.wait_for_load_state("networkidle")
        final_url = page.url
        game_slug = final_url.split("/")[-1]

        # -------------------------------------------------------------------

        butler_target = f"sherryninja/{game_slug}:web"
        actual_zip_file = f"{build['zip_path']}.zip"

        butler_command = [
            "butler",
            "push",
            actual_zip_file,
            butler_target
        ]

        try:
            print(f"Pushing {build['itch_title']} via Butler...")
            subprocess.run(butler_command, check=True, capture_output=True, text=True)
            print(f"Successfully uploaded {build['itch_title']}!")
            
            print("Configuring web player and publishing...")
            
            page.get_by_role("link", name="Edit game").click()

            page.wait_for_load_state("domcontentloaded")

            browser_play_checkbox = page.get_by_role("checkbox", name="This file will be played in")

            max_retries = 10
            for attempt in range(max_retries):
                if browser_play_checkbox.is_visible():
                    print(f"Itch.io processing complete on attempt {attempt + 1}.")
                    break
                
                print(f"Zip not processed yet. Reloading... ({attempt + 1}/{max_retries})")
                page.wait_for_timeout(3000)
                page.reload()
                page.wait_for_load_state("domcontentloaded")
            else:
                print("Error: Itch.io took too long to process the zip file.")

            browser_play_checkbox.check()
            page.get_by_role("checkbox", name="Mobile friendly — Your").check()
            page.get_by_role("checkbox", name="Automatically start on page").check()
            page.get_by_role("checkbox", name="SharedArrayBuffer support — (").check()
            page.get_by_role("radio", name="Public — Anyone can view the").check()
            page.get_by_role("button", name="Save").nth(1).click()

            page.get_by_role("link", name="Distribute").click()
            page.get_by_role("link", name="Embed game").click()

            page.wait_for_load_state("domcontentloaded")

            link_textbox = page.get_by_role("paragraph").filter(has_text=re.compile(r"Direct link")).get_by_role("textbox")
            raw_link = link_textbox.input_value()

            match = re.search(r"embed-upload/(\d+)", raw_link)
            
            if match:
                embed_code = match.group(1)
            else:
                embed_code = "Code Not Found"

            build["embed_code"] = embed_code

            page.wait_for_load_state("networkidle")
        except subprocess.CalledProcessError as e:
            print(f"Butler upload failed with error code {e.returncode}")
            print(e.stderr)
        
        page.close()

    context.close()

print("\n--- Final Student Links ---")

output_file = Path.cwd() / "direct-link-codes.txt"

with open(output_file, "a", encoding="utf-8") as f:
    for build in successful_builds:
        student = build.get("student_name", "Unknown Student")
        code = build.get("embed_code", "No code found")
        
        print(f"{student}: {code}")
        
        f.write(f"{student}: {code}\n")

print(f"\nAll codes successfully saved to {output_file.name}")

print("Goodbye")
