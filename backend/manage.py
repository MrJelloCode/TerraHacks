import subprocess

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    subprocess.run(["uvicorn", "src.app:app","--host", "0.0.0.0", "--port", "80", "--reload"], check=False)  # noqa: S607
