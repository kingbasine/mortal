import uvicorn
from mortal import app


if __name__ == "__main__":
    uvicorn.run("mortal:app", host="0.0.0.0", port=8083, reload=True)
