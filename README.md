# CS499 Capstone Project - Online Concept Exhange for the Human Domino Effect

<img width="1792" alt="Screenshot 2024-09-18 at 10 17 44 PM" src="https://github.com/user-attachments/assets/555da853-d665-449b-8a32-1b54bee5395f">

## Setting up the Python Virtual Environment

Codebase will be built against Python 3.12.1 (the most recent version of Python at the time of writing).

Python ships with the builtin `venv` module. Reference the [documentation tutorial](https://docs.python.org/3/tutorial/venv.html) on `venv` for setting things up and using the virtual environment.
Once created, you can sync up with the full development environment by running `python -m pip install -r requirements.txt` from within the virtual environment. This is the same `requirements.txt` that can found alongside `README.md` and `wsgi.py`.

## Running the site

During development, the site can be run using `flask run` from the terminal. You can also run the command as `flask run --debug` to enable hot reloading and the in-browser debugger.
This command must be run from the toplevel directory of the code structure (the same folder as `wsgi.py`). The site will be launched on your computer's [localhost](http://localhost:5000/) on port 5000. Use `Ctrl+C` to stop the server.

##Public Site Link