import os
import subprocess
import sys

def install_dependencies():
    """Checks for and automatically installs missing required libraries."""
    required_packages = ["pandas", "scipy", "tqdm", "unidiff", "openpyxl", "questionary"]
    print("🔍 Checking system dependencies...")
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"📦 Installing missing package: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            
    print("✅ All dependencies are installed and ready!\n")

# Run dependency check BEFORE importing third-party libraries
install_dependencies()

import questionary

def run_command(cmd):
    """Runs a command securely and captures output."""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Error executing: {cmd}")
        print(result.stderr)
        return False
    return True

def parse_bug_ids(input_str):
    """Parses a string like '1, 2, 5-7' into a sorted list of integers [1, 2, 5, 6, 7]."""
    bug_ids = set()
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if not part:
            continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                bug_ids.update(range(start, end + 1))
            except ValueError:
                print(f"⚠️ Invalid range: {part}")
        else:
            try:
                bug_ids.add(int(part))
            except ValueError:
                print(f"⚠️ Invalid number: {part}")
    return sorted(list(bug_ids))

def main():
    print("🎯 Defects4J Target Selector (Interactive Mode)")
    
    workspace_dir = os.path.expanduser("~/javelin-workspaces")
    os.makedirs(workspace_dir, exist_ok=True)

    # 1. UI: Select a Project (All 17 Projects Retained)
    projects = {
        "Chart (JFreeChart)": "Chart",
        "Cli (Apache Commons CLI)": "Cli",
        "Closure (Google Closure Compiler)": "Closure",
        "Codec (Apache Commons Codec)": "Codec",
        "Collections (Apache Commons Collections)": "Collections",
        "Compress (Apache Commons Compress)": "Compress",
        "Csv (Apache Commons CSV)": "Csv",
        "Gson (Google Gson)": "Gson",
        "JacksonCore (Jackson Core)": "JacksonCore",
        "JacksonDatabind (Jackson Databind)": "JacksonDatabind",
        "JacksonXml (Jackson XML format)": "JacksonXml",
        "Jsoup (Jsoup HTML parser)": "Jsoup",
        "JxPath (Apache Commons JXPath)": "JxPath",
        "Lang (Apache Commons Lang)": "Lang",
        "Math (Apache Commons Math)": "Math",
        "Mockito (Mockito Mocking framework)": "Mockito",
        "Time (Joda-Time)": "Time"
    }
    
    project_choice = questionary.select(
        "Which Defects4J project do you want to extract from?",
        choices=list(projects.keys())
    ).ask()

    if not project_choice:
        print("Operation cancelled.")
        sys.exit(0)
        
    selected_project = projects[project_choice]

    # 2. UI: Input Bug IDs
    print(f"\n✅ Selected Project: {selected_project}")
    bug_input = questionary.text(
        "Enter Bug IDs to extract (e.g., '1, 2, 4' or '1-5'):"
    ).ask()

    if not bug_input:
        print("Operation cancelled.")
        sys.exit(0)

    selected_bugs = parse_bug_ids(bug_input)
    
    if not selected_bugs:
        print("No valid bugs selected.")
        sys.exit(1)

    print(f"\nStarting extraction for {len(selected_bugs)} bugs from {selected_project}...\n")

    success_count = 0
    for bug_num in selected_bugs:
        # Formats exactly how your evaluation script expects: Defects4J-Lang-1
        bug_id = f"Defects4J-{selected_project}-{bug_num}"
        buggy_path = os.path.join(workspace_dir, f"{bug_id}-buggy")
        fixed_path = os.path.join(workspace_dir, f"{bug_id}-fixed")

        print(f"📦 Processing {bug_id}...")

        # Step A: Safe Buggy Extraction
        if not os.path.exists(buggy_path):
            print(f"   -> Pulling buggy environment...")
            cmd_buggy = f"defects4j checkout -p {selected_project} -v {bug_num}b -w {buggy_path}"
            if not run_command(cmd_buggy):
                continue
        else:
            print(f"   -> Buggy folder exists. Skipping.")

        # Step B: Safe Fixed Extraction
        if not os.path.exists(fixed_path):
            print(f"   -> Pulling developer-fixed environment...")
            cmd_fixed = f"defects4j checkout -p {selected_project} -v {bug_num}f -w {fixed_path}"
            if not run_command(cmd_fixed):
                continue
        else:
            print(f"   -> Fixed folder exists. Skipping.")
            
        success_count += 1

    print(f"\n✅ All done! Successfully extracted {success_count}/{len(selected_bugs)} bugs to {workspace_dir}")
    print("\n========================================================")
    print("NEXT STEPS:")
    print("1. Compile the buggy project (Ensure your terminal is running Java 8!):")
    if selected_bugs:
        print(f"   cd ~/javelin-workspaces/Defects4J-{selected_project}-{selected_bugs[0]}-buggy")
    print("   defects4j compile")
    print("   defects4j test")
    print("2. Run Javelin in IntelliJ to generate your .csv ranking.")
    print("3. Generate patches and run the Evaluation Script!")
    print("========================================================")

if __name__ == "__main__":
    main()
