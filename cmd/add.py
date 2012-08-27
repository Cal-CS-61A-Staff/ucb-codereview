""" This script gets run whenever we get a new submission to upload.
    The login of the student is passed in as the first argument.
    The steps to follow (should be fleshed out more) to add a submission are as follows:
    1. Unpack the submission into a temp directory.
    2. Move the file that has the student's code into their git repository.
    3. Add and commit their code.
    4. Upload their code.
"""
import argparse
import sys
import tempfile
import shutil
import utils

HOME_DIR = '~cs61a/'
GRADING_DIR = HOME_DIR + "grading/"
SUBMISSION_DIR = GRADING_DIR + 'submissions/'

def get_subm(login, assign):
    """
    Gets the submission for the given login and assignment
    and moves the current directory to be in the temp directory they're stored in
    """
    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)
    try:
        utils.run("get-subm " + login + " " + assign)
    except OSError as e:
        print << sys.stderr, str(e)
    return tempdir + "/" #need the trailing slash for the copy command

def find_path(login, assign):
    """
    Finds the path to the given login's assignment git repository
    Not sure how we're structuring this right now...
    """
    return ""

def get_important_files(assign):
    """
    Returns the files we want to copy.
    Do we need this function, or should we copy everything?
    Would involve either some looking at the params file, or looking at the DB
    """
    return [""]

def get_gmails(login):
    """
    Returns the gmail account associated with this student for the code review system.
    Not sure how to do this yet; we'll decide something in the first staff meeting
    """
    return "example@gmail.com"

PYTHON_BIN = "python2.6"
UPLOAD_SCRIPT = "~cs61a/code_review/61a-codereview/appengine/upload.py"
SERVER_NAME = "berkeley-61a.appspot.com"
ROBOT_EMAIL = "cs61a.robot@gmail.com"

def get_robot_pass():
    return "robotototototot"

def upload(path_to_repo, gmails, logins, assign):
    """
    ~cs61a/code_review/repo/login/assign/
    Calls the upload script with the needed arguments given the path to the repo and the
    gmail account of the student.
    Arguments we care about:
    -e email of the person
    -r reviewers
    --cc people to cc
    --private makes the issue private 
    --send_mail sends an email to the reviewers (might want)
    --send_patch sends an email but with the diff attached, possible thing to do
    new version of the same issue
    each issue is the same project
    These args are documented in upload.py starting on line 490.
    This method also needs to deal with assigning the correct people to this, which means
    it has to probably get info from somewhere about the roster. 
    stuff we needed to enter
    first time uploading
    -s (server)
    -t name of assignment 
    -e email for login to uploading (robot)
    -r reviewers (student TA reader other)

    every other time:
    issue number
    revision
    server
    title: timestamp?
    """
    issue_num = model.get_issue_number(logins, assign)
    staff_gmails = model.get_staff_gmails(logins)
    content = ""
    if not issue_num:
        cmd = " ".join(PYTHON_BIN, UPLOAD_SCRIPT, '-s', SERVER_NAME,
            "-t", assign, '-r', *gmails, *staff_gmails, '-e', ROBOT_EMAIL)
        content = get_robot_pass()
    else:
          cmd = " ".join(PYTHON_BIN, UPLOAD_SCRIPT, '-s', SERVER_NAME,
            "-t", utils.get_timestamp_str(), '-e', ROBOT_EMAIL, '-i', issue_num,
            '--rev', git.get_revision_hash(path_to_repo))
    out = utils.run(cmd, content)
    # if not issue_num:
    line = ""
    for l in out:
        if l.startswith("Issue created:"):
            line = l
            break
    if line:
        line = line[line.rfind('/') + 1:].strip()
        issue_num = int(line)
        model.set_issue_number(logins, assign, issue_num)

def put_in_repo(login, assign):
    """
    Puts the login's assignment into their repo
    If this is their first submission for this assignment, this also 
    """
    original_path = os.getcwd()
    tempdir = get_subm(login, assign)
    path_to_repo = find_path(login, assign)
    files_to_copy = get_important_files(assign)
    for filename in files_to_copy:
        shutil.copy(tempdir + filename, path_to_repo + filename)
    os.chdir(original_path)
    shutil.rmtree(tempdir)
    return path_to_repo, is_new_repo

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adds the given login's latest \
     submission for the given assignment to the code review system.")
    parser.add_argument('login', type=str,
                        help='the login to add')
    parser.add_argument('assign', type=str,
                        help='the assignment to look at')
    args = parser.parse_args()
    path_to_repo = put_in_repo(args.login, args.assign)
    upload(path_to_repo, get_gmail(args.login))