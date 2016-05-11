'''
rtp.site.monitor.scripts.run_app

runs monitor app

author | Immanuel Washington
'''
from rtp.site.flask_app import monitor_app as app
from rtp.site.monitor import views

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
