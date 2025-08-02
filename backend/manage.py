import subprocess

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    subprocess.run(["/usr/local/bin/uvicorn", "app:app", "--port", "8000", "--reload"], check=False)
