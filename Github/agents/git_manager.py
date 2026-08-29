import sys
from pathlib import Path
from datetime import datetime
import subprocess


ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from tools.file_tools import write_file, list_files


from memory import (
    add_change
)





def run_git(command):

    try:

        result = subprocess.run(

            command,

            cwd=ROOT,

            capture_output=True,

            text=True

        )


        return {

            "stdout": result.stdout,

            "stderr": result.stderr,

            "code": result.returncode

        }


    except Exception as e:


        return {

            "error": str(e)

        }








def git_manager_agent(task):


    print("\nGIT MANAGER AGENT")



    files = list_files.invoke({})



    report=f"""
# Git Management Report


## Task

{task}


## Project Files

{files}



## Git Status

"""


    status = run_git(

        [
            "git",
            "status"
        ]

    )


    report += str(status)



    report += """



## Recommendations

- Create checkpoints before major changes.
- Use meaningful commit messages.
- Keep history clean.

"""



    write_file.invoke(

        {

            "path":

            "docs/git_report.md",


            "content":

            report

        }

    )



    add_change(

        "Git manager generated report"

    )



    return "Git management report created"









if __name__=="__main__":


    print(

        git_manager_agent(

            "Check repository"

        )

    )