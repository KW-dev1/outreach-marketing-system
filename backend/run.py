import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402
from app.worker import Worker  # noqa: E402

app = create_app()
worker = Worker(app)

if __name__ == "__main__":
    worker.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
