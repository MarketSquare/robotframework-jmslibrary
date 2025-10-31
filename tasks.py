import pathlib
import subprocess
from invoke import task
from JMS import __version__ as VERSION
import inspect

if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

ROOT = pathlib.Path(__file__).parent.resolve().as_posix()

@task
def libdoc(context):
    source = f"{ROOT}/JMS/JMS.py"
    target = f"{ROOT}/docs/JMS.html"
    cmd = [
        "python",
        "-m",
        "robot.libdoc",
        "-n JMS",
        f"-v {VERSION}",
        source,
        target,
    ]
    subprocess.run(" ".join(cmd), shell=True)

@task
def atests(context):
    cmd = [
        "coverage",
        "run",
        "--source=JMS",
        "-p",
        "-m",
        "robot",
        "--loglevel=TRACE:DEBUG",
        "--listener RobotStackTracer",
        "--exclude appiumORnot_readyORnot_ci",
        "-d results",
        "--prerebotmodifier utilities.xom.XUnitOut:results/xunit.xml",
        f"{ROOT}/tests/atest"
    ]
    global atests_completed_process
    atests_completed_process = subprocess.run(" ".join(cmd), shell=True, check=False)

@task(atests)
def tests(context):
    subprocess.run("coverage combine", shell=True, check=False)
    subprocess.run("coverage report", shell=True, check=False)
    subprocess.run("coverage html -d results/htmlcov", shell=True, check=False)
    if atests_completed_process.returncode != 0:
        raise Exception("Tests failed")

@task
def coverage_report(context):
    subprocess.run("coverage combine", shell=True, check=False)
    subprocess.run("coverage report", shell=True, check=False)
    subprocess.run("coverage html -d results/htmlcov", shell=True, check=False)