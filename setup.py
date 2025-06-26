from setuptools import setup, find_packages

setup(
    name="msl-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pyautogui",
        "pytest",
        "httpx",
    ],
    extras_require={
        "test": ["pytest", "pytest-cov", "pytest-asyncio"],
    },
    python_requires=">=3.8",
) 