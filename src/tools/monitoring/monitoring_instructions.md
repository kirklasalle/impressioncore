# Terminal Session Monitoring Guide

This guide provides detailed instructions on how to use the `monitor_session.sh` script and compares it with other standard terminal logging utilities.

## `monitor_session.sh` Script Usage

### 1. Make the Script Executable

First, you need to make the script executable:

```bash
chmod +x monitor_session.sh
```

### 2. How to Identify the Target TTY

To monitor a terminal session, you need to know its TTY (teletype) device name.

* **For your current terminal:** Simply run the `tty` command.

    ```bash
    tty
    ```

    Output might be something like `/dev/pts/0`.

* **For another user's terminal or a different session:** You can use the `who` or `w` command to list all logged-in users and their TTYs.

    ```bash
    who
    ```

    The output will show the username, TTY, and login time.

### 3. Start Monitoring

To start monitoring, run the script with the `start` command.

* **Monitor the current terminal:**

    ```bash
    ./monitor_session.sh start
    ```

* **Monitor a specific TTY:**

    ```bash
    ./monitor_session.sh start /dev/pts/1
    ```

The script will create a log file in `~/tty_logs` with a timestamp and the TTY name.

### 4. Verify the Monitoring Process

You can check if the monitoring process is running with the `status` command:

```bash
./monitor_session.sh status
```

### 5. Stop Monitoring

To stop the monitoring process cleanly, use the `stop` command:

```bash
./monitor_session.sh stop
```

This will kill the `strace` process and remove the PID file.

### 6. View the Log File

The logs are stored in `~/tty_logs`. You can view the latest log file using the `view` command:

```bash
./monitor_session.sh view
```

This will open the log file in `less`. The log file contains raw output from `strace`, including timing information for every read and write system call.

## Comparison with Standard Utilities

Here’s a comparison of the custom script with standard Linux utilities for terminal logging.

### `script`

The `script` command is a standard utility that records an entire terminal session.

* **Pros:**
  * Easy to use: `script -t 2> timing.log -a output.session`
  * Captures everything, including control characters.
  * Can be replayed with `scriptreplay`.
* **Cons:**
  * Not non-intrusive: It starts a new shell, so you can't attach to an existing session.
  * Log files can be hard to read directly due to control characters.

### `ttyrec`

`ttyrec` is a TTY recorder that is similar to `script` but with a more standardized format.

* **Pros:**
  * Creates clean, replayable recordings.
  * `ttyplay` is a dedicated player for its recordings.
* **Cons:**
  * Like `script`, it's not non-intrusive and requires starting a new session.
  * May not be installed by default on all systems.

### `tmux` Logging

`tmux` is a terminal multiplexer that has built-in logging capabilities.

* **Pros:**
  * Can capture the entire history of a pane.
  * Can be enabled or disabled on the fly within a `tmux` session.
* **Cons:**
  * Only works if the user is already in a `tmux` session.
  * Not designed for security auditing, as a user can easily disable it.

### Custom `monitor_session.sh` Script

* **Pros:**
  * **Non-intrusive:** Can attach to any existing TTY session without interrupting the user.
  * **Covert:** Runs as a background process, making it less obvious to the user being monitored.
  * **Detailed Logs:** The `strace` output provides very detailed information, including timestamps for every I/O operation.
  * **Graceful Control:** The `start`, `stop`, and `status` commands make it easy to manage.
* **Cons:**
  * **Complex Logs:** The `strace` output can be verbose and difficult to parse for simple session playback.
  * **Root/Sudo Privileges:** `strace` typically requires elevated privileges to attach to processes owned by other users.
  * **Potential Performance Overhead:** `strace` can introduce a small amount of performance overhead on the monitored process.

### Use Case Recommendations

* **Security Auditing:** The custom `monitor_session.sh` script is the best choice due to its non-intrusive nature and detailed, timestamped logs.
* **Debugging:** `strace` (as used in the script) is a powerful debugging tool. For general session debugging, `script` or `ttyrec` might be simpler.
* **Session Playback:** `script` and `ttyrec` are superior for replaying a session exactly as it happened. The custom script's logs are more for analysis than for playback.
