from __future__ import print_function, division, absolute_import

import threading
import time
import socket
import os
import platform
import urlparse
import cgi
import httplib
import urllib
import sys
import psutil
import pickle
import subprocess
import netifaces
from astropy.time import Time

from string import upper

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from still_shared import InputThread
from still_shared import handle_keyboard_input

logger = True  # This is just here because the jedi syntax checker is dumb.

PLATFORM = platform.system()
FAIL_ON_ERROR = 1

TIME_INT_FOR_NEW_MC_CHECK = 300


class Task:

    def __init__(self, task, obs, still, args, drmaa_args, drmaa_queue, dbi, TaskServer, cwd='.',
                 path_to_do_scripts=".", custom_env_vars={}):
        self.task = task
        self.obs = obs
        self.still = still
        self.args = args
        self.custom_env_vars = custom_env_vars
        self.full_env = {}
        self.dbi = dbi
        self.cwd = cwd
        self.process = None
        self.outfile_counter = 0
        self.path_to_do_scripts = path_to_do_scripts
        self.ts = TaskServer
        self.jid = None
        self.sg = TaskServer.sg
        self.drmaa_stdout_file = ''
        self.drmaa_stderr_file = ''
        self.drmaa_args = drmaa_args
        self.drmaa_queue = drmaa_queue
        self.stdout_stderr_file = ''
        self.max_mem = 0.
        self.avg_cpu_load = 0.
        self.n_cpu_load_polls = 0
        self.start_time = Time.now()

    def remove_file_if_exists(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass
        return

    def run(self):
        if self.process is not None:
            raise RuntimeError('Cannot run a Task that has been run already.')
        self.process = self._run()
        if self.process is None:
            self.record_failure()
        else:
            self.record_launch()
        return

    def run_popen(self):

        self.stdout_stderr_file = "%s/%s_%s.stdout_stderr" % (
            self.ts.data_dir, self.obs, self.task)
        self.remove_file_if_exists(self.stdout_stderr_file)
        stdout_stderr_buf = open(self.stdout_stderr_file, "w")
        process = psutil.Popen(['%s/do_%s.sh' % (self.path_to_do_scripts, self.task)] + self.args,
                               cwd=self.cwd, env=self.full_env, stdout=stdout_stderr_buf, stderr=subprocess.STDOUT)
        try:
            process.nice(2)
            # Jon : I want to set all the processes evenly so they don't compete against core OS
            #    functionality (ssh, cron etc..) slowing things down.
            if PLATFORM != "Darwin":
                # Jon : cpu_affinity doesn't exist for the mac, testing on a
                # mac... yup... good story.
                process.cpu_affinity(range(psutil.cpu_count()))
        except:
            logger.exception("Could not set cpu affinity")
        return process

    def run_drmaa(self):
        jt = self.ts.drmaa_session.createJobTemplate()
        jt.remoteCommand = "%s/do_%s.sh" % (self.path_to_do_scripts, self.task)
        self.stdout_stderr_file = "%s/%s_%s.stdout_stderr" % (
            self.ts.data_dir, self.obs, self.task)
        #self.stdout_stderr_file = "%s/%s_%s.stdout_stderr" % (self.ts.drmaa_shared, self.obs, self.task)
        self.remove_file_if_exists(self.stdout_stderr_file)

        # Don't forget -e as well..
        jt.nativeSpecification = "%s -q %s -wd %s -V -j y -o %s" % (
            self.drmaa_args, self.drmaa_queue, self.cwd, self.stdout_stderr_file)
        jt.args = self.args
        jt.joinFiles = True
        jid = self.ts.drmaa_session.runJob(jt)  # Get the Job ID
        return jid

    def _run(self):
        process = None

        logger.info('Task._run: (%s, %s) %s cwd=%s' % (
            self.task, self.obs, ' '.join(['do_%s.sh' % self.task] + self.args), self.cwd))

        # Combine the current environment that the TaskManager is running in
        #    with any additional ones for the do_ script specified in conf file
        current_env = os.environ
        global_env_vars = {'obsnum': self.obs, 'task': self.task}
        self.full_env = current_env.copy()
        self.full_env.update(self.custom_env_vars)
        self.full_env.update(global_env_vars)
        # always look in do scripts dir. this is where we're putting production
        # python scripts.
        self.full_env['PATH'] = self.path_to_do_scripts + \
            ':' + self.full_env['PATH']

        try:
            if self.sg.cluster_scheduler == 1:  # Do we need to interface with a cluster scheduler?
                self.jid = self.run_drmaa()  # Yup
                process = self.jid
            else:
                process = self.run_popen()  # Use Popen to run a normal process
        except Exception:
            logger.exception('Task._run: (%s,%s) error="%s"' % (
                self.task, self.obs, ' '.join(['%s/do_%s.sh' % (
                    self.path_to_do_scripts, self.task)] + self.args)))
            self.record_failure()
            if FAIL_ON_ERROR == 1:
                self.ts.shutdown()

        try:
            self.dbi.update_obs_current_stage(self.obs, self.task)
            self.dbi.add_log(self.obs, self.task, ' '.join(
                ['%sdo_%s.sh' % (self.path_to_do_scripts, self.task)] + self.args + ['\n']), None)
        except:
            logger.exception("Could not update database")

        return process

    def finalize(self):
        try:
            # Read in stdout/stderr combined file
            with open(self.stdout_stderr_file, 'r') as output_file:
                task_output = output_file.read()
        except:
            logger.debug("Task.finalize: Could not open stdout / stderr file for obs: % s and task: "
                         " % s marking task as FAILED" % (self.obs, self.task))
            self.record_failure()
            return

        if self.sg.cluster_scheduler == 1:
            # get JobInfo instance
            task_info = self.ts.drmaa_session.wait(
                self.jid, self.ts.drmaa_session.TIMEOUT_WAIT_FOREVER)
            task_return_code = task_info.exitStatus
        else:
            # task_output = self.process.communicate()[0]
            task_return_code = self.process.returncode

        self.dbi.update_log(self.obs, status=self.task,
                            logtext=task_output, exit_status=task_return_code)

        if task_return_code != 0:  # If the task didn't return with an exit code of 0 mark as failure
            logger.error(
                "Task.finalize : Task Failed : Obsnum: %s , Task: %s, Exit Code: %s, OUTPUT : %s"
                % (self.task, self.obs, task_return_code, task_output))
            self.record_failure()
        else:
            logger.debug(
                "Task.finalize : Task Succeeded : Obsnum: %s , Task: %s, Exit Code: %s, OUTPUT : %s"
                % (self.task, self.obs, task_return_code, task_output))
            self.record_completion()
        return

    def kill(self):
        self.record_failure(failure_type="KILLED")

        if self.sg.cluster_scheduler == 1:
            import drmaa
            self.ts.drmaa_session.control(
                self.jid, drmaa.JobControlAction.TERMINATE)
            logger.debug(
                'Task.kill Trying to kill: ({task},{obsnum}) pid={pid}'.format(
                    task=self.task, obsnum=self.obs, pid=self.jid))
        else:
            if self.process.pid:
                logger.debug(
                    'Task.kill Trying to kill: ({task},{obsnum}) pid={pid}'.format(
                        task=self.task, obsnum=self.obs, pid=self.process.pid))

                for child in self.process.children(recursive=True):
                    child.kill()
                self.process.kill()

            os.wait()  # Might need to think about this one, communicate might be a better option but not sure

    def record_launch(self):
        if self.sg.cluster_scheduler == 1:
            self.dbi.set_obs_pid(self.obs, self.process)
        else:
            self.dbi.set_obs_pid(self.obs, self.process.pid)

        # log to M&C
        if self.ts.wf.log_to_mc:
            import mc_utils
            mc_utils.add_mc_process_event(self.obs, "started")

    def record_failure(self, failure_type="FAILED"):
        for task in self.ts.active_tasks:
            if task.obs == self.obs:
                # Remove the killed task from the active task list
                self.ts.active_tasks.remove(task)
                logger.debug("Removed task : %s from active list" % task.task)
        self.dbi.set_obs_pid(self.obs, -9)
        self.dbi.update_obs_current_stage(self.obs, failure_type)
        logger.error("Task.record_failure: Task: %s, Obsnum: %s, Type: %s" % (
            self.task, self.obs, failure_type))

        if self.ts.wf.log_to_mc:
            # log to M&C
            import mc_utils
            mc_utils.add_mc_process_event(self.obs, "error")

        return

    def record_completion(self):
        self.dbi.set_obs_status(self.obs, self.task)
        self.dbi.set_obs_pid(self.obs, 0)
        self.remove_file_if_exists(self.stdout_stderr_file)

        if self.ts.wf.log_to_mc:
            # log completion time to M&C
            import mc_utils
            mc_utils.add_mc_process_event(self.obs, "finished")
            mc_utils.add_mc_process_record(self.obs, self.ts.wf.workflow_actions,
                                        self.ts.wf.workflow_actions_endfile)
            # log task resources to M&C
            stop_time = Time.now()
            if self.max_mem > 0:
                max_mem = self.max_mem
            else:
                max_mem = None
            if self.n_cpu_load_polls > 0:
                avg_cpu = self.avg_cpu_load / self.n_cpu_load_polls
            else:
                avg_cpu = None
            mc_utils.add_mc_task_resource_record(self.obs, self.task, self.start_time,
                                                 self.stop_time, max_mem, avg_cpu)

        return


class TaskClient:

    def __init__(self, dbi, host, workflow, port, sg):
        self.dbi = dbi
        self.sg = sg
        self.host_port = (host, port)
        self.wf = workflow
        self.error_count = 0
        self.logger = sg.logger
        global logger
        logger = sg.logger

    def transmit(self, task, obs, action_type):
        ###
        #
        # This function along with the recieve should both to redone to pass the data via XML
        #
        ###

        conn_headers = {
            "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        status = ''
        response_status = -1
        response_reason = "Failed to connect"
        # respose_data = ""

        if action_type == "NEW_TASK":
            conn_type = "POST"
            conn_path = "/NEW_TASK"
            args = self.gen_args(task, obs)
            args_string = ' '.join(args)
            if self.sg.cluster_scheduler == 1:
                drmaa_args_string = self.gen_drmaa_args(task, obs)
                try:
                    if self.wf.drmaa_queue_by_task[task]:
                        drmaa_queue = self.wf.drmaa_queue_by_task[task]
                    else:
                        drmaa_queue = self.wf.default_drmaa_queue
                except:
                    drmaa_queue = self.wf.default_drmaa_queue

            else:
                drmaa_queue = ""
                drmaa_args_string = ""
            pickled_env_vars = pickle.dumps(self.sg.env_vars)
            conn_params = urllib.urlencode({'obsnum': obs,
                                            'task': task,
                                            'args': args_string,
                                            'drmaa_args': drmaa_args_string,
                                            'drmaa_queue': drmaa_queue,
                                            'env_vars': pickled_env_vars})
            logger.debug(
                'TaskClient.transmit: sending (%s,%s) with args=%s drmaa_args=%s'
                % (task, obs, args_string, drmaa_args_string))

        elif action_type == "KILL_TASK":
            conn_type = "GET"
            conn_path = "/KILL_TASK?" + obs
            conn_params = ""

        try:  # Attempt to open a socket to a server and send over task instructions
            logger.debug("connecting to TaskServer %s" % self.host_port[0])

            conn = httplib.HTTPConnection(
                self.host_port[0], self.host_port[1], timeout=20)
            conn.request(conn_type, conn_path, conn_params, conn_headers)
            response = conn.getresponse()
            response_status = response.status
            response_reason = response.reason
            response_data = response.read()
        except:
            logger.exception("Could not connect to server %s on port : %s, marking OFFLINE"
                             % (self.host_port[0], self.host_port[1]))
            # If we can't connect to the taskmanager just mark it as offline
            self.dbi.mark_still_offline(self.host_port[0])
        finally:
            conn.close()

        if response_status != 200:  # Check if we did not recieve 200 OK
            self.error_count += 1
            logger.debug("Problem connecting to host : %s  has error count :%s"
                         % (self.host_port[0], self.error_count))
            status = "FAILED_TO_CONNECT"
        else:
            status = "OK"
            logger.debug("Connection status : %s : %s" %
                         (response_status, response_reason))
        return status, self.error_count

    def gen_drmaa_args(self, task, obs):
        try:
            args = self.wf.drmaa_args[task]
        except:
            args = ""
        return args

    def gen_args(self, task, obs):
        args = []
        pot, path_prefix, parent_dirs, basename = self.dbi.get_input_file(
            obs, apply_path_prefix=True)
        path = os.path.join(path_prefix, parent_dirs)
        outhost, outpath = self.dbi.get_output_location(obs)

        # These varibles are here to be accessible to the arguments variable in
        # the config file
        stillhost = self.dbi.get_obs_still_host(obs)
        stillpath = self.dbi.get_still_info(self.host_port[0]).data_dir
        # PCL: I'm lazy and can't think of a better way to do this for now, so I'm leaving this block here
        #      as a purposely non-accessible block, but will reorganize later
        if False:
            neighbors = [(self.dbi.get_obs_still_host(n), self.dbi.get_still_info(self.host_port[0]).data_dir)
                         + self.dbi.get_input_file(n) for n in self.dbi.get_neighbors(obs) if n is not None]
            neighbors_base = list(self.dbi.get_neighbors(obs))
        else:
            neighbors = [(self.dbi.get_obs_still_host(n), self.dbi.get_still_info(self.host_port[0]).data_dir)
                         + self.dbi.get_input_file(n) for n in self.dbi.get_pol_neighbors(obs) if n is not None]
            neighbors_base = list(self.dbi.get_pol_neighbors(obs))
        if not neighbors_base[0] is None:
            neighbors_base[0] = self.dbi.get_input_file(neighbors_base[0])[-1]
        if not neighbors_base[1] is None:
            neighbors_base[1] = self.dbi.get_input_file(neighbors_base[1])[-1]

        # Jon : closurs are a bit weird but cool, should get rid of appendage
        # HARDWF
        def interleave(filename, appendage='cR'):
            # make sure this is in sync with do_X.sh task scripts.
            rv = [filename]
            if neighbors_base[0] is not None:
                rv = [neighbors_base[0] + appendage] + rv
            if neighbors_base[1] is not None:
                rv = rv + [neighbors_base[1] + appendage]
            return rv

        if task != "STILL_KILL_OBS":
            try:  # Jon: Check if we actually have any custom args to process, if not then defaulting is normal behavior and not an exception
                args = eval(self.wf.action_args[task])
            except:
                logger.exception("Could not process arguments for task %s please check args for this task in config file, ARGS: %s" % (
                    task, self.wf.action_args))
                # args = [obs]
                sys.exit(1)

        return args


class TaskHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)  # Return a response of 200, OK to the client
        self.end_headers()
        parsed_path = urlparse.urlparse(self.path)

        if upper(parsed_path.path) == "/KILL_TASK":
            try:
                obsnum = str(parsed_path.query)
                pid_of_obs_to_kill = int(self.server.dbi.get_obs_pid(obsnum))
                logger.debug("We recieved a kill request for obsnum: %s, shutting down pid: %s" % (
                    obsnum, pid_of_obs_to_kill))
                self.server.kill(pid_of_obs_to_kill)
                # Return a response of 200, OK to the client
                self.send_response(200)
                self.end_headers()
                logger.debug("Task killed for obsid: %s" % obsnum)
            except:
                logger.exception(
                    "Could not kill observation, url path called : %s" % self.path)
                # Return a response of 200, OK to the client
                self.send_response(400)
                self.end_headers()
        elif upper(parsed_path.path) == "/INFO_TASKS":
            task_info_dict = []
            for mytask in self.server.active_tasks:  # Jon : !!CHANGE THIS TO USE A PICKLED DICT!!
                try:
                    child_proc = mytask.process.children()[0]
                    if psutil.pid_exists(child_proc.pid):
                        task_info_dict.append({'obsnum': mytask.obs, 'task': mytask.task, 'pid': child_proc.pid,
                                               'cpu_percent': child_proc.cpu_percent(interval=1.0),
                                               'mem_used': child_proc.memory_info_ex()[0],
                                               'cpu_time': child_proc.cpu_times()[0],
                                               'start_time': child_proc.create_time(),
                                               'proc_status': child_proc.status()})
                except:
                    logger.exception(
                        "do_GET : Trying to send response to INFO request")
            pickled_task_info_dict = pickle.dumps(task_info_dict)
            self.wfile.write(pickled_task_info_dict)

        return

    def do_POST(self):
        task_already_exists = False

        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                environ={'REQUEST_METHOD': 'POST',
                                         'CONTENT_TYPE': self.headers['Content-Type']})

        self.send_response(200)  # Return a response of 200, OK to the client
        self.end_headers()

        if upper(self.path) == "/NEW_TASK":
            # New task recieved, grab the relavent bits out of the POST
            task = form.getfirst("task", "")
            obsnum = str(form.getfirst("obsnum", ""))
            still = form.getfirst("still", "")
            args = form.getfirst("args", "").split(' ')
            drmaa_args = form.getfirst("drmaa_args", "")  # .split(' ')
            drmaa_queue = form.getfirst("drmaa_queue", "")
            # Will be coming in pickled, might want to do the same for args
            pickled_env_vars = form.getfirst("env_vars", "")
            # depickled env_vars, should now be a dict
            env_vars = pickle.loads(pickled_env_vars)

            logger.info('TaskHandler.handle: received (%s,%s) with args=%s' % (
                task, obsnum, ' '.join(args)))

        if task == 'COMPLETE':
            self.server.dbi.set_obs_status(obsnum, task)
        else:
            for active_task in self.server.active_tasks:
                logger.debug("  Active Task: %s, For Obs: %s" %
                             (active_task.task, active_task.obs))
                if active_task.task == task and active_task.obs == obsnum:
                    # We now check to see if the task is already in the list before we go crazy
                    #   and try to run a second copy
                    logger.debug("We are currently running this task already. Task: %s , Obs: %s"
                                 % (active_task.task, active_task.obs))
                    task_already_exists = True
                    break

            if task_already_exists is False:
                t = Task(task, obsnum, still, args, drmaa_args, drmaa_queue, self.server.dbi,
                         self.server, self.server.data_dir, self.server.path_to_do_scripts,
                         custom_env_vars=env_vars)
                self.server.append_task(t)
                t.run()
        return


class TaskServer(HTTPServer):
    allow_reuse_address = True

    def __init__(self, dbi, sg, data_dir='.', port=14204, handler=TaskHandler,
                 path_to_do_scripts=".", drmaa_shared='/shared', workflow=None):
        global logger
        logger = sg.logger
        self.myhostname = socket.gethostname()
        # Class us into HTTPServer so we can make calls from TaskHandler into
        # this class via self.server.
        self.httpd = HTTPServer.__init__(
            self, (self.myhostname, port), handler)
        self.active_tasks_semaphore = threading.Semaphore()
        self.active_tasks = []
        self.dbi = dbi
        self.sg = sg
        self.data_dir = data_dir
        self.keep_running = False
        self.watchdog_count = 0
        self.port = port
        self.path_to_do_scripts = path_to_do_scripts
        self.logger = sg.logger
        self.drmaa_session = ''
        self.drmaa_shared = drmaa_shared
        self.shutting_down = False
        self.wf = workflow

        # signal.signal(signal.SIGINT, self.signal_handler)  # Enabled clean
        # shutdown after Cntrl-C event.

    def append_task(self, t):
        # Jon : Not sure why we're doing this, we only have one primary thread
        self.active_tasks_semaphore.acquire()
        self.active_tasks.append(t)
        self.active_tasks_semaphore.release()

    def poll_task_status(self, task):
        # Do we need to interface with a cluster scheduler?
        if self.sg.cluster_scheduler == 1:
            try:
                task_info = self.drmaa_session.jobStatus(task.jid)
            except:
                task_info = "failed"
                logger.debug(
                    "TS: poll_task_status : DRMAA jobstatus failed for jid : %s" % task.jid)
            # Check if task is done or failed..
            if task_info == "done" or task_info == "failed":
                poll_status = True
            else:
                poll_status = None
            # attributes: retval. :  jobId, hasExited, hasSignal, terminatedSignal, hasCoreDump,
            #                        wasAborted, exitStatus, and resourceUsage
        else:
            try:
                # race condition due to threading, might fix later, pretty rare
                poll_status = task.process.poll()
            except:
                poll_status = None
                time.sleep(2)

        return poll_status

    def finalize_tasks(self, poll_interval=5.):
        self.user_input = InputThread()
        self.user_input.start()

        while self.keep_running:
            self.active_tasks_semaphore.acquire()
            new_active_tasks = []
            for mytask in self.active_tasks:
                if self.poll_task_status(mytask) is None:
                    # This should probably be handled in a better way
                    new_active_tasks.append(mytask)
                else:
                    mytask.finalize()
            self.active_tasks = new_active_tasks
            self.active_tasks_semaphore.release()

            # Jon: I think we can get rid of the watchdog as I'm already
            # throwing this at the db
            time.sleep(poll_interval)
            if self.watchdog_count == 30:
                logger.debug('TaskServer is alive')
                for mytask in self.active_tasks:
                    try:
                        child_proc = mytask.process.children()[0]
                        if psutil.pid_exists(child_proc.pid):
                            cpu = child_proc.cpu_percent(interval=1.0)
                            mem_pct = child_proc.memory_percent()
                            mem_mb = mem_pct / 100 * psutil.virtual_memory().total / 1048576 # == 2**20, to convert to MB
                            # save in task object
                            mytask.max_mem = max(mytask.max_mem, mem_mb)
                            mytask.avg_cpu_load += cpu / 100.
                            mytask.n_cpu_load_polls += 1
                            # echo out to screen
                            logger.debug('Proc info on {obsnum}:{task}:{pid} - cpu={cpu:.1f}%,'
                                         ' mem={mem:.1f}%, Naffinity={aff}'.format(
                                             obsnum=mytask.obs, task=mytask.task, pid=child_proc.pid,
                                             cpu=cpu, mem=mem_pct, aff=len(child_proc.cpu_affinity())))
                    except:
                        pass
                self.watchdog_count = 0
            else:
                self.watchdog_count += 1

            self.keyboard_input = self.user_input.get_user_input()
            if self.keyboard_input is not None:
                handle_keyboard_input(self, self.keyboard_input)
        return

    def kill(self, pid):
        try:
            for task in self.active_tasks:
                if self.sg.cluster_scheduler == 1:  # Do we need to interface with a cluster scheduler?

                    if int(task.jid) == int(pid):
                        task.kill()
                        break
                else:
                    if int(task.process.pid) == int(pid):
                        task.kill()
                        break
        except:
            logger.exception(
                "Problem killing off task: %s  w/  pid : %s" % (task, pid))

    def kill_all(self):
        for task in self.active_tasks:
            task.kill()
            break

    def checkin_timer(self):
        #
        # Just a timer that will update that its last_checkin time in the database every 5min
        #
        while self.keep_running is True:
            hostname = platform.node()
            ip_addr = self.get_ip_address()
            cpu_usage = os.getloadavg()[1]  # using the 5 min load avg
            ntasks = len(self.active_tasks)
            self.dbi.still_checkin(hostname, ip_addr, self.port, int(cpu_usage), self.data_dir,
                                   status="OK", max_tasks=self.sg.actions_per_still, cur_tasks=ntasks)

            time.sleep(10)
        return 0

    def mc_checkin_thread(self):
        import mc_utils

        while self.keep_running is True:
            hostname = platform.node()
            ip_addr = self.get_ip_address()
            cpu_usage = os.getloadavg()[1]  # using the 5 min load avg
            ntasks = len(self.active_tasks)

            # get general info
            ncpu = psutil.cpu_count()
            s = self.dbi.Session()
            still = s.query(Still).filter(Still.hostname == hostname).one()
            status = still.status
            s.close()

            # get memory usage
            vmem = psutil.virtual_memory()
            vmem_tot = vmem.total / 1024 / 1024 / 1024
            vmem_pct = vmem.percent

            # get disk usage
            du = psutil.disk_usage('/')
            du_tot = du.total / 1024 / 1024 / 1024
            du_pct = du.percent

            # get time since boot in hr
            now = time.time()
            boot_time = psutil.boot_time()
            dt_boot = now - boot_time
            dt_boot_days = dt_boot / 60 / 60 / 24

            # call functions for interacting with M&C
            mc_utils.add_mc_server_status(hostname, ip_addr, ncpu, cpu_usage, dt_boot_days,
                                          vmem_pct, vmem_tot, du_pct, du_tot)

            # sleep
            time.sleep(TIME_INT_FOR_NEW_MC_CHECK)

        return 0

    def start(self):
        psutil.cpu_percent()
        time.sleep(1)
        self.keep_running = True
        t = threading.Thread(target=self.finalize_tasks)
        t.daemon = True
        t.start()
        logger.info('Starting Task Server')
        logger.info("using code at: " + __file__)
        logger.info("Path to do_ Scripts : %s" % self.path_to_do_scripts)
        logger.info("Data_dir : %s" % self.data_dir)
        logger.info("Port : %s" % self.port)

        if self.sg.cluster_scheduler == 1:
            logger.info("Initilizing DRMAA interface to cluster scheduler")
            import drmaa
            # Start the interface session to DRMAA to control GridEngine
            self.drmaa_session = drmaa.Session()
            self.drmaa_session.initialize()
        try:
            # Setup a thread that just updates the last checkin time for this
            # still every 10s
            timer_thread = threading.Thread(target=self.checkin_timer)
            # Make it a daemon so that when ctrl-c happens this thread goes
            # away
            timer_thread.daemon = True
            timer_thread.start()  # Start heartbeat
            self.serve_forever()  # Start the lisetenser server

            if self.wf.log_to_mc:
                # Also set up an M&C status thread
                mc_thread = threading.Thread(target=self.mc_checkin_thread)
                # Make it a daemon so that when ctrl-c happens this thread
                # goes away
                mc_thread.daemon = True
                mc_thread.start()
        finally:
            self.shutdown()
        return

    def shutdown(self):
        if self.shutting_down is False:
            # check to see if we're already shutting down so we don't step
            #    over multiple threads attempting this
            self.shutting_down = True
            logger.debug("Shutting down task_server")
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)
            cpu_usage = psutil.cpu_percent()
            self.dbi.still_checkin(hostname, ip_addr, self.port, int(cpu_usage), self.data_dir,
                                   status="OFFLINE")
            self.keep_running = False
            parentproc = psutil.Process()
            myprocs = parentproc.children(recursive=True)
            for proc in myprocs:
                logger.debug("Killing nicely -> Pid: %s - Proc: %s" %
                             (proc.pid, proc.name))
                proc.terminate()
            gone, alive = psutil.wait_procs(myprocs, timeout=3)
            for proc in alive:
                logger.debug("Killing with gusto -> Pid: %s - Proc: %s" %
                             (proc.pid, proc.name))
                proc.kill()
            HTTPServer.shutdown(self)
            if self.sg.cluster_scheduler == 1:
                self.drmaa_session.exit()  # Terminate DRMAA sessionmaker

            sys.exit(0)

    def get_ip_address(self):
        """Return an IP address for this machine as a string.

        https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python

        This is actually not well defined -- machines have multiple interfaces,
        each with its own IP address. We use eth0 if it exists, otherwise the
        first one that isn't `lo`.

        Copied from hera_mc/scripts/mc_server_status_daemon.py
        """
        try:
            addrs = netifaces.ifaddresses('eth0')
        except ValueError:
            for ifname in sorted(netifaces.interfaces()):
                if ifname != 'lo':
                    addrs = netifaces.ifaddresses(ifname)
                    break
            else:  # triggered if we never did the 'break'
                return '?.?.?.?'

        return addrs[netifaces.AF_INET][0]['addr']
