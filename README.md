## Setting Up the Automator

1. **Create a new directory** where you want the script to reside:
   ```bash
   mkdir -p ~/itch_automation

```

*(Tip: Add a `.` before the folder name if you want to make it hidden. Feel free to name the folder whatever works best for you.)*

2. **Navigate into the directory** you just created:
```bash
cd ~/itch_automation

```


3. **Paste your `requirements.txt**` file into this directory.
4. **Create and activate** a virtual environment:
```bash
python3 -m venv venv && source venv/bin/activate

```


5. **Install the dependencies** listed in `requirements.txt`:
```bash
pip install -r requirements.txt

```


6. **Install and set up the Butler CLI**:
* Go to the official page: [itchio.itch.io/butler](https://itchio.itch.io/butler)
* Download **butler for linux 64-bit (stable)**.
* Head into your downloads folder and unzip the binary into your local bin directory (or your preferred location):
```bash
cd ~/Downloads
unzip butler-linux-amd64.zip -d ~/.local/bin/

```




7. **Add Butler to your PATH** so it can be run from anywhere:
```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc

```


*(Ensure the path points to the exact folder where you unzipped Butler in the previous step.)*
8. **Add the execution alias** to your `.bashrc` (or `.zshrc`):
```bash
echo "alias itch_uploader='source ~/personal_projects/2d_games_camp_uploader/venv/bin/activate && python ~/personal_projects/2d_games_camp_uploader/uploader.py && deactivate'" >> ~/.bashrc

```


*(Make sure to adjust the paths in the alias above to match your actual setup location.)*

---

## Using the Automator

1. **Prepare the target folder**: Create a dedicated folder and place only the final game directories inside it.
2. **Format the game folders** based on the Google Sheet visibility settings:
* **If Public:** `Firstname-Name-of-Game` (e.g., `Aarsh-Zombie-Survival`)
* **If Private:** `p-Firstname-Name-of-Game` (e.g., `p-Deep-Heist`)


3. **Run the automation script** by typing your configured alias in the terminal:
```bash
itch_uploader

```



```

```
