from flask import Flask, render_template, Response
import subprocess
import traceback

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/<path:command>')
def show_man_page(command):
    command_list = command.split('/')

    # Only alphanumeric please
    for i, cmd in enumerate(command_list):
        if not cmd.isalnum():
            del command_list[i]
    
    result = subprocess.run(['man', *command_list], capture_output=True, text=True)
    output = result.stderr if result.returncode != 0 else result.stdout
  
    return render_template('manpage.html', content=output)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=1337)
