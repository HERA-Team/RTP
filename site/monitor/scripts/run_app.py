'''
RTP.site.monitor.scripts.run_app

runs monitor app

author | Immanuel Washington
'''
import os
import sys
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(base_dir))
sys.path.append(os.path.dirname(os.path.dirname(base_dir)))
import nviews
from flask_app import monitor_app as app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
