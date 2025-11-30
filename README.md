# CS499 Capstone Project - Human Family Team Website

<img width="1792" alt="Screenshot 2024-09-18 at 10 17 44 PM" src="https://github.com/user-attachments/assets/555da853-d665-449b-8a32-1b54bee5395f">

A web application aimed towards teachers, students and their families that serves as a hub for discussions, resources and ecommerce.

## Running the Project

### Clone the Project

```
git clone https://github.com/paryal58/humanFamilyTeam.git humanFamilyTeam
```

### Open the Project Folder
```
cd humanFamilyTeam
```

### Set up the Python Virtual Environment

Create virtual environment.
```
python -m venv venv
```

Activate the virtual environment. (Command for MacOS) 
```
source venv/bin/activate
```

### Install all required packages

Once created, you can sync up with the full development environment by running `python -m pip install -r requirements.txt` from within the virtual environment. This is the same `requirements.txt` that can found alongside `README.md` and `wsgi.py`.

## Running the site

During development, the site can be run using `flask run` from the terminal. You can also run the command as `flask run --debug` to enable hot reloading and the in-browser debugger.
This command must be run from the toplevel directory of the code structure (the same folder as `wsgi.py`). The site will be launched on your computer's [localhost](http://localhost:5000/) on port 5000. Use `Ctrl+C` to stop the server.