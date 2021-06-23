# CST - Cyber Range - proxmox

### Getting Started

 - run `pip install -r requirements.txt`
 - make sure constants are correct in `main.py`
   ```python
    proxmox_ip = '192.168.200.1'
    proxmox_password = 'password'
    proxmox_node = 'pve'
    proxmox_iso_storage = 'local'
   ```
 - run `python3 main.py`
 - UI will start on http://localhost:5000

### Background
The application has been made by students as part of a project we did for The hague
University of Applied Sciences. The main goal of this project is to automate repetitive tasks
a lab instructor might have to do in the proxmox environment. There hasn't really been an 
attempt to make this project nice and clean; it just had to work :).

### Technical details

This app is a flask server with a few endpoints.

The ui is served from the filesystem (`/ui/build`-folder). Below
is the piece of code responsible for this.

```python
app = Flask(__name__, static_folder='ui/build')
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

### How to make changes to the ui

The source code of the ui can be found here https://github.com/karavaan/cst-proxmox-ui.

When you made changes to the ui you have to create a build of the react-application using `yarn build` or `npm run build`
react will build the application and output it to the `/build`-folder in that project. (see the default react readme in that repo.)

The `/build`-folder in the react application can be copy-pasted in to the `/ui/build` of this flask-application.
