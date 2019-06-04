import subprocess, os

if __name__ == "__main__":
    main_pid = os.getpid()
    process_file = open('/var/workspace/run/tumbler.pid', 'w')
    process_file.write(str(main_pid))
    process_file.close()
    while True:
        command = 'python -u /var/workspace/spark/prediction.py'
        process = subprocess.Popen(command, shell=True)
        process.wait()