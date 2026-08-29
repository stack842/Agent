import sys
from pathlib import Path
import json
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from tools.file_tools import (
    list_files,
    read_file,
    write_file
)


from memory import (
    add_issue,
    add_change
)



def debug_agent(task):


    print("\nDEBUG AGENT")


    files = list_files.invoke({})


    report = f"""
# Debug Report


## Task

{task}


## Current Files

{files}


## Analysis

Debug agent analyzed the project.

Further investigation required based on test failures.


## Recommendation

Run tests and review reported issues.

"""


    write_file.invoke(

        {
            "path":
            "docs/debug_report.md",

            "content":
            report
        }

    )


    add_issue(

        {
            "debug_task":
            task
        }

    )


    add_change(

        "Debug analysis completed"

    )


    return "Debug report created"